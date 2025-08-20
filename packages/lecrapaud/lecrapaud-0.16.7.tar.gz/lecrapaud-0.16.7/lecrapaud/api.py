"""LeCrapaud API module.

This module provides the main interface for the LeCrapaud machine learning pipeline.
It allows for end-to-end ML workflows including data preprocessing, feature engineering,
model training, and prediction.

Basic Usage:
    # Create a LeCrapaud instance
    lc = LeCrapaud()

    # Create a new experiment
    experiment = lc.create_experiment(data, target_numbers=[1], target_clf=[1])

    # Train a model
    best_features, artifacts, best_model = experiment.train(data)

    # Make predictions
    predictions, scores_reg, scores_clf = experiment.predict(new_data)

    # Or use individual pipeline steps:
    processed_data = experiment.feature_engineering(data)  # Feature engineering
    train, val, test = experiment.preprocess_feature(data)  # Data splitting and encoding
    selected_features = experiment.feature_selection(train)  # Feature selection
    model_data = experiment.preprocess_model(train, val, test)  # Model preprocessing
    best_model = experiment.model_selection(model_data)  # Model selection
"""

import joblib
import pandas as pd
import ast
import os
import logging
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from lecrapaud.db.session import init_db
from lecrapaud.feature_selection import FeatureSelectionEngine, PreprocessModel
from lecrapaud.model_selection import (
    ModelSelectionEngine,
    ModelEngine,
    evaluate,
    load_model,
    plot_threshold,
    plot_evaluation_for_classification,
)
from lecrapaud.feature_engineering import FeatureEngineeringEngine, PreprocessFeature
from lecrapaud.experiment import create_experiment
from lecrapaud.db import Experiment
from lecrapaud.search_space import normalize_models_idx
from lecrapaud.utils import logger
from lecrapaud.directories import tmp_dir


class LeCrapaud:
    """Main class for interacting with the LeCrapaud ML pipeline.

    This class provides methods to create and retrieve experiments.

    Args:
        uri (str, optional): Database connection URI. If None, uses default connection.
    """

    def __init__(self, uri: str = None):
        """Initialize LeCrapaud with optional database URI."""
        init_db(uri=uri)

    def create_experiment(self, data: pd.DataFrame, **kwargs) -> "ExperimentEngine":
        """Create a new experiment.

        Args:
            data (pd.DataFrame): Input data for the experiment
            **kwargs: Additional arguments to configure the experiment

        Returns:
            ExperimentEngine: A new experiment instance
        """
        return ExperimentEngine(data=data, **kwargs)

    def get_experiment(self, id: int, **kwargs) -> "ExperimentEngine":
        """Retrieve an existing experiment by ID.

        Args:
            id (int): The ID of the experiment to retrieve
            **kwargs: Additional arguments to pass to the experiment

        Returns:
            ExperimentEngine: The retrieved experiment instance
        """
        return ExperimentEngine(id=id, **kwargs)

    def get_last_experiment_by_name(self, name: str, **kwargs) -> "ExperimentEngine":
        """Retrieve the last experiment by name."""
        return ExperimentEngine(id=Experiment.get_last_by_name(name).id, **kwargs)

    def get_best_experiment_by_name(
        self, name: str, metric: str = "both", **kwargs
    ) -> "ExperimentEngine":
        """Retrieve the best experiment by score."""
        return ExperimentEngine(
            id=Experiment.get_best_by_score(name=name, metric=metric).id, **kwargs
        )

    def compare_experiment_scores(self, name: str):
        """Compare scores of experiments with matching names.
        
        Args:
            name (str): Name or partial name of experiments to compare
            
        Returns:
            dict: Dictionary containing experiment names as keys and their scores as values
        """
        from lecrapaud.db import SessionLocal
        from sqlalchemy.orm import joinedload
        
        db = SessionLocal()
        try:
            # Get all experiments with the given name pattern
            experiments = (
                db.query(Experiment)
                .options(joinedload(Experiment.model_selections)
                        .joinedload(ModelSelection.scores))
                .filter(Experiment.name.ilike(f"%{name}%"))
                .all()
            )
            
            if not experiments:
                return {"error": f"No experiments found with name containing '{name}'"}
                
            comparison = {}
            
            for exp in experiments:
                scores = {
                    "rmse": exp.avg_rmse,
                    "logloss": exp.avg_logloss,
                    "accuracy": None,
                    "f1": None,
                    "roc_auc": None
                }
                
                # Get classification metrics from the first model selection with scores
                for model_sel in exp.model_selections:
                    if model_sel.scores:
                        for score in model_sel.scores:
                            if score.type == 'validation':  # Use validation scores
                                if score.accuracy is not None:
                                    scores["accuracy"] = score.accuracy
                                if score.f1 is not None:
                                    scores["f1"] = score.f1
                                if score.roc_auc is not None:
                                    scores["roc_auc"] = score.roc_auc
                                break
                
                comparison[exp.name] = scores
                
            return comparison
            
        except Exception as e:
            return {"error": f"Error comparing experiment scores: {str(e)}"}
        finally:
            db.close()
    
    def list_experiments(
        self, name: str = None, limit: int = 1000
    ) -> list["ExperimentEngine"]:
        """List all experiments in the database."""
        return [
            ExperimentEngine(id=exp.id)
            for exp in Experiment.get_all_by_name(name=name, limit=limit)
        ]


