import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
from typing import Optional
from tqdm import tqdm
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
import joblib
import re
from pathlib import Path

os.environ["COVERAGE_FILE"] = str(Path(".coverage").resolve())

# feature selection
from sklearn.feature_selection import (
    f_classif,
    f_regression,
    mutual_info_classif,
    mutual_info_regression,
    chi2,
    SelectPercentile,
    SelectFpr,
    RFE,
    SelectFromModel,
)
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import root_mean_squared_error, log_loss, make_scorer
from mlxtend.feature_selection import SequentialFeatureSelector
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.stats import spearmanr, kendalltau

# Internal
from lecrapaud.directories import tmp_dir, clean_directory
from lecrapaud.utils import logger
from lecrapaud.config import PYTHON_ENV
from lecrapaud.db import (
    Experiment,
    Target,
    Feature,
    FeatureSelection,
    FeatureSelectionRank,
)
from lecrapaud.search_space import all_models

# Annoying Warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def load_train_data(experiment_dir):
    data_dir = f"{experiment_dir}/data"

    logger.info("Loading data...")
    train = joblib.load(f"{data_dir}/train.pkl")
    val = joblib.load(f"{data_dir}/val.pkl")
    test = joblib.load(f"{data_dir}/test.pkl")
    try:
        train_scaled = joblib.load(f"{data_dir}/train_scaled.pkl")
        val_scaled = joblib.load(f"{data_dir}/val_scaled.pkl")
        test_scaled = joblib.load(f"{data_dir}/test_scaled.pkl")
    except FileNotFoundError:
        train_scaled = None
        val_scaled = None
        test_scaled = None

    return train, val, test, train_scaled, val_scaled, test_scaled


class FeatureSelectionEngine:
    def __init__(self, train, experiment, target_number, target_clf, **kwargs):
        self.experiment = experiment
        self.train = train
        self.target_number = target_number
        self.target_clf = target_clf

        self.target_type = (
            "classification" if self.target_number in self.target_clf else "regression"
        )
        self.percentile = self.experiment.percentile
        self.corr_threshold = self.experiment.corr_threshold
        self.max_features = self.experiment.max_features

        self.experiment_dir = self.experiment.path
        self.experiment_id = self.experiment.id
        self.data_dir = f"{self.experiment_dir}/data"
        self.target_dir = f"{self.experiment_dir}/TARGET_{self.target_number}"
        self.feature_selection_dir = f"{self.target_dir}/feature_selection"
        os.makedirs(self.feature_selection_dir, exist_ok=True)

    # Main feature selection function
    def run(
        self,
        single_process: bool = True,
    ):
        """Function to do feature selection with a range of different feature selection technics

        Args:
            - train (pd.DataFrame): a pandas train set
            - target_number (in): a target, targets need to be name ``TARGET_{n}```
            - single_process (bool): if True, run all feature selection methods in a single process. If False, run them in parallel.
        """
        target_number = self.target_number
        target_type = self.target_type

        # Create the feature selection in db
        target = Target.find_by(name=f"TARGET_{target_number}")
        percentile = self.percentile
        corr_threshold = self.corr_threshold
        max_features = self.max_features

        feature_selection = FeatureSelection.upsert(
            match_fields=["target_id", "experiment_id"],
            target_id=target.id,
            experiment_id=self.experiment_id,
        )
        feature_map = {f.name: f.id for f in Feature.get_all(limit=20000)}

        if feature_selection.best_features_path and os.path.exists(
            feature_selection.best_features_path
        ):
            return joblib.load(feature_selection.best_features_path)

        self.X = self.train.loc[:, ~self.train.columns.str.contains("^TARGET_")]
        self.y = self.train[f"TARGET_{target_number}"]

        logger.info(f"Starting feature selection for TARGET_{target_number}...")
        clean_directory(self.feature_selection_dir)

        # Let's start by removing very low variance feature and extremly correlated features
        # This is needed to reduce nb of feature but also for methods such as anova or chi2 that requires independent, non constant, non full 0 features
        self.X = self.remove_low_variance_columns()
        features_uncorrelated, features_correlated = self.remove_correlated_features(
            90, vizualize=False
        )
        self.X = self.X[features_uncorrelated]

        logger.debug(
            f"""
            \nWe first have removed {len(features_correlated)} features with correlation greater than 90%
            \nWe are looking to capture {percentile}% of {len(self.X.columns)} features, i.e. {int(len(self.X.columns)*percentile/100)} features, with different feature selection methods
            \nWe will then remove above {corr_threshold}% correlated features, keeping the one with the best ranks
            \nFinally, we will keep only the {max_features} best ranked features
            """
        )

        start = time.time()

        # handling categorical features (only if classification)
        self.X_categorical, self.X_numerical = get_features_by_types(self.X)

        if target_type == "classification" and self.X_categorical.shape[1] > 0:
            feat_scores = self.select_categorical_features(percentile=percentile)
            rows = []
            for row in feat_scores.itertuples(index=False):
                feature_id = feature_map.get(row.features)

                rows.append(
                    {
                        "feature_selection_id": feature_selection.id,
                        "feature_id": feature_id,
                        "method": row.method,
                        "score": row.score,
                        "pvalue": row.pvalue,
                        "support": row.support,
                        "rank": row.rank,
                        "training_time": row.training_time,
                    }
                )

            if len(rows) == 0:
                logger.warning(
                    f"No categorical features selected for TARGET_{target_number}"
                )

            FeatureSelectionRank.bulk_upsert(rows=rows)

            categorical_features_selected = feat_scores[feat_scores["support"]][
                "features"
            ].values.tolist()

        results = []
        params = {"percentile": percentile}
        if single_process:
            results = [
                self.select_feature_by_linear_correlation(**params),
                self.select_feature_by_nonlinear_correlation(**params),
                self.select_feature_by_mi(**params),
                self.select_feature_by_feat_imp(**params),
                self.select_feature_by_rfe(**params),
                # self.select_feature_by_sfs(
                #     **params
                # ), # TODO: this is taking too long
            ]
        else:
            # Use ProcessPoolExecutor to run tasks in parallel
            # TODO: not sure it's efficient from previous tests... especially because rfe and sfs methods are doing parallel processing already, this can create overhead
            with ProcessPoolExecutor() as executor:
                # Submit different functions to be executed in parallel
                futures = [
                    executor.submit(
                        self.select_feature_by_linear_correlation,
                        **params,
                    ),
                    executor.submit(
                        self.select_feature_by_nonlinear_correlation,
                        **params,
                    ),
                    executor.submit(
                        self.select_feature_by_mi,
                        **params,
                    ),
                    executor.submit(
                        self.select_feature_by_feat_imp,
                        **params,
                    ),
                    executor.submit(
                        self.select_feature_by_rfe,
                        **params,
                    ),
                    # executor.submit(
                    #     self.select_feature_by_sfs,
                    #     **params,
                    # ),  # TODO: this is taking too long
                ]

                # Wait for all futures to complete and gather the results
                with tqdm(total=len(futures)) as pbar:
                    for future in as_completed(futures):
                        results.append(future.result())
                        pbar.update(1)

        logger.info(f"Finished feature selection for target {target_number}")

        stop = time.time()

        # Once all tasks are completed, start by inserting results to db
        feat_scores = pd.concat(
            results,
            axis=0,
        )

        logger.info("Inserting feature selection results to db...")
        rows = []
        for row in feat_scores.itertuples(index=False):
            feature_id = feature_map.get(row.features)

            rows.append(
                {
                    "feature_selection_id": feature_selection.id,
                    "feature_id": feature_id,
                    "method": row.method,
                    "score": row.score,
                    "pvalue": None if pd.isna(row.pvalue) else row.pvalue,
                    "support": row.support,
                    "rank": row.rank,
                    "training_time": row.training_time,
                }
            )

        if len(rows) == 0:
            logger.warning(f"No numerical features selected for TARGET_{target_number}")

        FeatureSelectionRank.bulk_upsert(rows=rows)

        # Merge the results
        logger.info("Merging feature selection methods...")
        features_selected = feat_scores[feat_scores["support"]][["features", "rank"]]
        features_selected.sort_values("rank", inplace=True)
        features_selected.drop_duplicates("features", inplace=True)

        features_selected_list = features_selected["features"].values.tolist()

        # analysis 1
        features_selected_by_every_methods = set(results[0]["features"].values.tolist())
        for df in results[1:]:
            features_selected_by_every_methods &= set(
                df["features"].values.tolist()
            )  # intersection
        features_selected_by_every_methods = list(features_selected_by_every_methods)
        logger.debug(
            f"We selected {len(features_selected_list)} features and {len(features_selected_by_every_methods)} were selected unanimously:"
        )
        logger.debug(features_selected_by_every_methods)
        pd.Series(features_selected_list).to_csv(
            f"{self.feature_selection_dir}/features_before_corr.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        # removing correlated features
        self.X = self.X[features_selected_list]
        features, features_correlated = self.remove_correlated_features(corr_threshold)
        pd.Series(features).to_csv(
            f"{self.feature_selection_dir}/features_before_max.csv",
            index=True,
            header=True,
            index_label="ID",
        )
        features = features[:max_features]

        # adding categorical features selected
        features += (
            categorical_features_selected if target_type == "classification" else []
        )
        logger.debug(
            f"Final pre-selection: {len(features)} features below {corr_threshold}% out of {len(features_selected_list)} features, and rejected {len(features_correlated)} features, {100*len(features)/len(features_selected_list):.2f}% features selected"
        )

        pd.Series(features).to_csv(
            f"{self.feature_selection_dir}/features.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        # analysis 2
        features_selected_by_every_methods_uncorrelated = list(
            set(features) & set(features_selected_by_every_methods)
        )
        logger.debug(
            f"In this pre-selection, there is {len(features_selected_by_every_methods_uncorrelated)} features from the {len(features_selected_by_every_methods)} selected unanimously\n"
        )
        logger.debug(
            features_selected[
                features_selected["features"].isin(features)
            ].to_markdown()
        )

        # save to path
        best_features_path = Path(f"{self.target_dir}/features.pkl").resolve()
        joblib.dump(features, best_features_path)

        # save in db
        db_features = Feature.filter(name__in=features)
        # Order matters, to keep the same order in db as in features, we need: map features by name
        feature_by_name = {f.name: f for f in db_features}
        # Reorder them according to original `features` list
        ordered_db_features = [
            feature_by_name[name] for name in features if name in feature_by_name
        ]

        feature_selection = FeatureSelection.get(feature_selection.id)
        feature_selection = feature_selection.add_features(ordered_db_features)
        feature_selection.training_time = stop - start
        feature_selection.best_features_path = best_features_path
        feature_selection.save()

        return features

    # Remove correlation
    # ------------------

    def remove_low_variance_columns(self, threshold: float = 1e-10) -> pd.DataFrame:
        """
        Removes columns with very low variance (including constant columns).

        Parameters:
            threshold (float): Minimum variance required to keep a column.
                            Default is 1e-10 to eliminate near-constant features.

        Returns:
            pd.DataFrame: Cleaned DataFrame without low-variance columns.
        """
        X = self.X

        low_var_cols = [
            col
            for col in X.columns
            if pd.api.types.is_numeric_dtype(X[col])
            and np.nanvar(X[col].values) < threshold
        ]

        if low_var_cols:
            logger.info(f"🧹 Removed {len(low_var_cols)} low-variance columns:")
            logger.info(low_var_cols)

        return X.drop(columns=low_var_cols, errors="ignore")

    def remove_correlated_features(self, corr_threshold: int, vizualize: bool = False):
        X = self.X
        features = X.columns
        # Create correlation matrix, select upper triangle & remove features with correlation greater than threshold
        corr_matrix = X[features].corr().abs()

        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        features_uncorrelated = [
            column
            for column in upper.columns
            if all(upper[column].dropna() <= corr_threshold / 100)
        ]
        features_correlated = [
            column
            for column in upper.columns
            if any(upper[column] > corr_threshold / 100)
        ]

        if vizualize:
            features_selected_visualization = (
                X[features]
                .corr()
                .where(np.triu(np.ones(len(features)), k=1).astype(bool))
                .fillna(0)
            )
            # Plot the heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                corr_matrix,
                annot=True,
                cmap="coolwarm",
                center=0,
                linewidths=1,
                linecolor="black",
            )
            plt.title(f"Correlation Matrix")
            plt.show()

            logger.info(f"\n{features_selected_visualization.describe().to_string()}")
            logger.info(f"\n{features_selected_visualization.to_string()}")
        return features_uncorrelated, features_correlated

    # Filter methods
    # ----------------

    def select_categorical_features(self, percentile):
        X, y = self.X_categorical, self.y

        start = time.time()
        logger.debug("Running Chi2 for categorical features...")
        feat_selector = SelectPercentile(chi2, percentile=percentile).fit(X, y)
        feat_scores = pd.DataFrame()
        feat_scores["score"] = feat_selector.scores_
        feat_scores["pvalue"] = feat_selector.pvalues_
        feat_scores["support"] = feat_selector.get_support()
        feat_scores["features"] = X.columns
        feat_scores["rank"] = feat_scores["score"].rank(method="first", ascending=False)
        feat_scores["method"] = "Chi2"
        feat_scores.sort_values("rank", ascending=True, inplace=True)
        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"Chi2 evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/Chi2.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores

    # Linear correlation (Person's R for regression and ANOVA for classification)
    def select_feature_by_linear_correlation(self, percentile: int = 20):
        X, y, target_type = self.X_numerical, self.y, self.target_type

        start = time.time()
        test_type = "Person's R" if target_type == "regression" else "ANOVA"
        logger.debug(f"Running {test_type}...")

        model = f_regression if target_type == "regression" else f_classif
        feat_selector = SelectPercentile(model, percentile=percentile).fit(X, y)
        feat_scores = pd.DataFrame()
        feat_scores["score"] = feat_selector.scores_
        feat_scores["pvalue"] = feat_selector.pvalues_
        feat_scores["support"] = feat_selector.get_support()
        feat_scores["features"] = X.columns
        feat_scores["rank"] = feat_scores["score"].rank(method="first", ascending=False)
        feat_scores["method"] = test_type
        feat_scores.sort_values("rank", ascending=True, inplace=True)
        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"{test_type} evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/{test_type}.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores

    # Non-Linear correlation (Spearsman's R for regression and Kendall's Tau for classification)
    def select_feature_by_nonlinear_correlation(self, percentile: int = 20):
        X, y, target_type = self.X_numerical, self.y, self.target_type

        start = time.time()

        def model(X_model, y_model):
            X_model = pd.DataFrame(X_model)
            y_model = pd.Series(y_model)

            method = "spearman" if target_type == "regression" else "kendall"

            corr_scores = []
            p_values = []

            for col in X_model.columns:
                if method == "spearman":
                    corr, pval = spearmanr(X_model[col], y_model)
                else:  # Kendall's Tau for classification
                    corr, pval = kendalltau(X_model[col], y_model)

                corr_scores.append(abs(corr))  # Keeping absolute correlation
                p_values.append(pval)

            return np.array(corr_scores), np.array(p_values)

        test_type = "Spearman's R" if target_type == "regression" else "Kendall's Tau"
        logger.debug(f"Running {test_type}...")

        feat_selector = SelectPercentile(model, percentile=percentile).fit(X, y)
        feat_scores = pd.DataFrame()
        feat_scores["score"] = feat_selector.scores_
        feat_scores["pvalue"] = feat_selector.pvalues_
        feat_scores["support"] = feat_selector.get_support()
        feat_scores["features"] = X.columns
        feat_scores["rank"] = feat_scores["score"].rank(method="first", ascending=False)
        feat_scores["method"] = test_type
        feat_scores.sort_values("rank", ascending=True, inplace=True)
        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"{test_type} evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/{test_type}.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores

    # Mutual Information
    def select_feature_by_mi(self, percentile: int = 20):
        X, y, target_type = self.X_numerical, self.y, self.target_type

        start = time.time()
        logger.debug("Running Mutual Information...")
        model = (
            mutual_info_regression
            if target_type == "regression"
            else mutual_info_classif
        )
        feat_selector = SelectPercentile(model, percentile=percentile).fit(X, y)
        feat_scores = pd.DataFrame()
        feat_scores["score"] = feat_selector.scores_
        feat_scores["support"] = feat_selector.get_support()
        feat_scores["features"] = X.columns
        feat_scores["rank"] = feat_scores["score"].rank(method="first", ascending=False)
        feat_scores["method"] = "Mutual Information"
        feat_scores.sort_values("rank", ascending=True, inplace=True)
        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"MI evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/MI.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores

    # Intrisic/embeedded method
    # ----------------

    # feature importance
    def select_feature_by_feat_imp(self, percentile: int = 20):
        X, y, target_type = self.X_numerical, self.y, self.target_type

        start = time.time()
        logger.debug("Running Feature importance...")

        params = {
            "n_estimators": 500,
            "max_depth": 2**3,
            "random_state": 42,
            "n_jobs": -1,
        }

        estimator = (
            RandomForestClassifier(**params)
            if target_type == "classification"
            else RandomForestRegressor(**params)
        )

        feat_selector = SelectFromModel(
            estimator=estimator,
            threshold=-np.inf,
            max_features=int(percentile * X.shape[1] / 100),
        ).fit(X, y)

        feat_scores = pd.DataFrame()
        feat_scores["score"] = feat_selector.estimator_.feature_importances_
        feat_scores["support"] = feat_selector.get_support()
        feat_scores["features"] = X.columns
        feat_scores["rank"] = feat_scores["score"].rank(method="first", ascending=False)
        feat_scores["method"] = "FI"
        feat_scores.sort_values("rank", ascending=True, inplace=True)

        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"Feat importance evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/FI.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores

    # Wrapper method
    # ----------------

    # recursive feature elimination
    def select_feature_by_rfe(self, percentile: int = 20):
        X, y, target_type = self.X_numerical, self.y, self.target_type

        start = time.time()
        logger.debug("Running Recursive Feature Elimination...")

        params = {
            "max_depth": 2**3,
            "random_state": 42,
        }
        estimator = (
            DecisionTreeClassifier(**params)
            if target_type == "classification"
            else DecisionTreeRegressor(**params)
        )
        rfe = RFE(estimator, n_features_to_select=percentile / 100, step=4, verbose=0)
        feat_selector = rfe.fit(X, y)

        feat_scores = pd.DataFrame(
            {
                "score": 0.0,  # Default feature importance
                "support": feat_selector.get_support(),
                "features": X.columns,
                "rank": 0,
                "method": "RFE",
            }
        )
        feat_scores.loc[
            feat_scores["features"].isin(feat_selector.get_feature_names_out()), "score"
        ] = list(feat_selector.estimator_.feature_importances_)
        feat_scores["rank"] = feat_scores["score"].rank(method="first", ascending=False)
        feat_scores.sort_values("rank", ascending=True, inplace=True)

        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"RFE evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/RFE.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores

    # SequentialFeatureSelector (loss based, possibility to do forwards or backwards selection or removal)
    def select_feature_by_sfs(self, percentile: int = 20):
        X, y, target_type = self.X_numerical, self.y, self.target_type

        start = time.time()
        logger.debug("Running Sequential Feature Selection...")
        warnings.filterwarnings("ignore", category=FutureWarning)

        params = {
            "max_depth": 2**3,
            "random_state": 42,
        }
        estimator = (
            DecisionTreeClassifier(**params)
            if target_type == "classification"
            else DecisionTreeRegressor(**params)
        )

        n_splits = 3
        n_samples = len(X)
        test_size = int(n_samples / (n_splits + 4))
        tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)

        score_function = (
            make_scorer(
                log_loss, response_method="predict_proba"
            )  # logloss needs probabilities
            if target_type == "classification"
            else make_scorer(root_mean_squared_error)
        )  # we avoid greater_is_better = False because it make the score negative and mess up ranking

        sfs = SequentialFeatureSelector(
            estimator,
            k_features=int(percentile * X.shape[1] / 100),
            forward=True,
            floating=True,  # Enables dynamic feature elimination
            scoring=score_function,
            cv=tscv,
            n_jobs=-1,
            verbose=0,
        )

        feat_selector = sfs.fit(X, y)

        # Extract selected features and their scores
        selected_features = set(feat_selector.k_feature_names_)
        feat_subsets = feat_selector.subsets_

        # Create DataFrame for feature scores
        feat_scores = pd.DataFrame(
            {
                "features": X.columns,
                "support": X.columns.isin(
                    selected_features
                ),  # TODO: comprendre pourquoi le support n'est pas correct (les bons scores ne sont pas toujours choisis)
                "score": 1000,
                "rank": None,
                "method": "SFS",
            }
        )

        # Sort subsets by score (lower is better)
        sorted_subsets = sorted(
            feat_subsets.items(), key=lambda item: item[1]["avg_score"]
        )

        # Record score per feature (first appearance)
        feature_score_map = {}
        for step in sorted_subsets:
            step = step[1]
            for feature in step["feature_names"]:
                if feature not in feature_score_map:
                    feature_score_map[feature] = step["avg_score"]

        # Assign scores
        for feature, score in feature_score_map.items():
            feat_scores.loc[feat_scores["features"] == feature, "score"] = score

        # rank by score (lower = better)
        feat_scores["rank"] = (
            feat_scores["score"].rank(method="first", ascending=True).astype(int)
        )

        feat_scores.sort_values("rank", ascending=True, inplace=True)

        stop = time.time()
        training_time = timedelta(seconds=(stop - start)).total_seconds()
        feat_scores["training_time"] = training_time

        logger.debug(
            f"SFS evaluation selected {feat_scores['support'].sum()} features in {training_time:.2f} seconds"
        )

        feat_scores.to_csv(
            f"{self.feature_selection_dir}/SFS.csv",
            index=True,
            header=True,
            index_label="ID",
        )

        return feat_scores