class ExperimentEngine:
    """Engine for managing ML experiments.

    This class handles the complete ML pipeline including feature engineering,
    model training, and prediction. It can be initialized with either new data
    or by loading an existing experiment by ID.

    Args:
        id (int, optional): ID of an existing experiment to load
        data (pd.DataFrame, optional): Input data for a new experiment
        **kwargs: Additional configuration parameters
    """

    def __init__(self, id: int = None, data: pd.DataFrame = None, **kwargs):
        """Initialize the experiment engine with either new or existing experiment."""
        if id:
            self.experiment = Experiment.get(id)
            kwargs.update(self.experiment.context)
            experiment_dir = f"{tmp_dir}/{self.experiment.name}"
            preprocessing_dir = f"{experiment_dir}/preprocessing"
            data_dir = f"{experiment_dir}/data"
            os.makedirs(preprocessing_dir, exist_ok=True)
            os.makedirs(data_dir, exist_ok=True)
        else:
            if data is None:
                raise ValueError(
                    "Either id or data must be provided. Data can be a path to a folder containing trained models"
                )
            self.experiment = create_experiment(data=data, **kwargs)

        # Set all kwargs as instance attributes
        for key, value in kwargs.items():
            if key == "models_idx":
                value = normalize_models_idx(value)
            setattr(self, key, value)

    def train(self, data, best_params=None):
        logger.info("Running training...")

        data_eng = self.feature_engineering(data)
        logger.info("Feature engineering done.")

        train, val, test = self.preprocess_feature(data_eng)
        logger.info("Feature preprocessing done.")

        self.feature_selection(train)
        logger.info("Feature selection done.")

        std_data, reshaped_data = self.preprocess_model(train, val, test)
        logger.info("Model preprocessing done.")

        self.model_selection(std_data, reshaped_data, best_params=best_params)
        logger.info("Model selection done.")

    def predict(self, new_data, verbose: int = 0):
        # for scores if TARGET is in columns
        scores_reg = []
        scores_clf = []

        if verbose == 0:
            logger.setLevel(logging.WARNING)

        logger.warning("Running prediction...")

        # feature engineering + preprocessing
        data = self.feature_engineering(
            data=new_data,
            for_training=False,
        )
        data = self.preprocess_feature(data, for_training=False)
        data, scaled_data, reshaped_data = self.preprocess_model(
            data, for_training=False
        )

        for target_number in self.target_numbers:

            # loading model
            target_dir = f"{self.experiment.path}/TARGET_{target_number}"
            all_features = self.experiment.get_all_features(
                date_column=self.date_column, group_column=self.group_column
            )
            features = self.experiment.get_features(target_number)

            model = ModelEngine(path=target_dir, target_number=target_number)

            # getting data
            if model.recurrent:
                features_idx = [
                    i for i, e in enumerate(all_features) if e in set(features)
                ]
                x_pred = reshaped_data[:, :, features_idx]
            else:
                x_pred = scaled_data[features] if model.need_scaling else data[features]

            # predicting
            y_pred = model.predict(x_pred)

            # fix for recurrent model because x_val has no index as it is a 3D np array
            if model.recurrent:
                y_pred.index = (
                    new_data.index
                )  # TODO: not sure this will work for old experiment not aligned with data_for_training for test use case (done, this is why we decode the test set)

            # unscaling prediction
            if (
                model.need_scaling
                and model.target_type == "regression"
                and model.scaler_y is not None
            ):
                y_pred = pd.Series(
                    model.scaler_y.inverse_transform(
                        y_pred.values.reshape(-1, 1)
                    ).flatten(),
                    index=new_data.index,
                )
                y_pred.name = "PRED"

            # evaluate if TARGET is in columns (case-insensitive check)
            target_col = next(
                (
                    col
                    for col in new_data.columns
                    if col.upper() == f"TARGET_{target_number}"
                ),
                None,
            )
            if target_col is not None:
                y_true = new_data[target_col]
                prediction = pd.concat([y_true, y_pred], axis=1)
                prediction.rename(columns={target_col: "TARGET"}, inplace=True)
                score = evaluate(
                    prediction,
                    target_type=model.target_type,
                )
                score["TARGET"] = f"TARGET_{target_number}"

                if model.target_type == "classification":
                    scores_clf.append(score)
                else:
                    scores_reg.append(score)

            # renaming and concatenating with initial data
            if isinstance(y_pred, pd.DataFrame):
                y_pred = y_pred.add_prefix(f"TARGET_{target_number}_")
                new_data = pd.concat([new_data, y_pred], axis=1)

            else:
                y_pred.name = f"TARGET_{target_number}_PRED"
                new_data = pd.concat([new_data, y_pred], axis=1)

        if len(scores_reg) > 0:
            scores_reg = pd.DataFrame(scores_reg).set_index("TARGET")
        if len(scores_clf) > 0:
            scores_clf = pd.DataFrame(scores_clf).set_index("TARGET")
        return new_data, scores_reg, scores_clf

    def feature_engineering(self, data, for_training=True):
        app = FeatureEngineeringEngine(
            data=data,
            columns_drop=self.columns_drop,
            columns_boolean=self.columns_boolean,
            columns_date=self.columns_date,
            columns_te_groupby=self.columns_te_groupby,
            columns_te_target=self.columns_te_target,
            for_training=for_training,
        )
        data = app.run()
        return data

    def preprocess_feature(self, data, for_training=True):
        app = PreprocessFeature(
            data=data,
            experiment=self.experiment,
            time_series=self.time_series,
            date_column=self.date_column,
            group_column=self.group_column,
            val_size=self.val_size,
            test_size=self.test_size,
            columns_pca=self.columns_pca,
            columns_onehot=self.columns_onehot,
            columns_binary=self.columns_binary,
            columns_frequency=self.columns_frequency,
            columns_ordinal=self.columns_ordinal,
            target_numbers=self.target_numbers,
            target_clf=self.target_clf,
        )
        if for_training:
            train, val, test = app.run()
            return train, val, test
        else:
            data = app.inference()
            return data

    def feature_selection(self, train):
        for target_number in self.target_numbers:
            app = FeatureSelectionEngine(
                train=train,
                target_number=target_number,
                experiment=self.experiment,
                target_clf=self.target_clf,
            )
            app.run()
        self.experiment = Experiment.get(self.experiment.id)
        all_features = self.experiment.get_all_features(
            date_column=self.date_column, group_column=self.group_column
        )
        joblib.dump(
            all_features, f"{self.experiment.path}/preprocessing/all_features.pkl"
        )
        return all_features

    def preprocess_model(self, train, val=None, test=None, for_training=True):
        app = PreprocessModel(
            train=train,
            val=val,
            test=test,
            experiment=self.experiment,
            target_numbers=self.target_numbers,
            target_clf=self.target_clf,
            models_idx=self.models_idx,
            time_series=self.time_series,
            max_timesteps=self.max_timesteps,
            date_column=self.date_column,
            group_column=self.group_column,
        )
        if for_training:
            data, reshaped_data = app.run()
            return data, reshaped_data
        else:
            data, scaled_data, reshaped_data = app.inference()
            return data, scaled_data, reshaped_data

    def model_selection(self, data, reshaped_data, best_params=None):
        for target_number in self.target_numbers:
            app = ModelSelectionEngine(
                data=data,
                reshaped_data=reshaped_data,
                target_number=target_number,
                experiment=self.experiment,
                target_clf=self.target_clf,
                models_idx=self.models_idx,
                time_series=self.time_series,
                date_column=self.date_column,
                group_column=self.group_column,
                target_clf_thresholds=self.target_clf_thresholds,
            )
            if best_params and target_number not in best_params.keys():
                raise ValueError(
                    f"Target {target_number} not found in best_params passed as argument"
                )
            app.run(
                self.experiment_name,
                perform_hyperopt=self.perform_hyperopt,
                number_of_trials=self.number_of_trials,
                perform_crossval=self.perform_crossval,
                plot=self.plot,
                preserve_model=self.preserve_model,
                best_params=best_params[target_number] if best_params else None,
            )

    def get_scores(self, target_number: int):
        return pd.read_csv(
            f"{self.experiment.path}/TARGET_{target_number}/scores_tracking.csv"
        )

    def get_prediction(self, target_number: int, model_name: str):
        return pd.read_csv(
            f"{self.experiment.path}/TARGET_{target_number}/{model_name}/prediction.csv"
        )

    def get_feature_summary(self):
        return pd.read_csv(f"{self.experiment.path}/feature_summary.csv")

    def get_threshold(self, target_number: int):
        thresholds = joblib.load(
            f"{self.experiment.path}/TARGET_{target_number}/thresholds.pkl"
        )
        if isinstance(thresholds, str):
            thresholds = ast.literal_eval(thresholds)

        return thresholds

    def load_model(self, target_number: int, model_name: str = None):

        if not model_name:
            return load_model(f"{self.experiment.path}/TARGET_{target_number}")

        return load_model(f"{self.experiment.path}/TARGET_{target_number}/{model_name}")

    def plot_feature_importance(
        self, target_number: int, model_name="linear", top_n=30
    ):
        """
        Plot feature importance ranking.

        Args:
            target_number (int): Target variable number
            model_name (str): Name of the model to load
            top_n (int): Number of top features to display
        """
        model = self.load_model(target_number, model_name)
        experiment = self.experiment

        # Get feature names
        feature_names = experiment.get_features(target_number)

        # Get feature importances based on model type
        if hasattr(model, "feature_importances_"):
            # For sklearn tree models
            importances = model.feature_importances_
            importance_type = "Gini"
        elif hasattr(model, "get_score"):
            # For xgboost models
            importance_dict = model.get_score(importance_type="weight")
            importances = np.zeros(len(feature_names))
            for i, feat in enumerate(feature_names):
                if feat in importance_dict:
                    importances[i] = importance_dict[feat]
            importance_type = "Weight"
        elif hasattr(model, "feature_importance"):
            # For lightgbm models
            importances = model.feature_importance(importance_type="split")
            importance_type = "Split"
        elif hasattr(model, "coef_"):
            # For linear models
            importances = np.abs(model.coef_.flatten())
            importance_type = "Absolute coefficient"
        else:
            raise ValueError(
                f"Model {model_name} does not support feature importance calculation"
            )

        # Create a DataFrame for easier manipulation
        importance_df = pd.DataFrame(
            {"feature": feature_names[: len(importances)], "importance": importances}
        )

        # Sort features by importance and take top N
        importance_df = importance_df.sort_values("importance", ascending=False).head(
            top_n
        )

        # Create the plot
        plt.figure(figsize=(10, max(6, len(importance_df) * 0.3)))
        ax = sns.barplot(
            data=importance_df,
            x="importance",
            y="feature",
            palette="viridis",
            orient="h",
        )

        # Add value labels
        for i, v in enumerate(importance_df["importance"]):
            ax.text(v, i, f"{v:.4f}", color="black", ha="left", va="center")

        plt.title(f"Feature Importance ({importance_type})")
        plt.tight_layout()
        plt.show()

        return importance_df

    def plot_evaluation_for_classification(
        self, target_number: int, model_name="linear"
    ):
        prediction = self.get_prediction(target_number, model_name)
        thresholds = self.get_threshold(target_number)

        plot_evaluation_for_classification(prediction)

        for class_label, metrics in thresholds.items():
            threshold = metrics["threshold"]
            precision = metrics["precision"]
            recall = metrics["recall"]
            if threshold is not None:
                tmp_pred = prediction[["TARGET", "PRED", class_label]].copy()
                tmp_pred.rename(columns={class_label: 1}, inplace=True)
                print(f"Class {class_label}:")
                plot_threshold(tmp_pred, threshold, precision, recall)
            else:
                print(f"No threshold found for class {class_label}")

    def get_best_params(self, target_number: int = None) -> dict:
        """
        Load the best parameters for the experiment.

        Args:
            target_number (int, optional): If provided, returns parameters for this specific target.
                                         If None, returns parameters for all targets.

        Returns:
            dict: Dictionary containing the best parameters. If target_number is provided,
                  returns parameters for that target only. Otherwise, returns a dictionary
                  with target numbers as keys.
        """
        import json
        import os

        params_file = os.path.join(
            self.experiment.path, "preprocessing", "all_targets_best_params.json"
        )

        if not os.path.exists(params_file):
            raise FileNotFoundError(
                f"Best parameters file not found at {params_file}. "
                "Make sure to run model training first."
            )

        try:
            with open(params_file, "r") as f:
                all_params = json.load(f)

            # Convert string keys to integers
            all_params = {int(k): v for k, v in all_params.items()}

            if target_number is not None:
                if target_number not in all_params:
                    available_targets = list(all_params.keys())
                    raise ValueError(
                        f"No parameters found for target {target_number}. "
                        f"Available targets: {available_targets}"
                    )
                return all_params[target_number]

            return all_params

        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing best parameters file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading best parameters: {str(e)}")