class PreprocessModel:

    def __init__(
        self,
        train,
        val,
        test,
        experiment,
        target_numbers,
        target_clf,
        models_idx,
        time_series,
        max_timesteps,
        group_column,
        date_column,
        **kwargs,
    ):
        self.train = train
        self.val = val
        self.test = test
        self.experiment = experiment
        self.target_numbers = target_numbers
        self.target_clf = target_clf
        self.models_idx = models_idx
        self.time_series = time_series
        self.max_timesteps = max_timesteps
        self.group_column = group_column
        self.date_column = date_column

        self.experiment_dir = experiment.path
        self.data_dir = f"{self.experiment_dir}/data"
        self.preprocessing_dir = f"{self.experiment_dir}/preprocessing"

        self.all_features = experiment.get_all_features(
            date_column=date_column, group_column=group_column
        )

    def run(self):
        # save data
        columns_to_keep = self.all_features + [
            f"TARGET_{i}" for i in self.target_numbers
        ]
        duplicates = [
            col for col in set(columns_to_keep) if columns_to_keep.count(col) > 1
        ]
        if duplicates:
            raise ValueError(f"Doublons détectés dans columns_to_keep: {duplicates}")
        self.train = self.train[columns_to_keep]
        self.val = self.val[columns_to_keep]
        self.test = self.test[columns_to_keep]
        joblib.dump(self.train, f"{self.data_dir}/train.pkl")
        joblib.dump(self.val, f"{self.data_dir}/val.pkl")
        joblib.dump(self.test, f"{self.data_dir}/test.pkl")

        # scaling features
        if any(t not in self.target_clf for t in self.target_numbers) and any(
            all_models[i].get("need_scaling") for i in self.models_idx
        ):
            logger.info("Scaling features...")
            train_scaled, scaler_x, scalers_y = self.scale_data(self.train)
            val_scaled, _, _ = self.scale_data(
                self.val,
                scaler_x=scaler_x,
                scalers_y=scalers_y,
            )
            test_scaled, _, _ = self.scale_data(
                self.test,
                scaler_x=scaler_x,
                scalers_y=scalers_y,
            )
        else:
            train_scaled = None
            val_scaled = None
            test_scaled = None
            scaler_x = None

        # save data
        joblib.dump(train_scaled, f"{self.data_dir}/train_scaled.pkl")
        joblib.dump(val_scaled, f"{self.data_dir}/val_scaled.pkl")
        joblib.dump(test_scaled, f"{self.data_dir}/test_scaled.pkl")
        joblib.dump(scaler_x, f"{self.preprocessing_dir}/scaler_x.pkl")

        data = {
            "train": self.train,
            "val": self.val,
            "test": self.test,
            "train_scaled": train_scaled,
            "val_scaled": val_scaled,
            "test_scaled": test_scaled,
        }

        # reshape data for time series
        reshaped_data = None
        if (
            any(all_models[i].get("recurrent") for i in self.models_idx)
            and self.time_series
        ):
            # reshaping data for recurrent models
            logger.info("Reshaping data for recurrent models...")
            reshaped_data = self.reshape_time_series(
                train_scaled,
                val_scaled,
                test_scaled,
                features=self.all_features,
                timesteps=self.max_timesteps,
            )

        return data, reshaped_data

    def inference(self):
        # self.train is new data here
        columns_to_keep = self.all_features
        self.train = self.train[columns_to_keep]

        scaler_x = joblib.load(f"{self.preprocessing_dir}/scaler_x.pkl")

        if scaler_x:
            scaled_data = scaler_x.transform(self.train)
            scaled_data = pd.DataFrame(
                scaled_data, columns=self.train.columns, index=self.train.index
            )
        else:
            scaled_data = self.train

        reshaped_data = None
        if (
            any(all_models[i].get("recurrent") for i in self.models_idx)
            and self.time_series
        ):
            # we need to make sur we have max_timesteps of data after grouping by group_column
            if (
                self.group_column
                and scaled_data.groupby(self.group_column).size().min()
                < self.max_timesteps
            ) or scaled_data.shape[0] < self.max_timesteps:
                raise ValueError(
                    f"Not enough data for group_column {self.group_column} to reshape data for recurrent models"
                )

            # reshaping data for recurrent models
            logger.info("Reshaping data for recurrent models...")
            reshaped_data = self.reshape_time_series(
                scaled_data,
                features=self.all_features,
                timesteps=self.max_timesteps,
            )

        return self.train, scaled_data, reshaped_data

    # scaling
    def scale_data(
        self,
        df: pd.DataFrame,
        scaler_x=None,
        scalers_y: Optional[list] = None,
    ):
        logger.info("Scale data...")
        X = df.loc[:, ~df.columns.str.contains("^TARGET_")]

        if scaler_x:
            X_scaled = pd.DataFrame(
                scaler_x.transform(X), columns=list(X.columns), index=X.index
            )
        else:
            scaler_x = StandardScaler()  # MinMaxScaler(feature_range=(-1,1))
            X_scaled = pd.DataFrame(
                scaler_x.fit_transform(X), columns=list(X.columns), index=X.index
            )

        # Determine which targets need to be scaled
        targets_numbers_to_scale = [
            i for i in self.target_numbers if i not in self.target_clf
        ]

        # Dictionary to store scaled target data
        scaled_targets = {}

        if scalers_y:
            for target_number in targets_numbers_to_scale:
                y = df[[f"TARGET_{target_number}"]]
                scaled_targets[target_number] = pd.DataFrame(
                    scalers_y[f"scaler_y_{target_number}"].transform(y.values),
                    columns=y.columns,
                    index=y.index,
                )
        else:
            scalers_y = {}
            for target_number in targets_numbers_to_scale:
                scaler_y = StandardScaler()
                y = df[[f"TARGET_{target_number}"]]

                scaled_y = pd.DataFrame(
                    scaler_y.fit_transform(y.values),
                    columns=y.columns,
                    index=y.index,
                )
                target_dir = f"{self.experiment_dir}/TARGET_{target_number}"
                joblib.dump(scaler_y, f"{target_dir}/scaler_y.pkl")

                scalers_y[f"scaler_y_{target_number}"] = scaler_y
                scaled_targets[target_number] = scaled_y

        # Reconstruct y_scaled in the original order
        y_scaled = pd.concat(
            [
                scaled_targets[target_number]
                for target_number in targets_numbers_to_scale
            ],
            axis=1,
        )
        y_not_scaled = df[
            df.columns.intersection([f"TARGET_{i}" for i in self.target_clf])
        ]

        # Ensure the final DataFrame keeps the original order
        df_scaled = pd.concat(
            [X_scaled, y_scaled, y_not_scaled],
            axis=1,
        )[
            df.columns
        ]  # Reorder columns to match original `df`

        if not df_scaled.columns.equals(df.columns):
            raise Exception("Columns are not in the same order after scaling.")

        return df_scaled, scaler_x, scalers_y

    # Reshape into 3D tensors for recurrent models
    def reshape_time_series(
        self,
        train: pd.DataFrame,
        val: pd.DataFrame,
        test: pd.DataFrame,
        features: list,
        timesteps: int = 120,
    ):
        # always scale for recurrent layers : train should be scaled
        group_column = self.group_column

        target_columns = train.columns.intersection(
            [f"TARGET_{i}" for i in self.target_numbers]
        )

        data = pd.concat([train, val, test], axis=0)

        def reshape_df(df: pd.DataFrame, group_series: pd.Series, timesteps: int):
            fill_value = [[[0] * len(df.columns)]]

            def shiftsum(x, timesteps: int):
                tmp = x.copy()
                for i in range(1, timesteps):
                    tmp = x.shift(i, fill_value=fill_value) + tmp
                return tmp

            logger.info("Grouping each feature in a unique column with list...")
            df_reshaped = df.apply(list, axis=1).apply(lambda x: [list(x)])
            df_reshaped = pd.concat([df_reshaped, group_series], axis=1)

            logger.info("Grouping features and creating timesteps...")
            df_reshaped = (
                df_reshaped.groupby(group_column)[0]
                .apply(lambda x: shiftsum(x, timesteps))
                .reset_index(group_column, drop=True)
                .rename("RECURRENT_FEATURES")
            )
            df_reshaped = pd.DataFrame(df_reshaped)

            return df_reshaped

        data_reshaped = reshape_df(data[features], data[group_column], timesteps)

        data_reshaped[target_columns] = data[target_columns]

        logger.info("Separating train, val, test data and creating np arrays...")
        train_reshaped = data_reshaped.loc[train.index]
        val_reshaped = data_reshaped.loc[val.index]
        test_reshaped = data_reshaped.loc[test.index]

        x_train_reshaped = np.array(
            train_reshaped["RECURRENT_FEATURES"].values.tolist()
        )
        y_train_reshaped = np.array(train_reshaped[target_columns].reset_index())
        x_val_reshaped = np.array(val_reshaped["RECURRENT_FEATURES"].values.tolist())
        y_val_reshaped = np.array(val_reshaped[target_columns].reset_index())
        x_test_reshaped = np.array(test_reshaped["RECURRENT_FEATURES"].values.tolist())
        y_test_reshaped = np.array(test_reshaped[target_columns].reset_index())

        reshaped_data = {
            "x_train_reshaped": x_train_reshaped,
            "y_train_reshaped": y_train_reshaped,
            "x_val_reshaped": x_val_reshaped,
            "y_val_reshaped": y_val_reshaped,
            "x_test_reshaped": x_test_reshaped,
            "y_test_reshaped": y_test_reshaped,
        }

        return reshaped_data


# utils
# TODO : can we use this to select the ideal number of features ?
def feature_selection_analysis(feature_selection_id: int, n_components: int = 5):

    feature_selection = FeatureSelection.get(feature_selection_id)
    experiment_dir = feature_selection.experiment.path
    features = [f.name for f in feature_selection.features]
    target = feature_selection.target.name
    target_number = target.split("_")[1]

    train, val, train_scaled, val_scaled, _scaler_y = load_train_data(
        experiment_dir, target_number, target_type=feature_selection.target.type
    )
    train = train[features + [target]]
    train_scaled = train_scaled[features + [target]]

    logger.info("Plot features correlation with target variable...")

    correlations = train.corr()[target].sort_values(ascending=False)

    plt.figure(figsize=(12, 6))
    sns.barplot(x=correlations.index, y=correlations.values, palette="coolwarm")
    plt.xticks(rotation=90)
    plt.title("Feature correlation with target variable")
    plt.ylabel("Correlation")
    plt.xlabel("Features")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

    plt.figure(figsize=(14, 10))
    sns.heatmap(train.corr(), annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title("Correlation Matrix")
    plt.show()

    logger.info("Plot explained variance by components...")
    n_components = min(len(features), n_components)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(train_scaled)

    explained_variance = pca.explained_variance_ratio_

    plt.figure(figsize=(10, 7))
    plt.bar(
        range(1, len(explained_variance) + 1),
        explained_variance,
        label="Explained Variance",
    )
    plt.plot(
        range(1, len(explained_variance) + 1),
        np.cumsum(explained_variance),
        label="Cumulative Explained Variance",
        color="orange",
        marker="o",
    )
    plt.title("Explained Variance by Components")
    plt.xlabel("Number of Components")
    plt.ylabel("Explained Variance")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

    logger.info("Main PCA vs target variable...")
    plt.scatter(
        X_pca[:, 0],
        X_pca[:, 1],
        c=train[target],
        cmap="coolwarm",
        alpha=0.7,
    )
    plt.title("PCA of target variable")
    plt.xlabel("First Principal Component")
    plt.ylabel("Second Principal Component")
    plt.colorbar()
    plt.show()


def get_features_by_types(df: pd.DataFrame, sample_categorical_threshold: int = 15):
    categorical_features = [
        col
        for col in df.columns
        if df[col].nunique() <= sample_categorical_threshold
        and df[col].dtype in ["int64", "Int64"]
        and (df[col] >= 0).all()
    ]
    df_categorical = df[categorical_features]
    logger.info(f"Number of categorical features: {len(categorical_features)}")

    numerical_features = list(set(df.columns).difference(set(categorical_features)))
    df_numerical = df[numerical_features]
    logger.info(f"Number of numerical features: {len(numerical_features)}")

    return df_categorical, df_numerical
