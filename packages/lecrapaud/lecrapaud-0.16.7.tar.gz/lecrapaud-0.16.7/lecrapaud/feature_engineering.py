"""
Feature engineering module for data preprocessing and transformation.

Process
-------
FEAT ENG
- utiliser business_analysis > get_table_summary pour voir quels sont les champs null à + de 90%
- utiliser remove_constant_columns pour supprimer les colonnes constantes
- utiliser summarize_dataframe pour supprimer de nouvelles colonnes inutiles (date, id, donnée future à la prédiction, misc not useful)
- caster en numeric ce qui peut être casté en numeric

- definir columns_boolean
- definir groupby_columns_list et target_column pour le target encoding
- créer la/les targets
- définir columns_pca
- définir columns_one_hot, columns_binary, columns_ordinal, columns_frequency


Todo
----
- DONE: drop meaningless identifier columns
- DONE: PCA on embedding of deck
- DONE: maybe cyclic encoding for date columns

- DONE: ordinal/label encode (only 1 column) for tree based method when not too big number of categories
- DONE: frequency encoding for some categorical columns
- DONE: one hot encoding for categorical columns
- DONE: binary encoding if big number of category

- DONE: create other other embedding column for textual data ?
- DONE: create some boolean like has_website, has_linkedin_company_url, etc...

- target/mean encoding with a groupby on a very interesting categorical column
- faire du "vrai" target encoding avec du leave one out encoding par exemple, sur la target variable ?

- better categorize some stuff like country ? for sourcing we do position, ext_position, company, ext_company, country, source, but only country is relevant here


Development
-----------
- utiliser le PCA pour définir combien de variable explique la variance pour la feature selection max_feature
- could be nice to get linkedin info of founders (need to search reps in rails first) - and score !
- add created_from, utm_source, referrer when we will have more data
- could be nice to get team_count, or dealroom info but at the moment of submission...
"""

import pandas as pd
import numpy as np
from itertools import product
import joblib
import os

from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from category_encoders import BinaryEncoder, CountEncoder
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split

from lecrapaud.integrations.openai_integration import (
    truncate_text,
    get_openai_embeddings,
)
from lecrapaud.feature_selection import get_features_by_types
from lecrapaud.utils import logger
from lecrapaud.db import Target, Feature, Experiment
from lecrapaud.config import PYTHON_ENV


# main function
class FeatureEngineeringEngine:
    """
    Feature engineering pipeline

    Params needed
    -------------
    data
    columns_boolean
    columns_date
    columns_te_groupby
    columns_te_target
    for_training
    """

    def __init__(
        self,
        data: pd.DataFrame,
        columns_drop: list[str] = [],
        columns_boolean: list[str] = [],
        columns_date: list[str] = [],
        columns_te_groupby: list[str] = [],
        columns_te_target: list[str] = [],
        for_training: bool = True,
        **kwargs,
    ):
        self.data = data
        self.columns_drop = columns_drop
        self.columns_boolean = columns_boolean
        self.columns_date = columns_date
        self.columns_te_groupby = columns_te_groupby
        self.columns_te_target = columns_te_target
        self.for_training = for_training

    def run(self) -> pd.DataFrame:
        # drop columns
        self.data = self.data.drop(columns=self.columns_drop, errors="ignore")

        # convert object columns to numeric if possible
        self.data = convert_object_columns_that_are_numeric(self.data)

        # handle boolean features
        self.data = self.boolean_encode_columns()

        # handle missing values
        self.data = (
            self.fillna_at_training()
            if self.for_training
            else self.fillna_at_inference()
        )

        # target encoding
        self.data = self.generate_target_encodings()

        # Cyclic encode dates
        self.data = self.cyclic_encode_date()

        return self.data

    def cyclic_encode_date(self) -> pd.DataFrame:
        """
        Adds cyclic (sine and cosine) encoding for common date parts: day of week, day of month, and month.

        Parameters:
            df (pd.DataFrame): Input dataframe
            columns (list[str]): List of datetime columns to encode
            prefix (str): Optional prefix for new columns. If None, uses column names.

        Returns:
            pd.DataFrame: Updated dataframe with new cyclic features
        """

        df: pd.DataFrame = self.data
        columns: list[str] = self.columns_date

        def cyclic_encode(series, max_value):
            sin_values = np.sin(2 * np.pi * series / max_value)
            cos_values = np.cos(2 * np.pi * series / max_value)
            return sin_values, cos_values

        for col in columns:

            df[col] = pd.to_datetime(df[col]).dt.normalize()
            df[f"{col}_year"] = df[col].dt.isocalendar().year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_week"] = df[col].dt.isocalendar().week
            df[f"{col}_weekday"] = df[col].dt.weekday
            df[f"{col}_yearday"] = df[col].dt.dayofyear
            df[col] = pd.to_datetime(df[col]).map(pd.Timestamp.toordinal)

            df[f"{col}_month_sin"], df[f"{col}_month_cos"] = cyclic_encode(
                df[f"{col}_month"], 12
            )
            df[f"{col}_day_sin"], df[f"{col}_day_cos"] = cyclic_encode(
                df[f"{col}_day"], 31
            )
            df[f"{col}_week_sin"], df[f"{col}_week_cos"] = cyclic_encode(
                df[f"{col}_week"], 52
            )
            df[f"{col}_weekday_sin"], df[f"{col}_weekday_cos"] = cyclic_encode(
                df[f"{col}_weekday"], 7
            )
            df[f"{col}_yearday_sin"], df[f"{col}_yearday_cos"] = cyclic_encode(
                df[f"{col}_yearday"], 365
            )

            # Drop the original column TODO: not sure if we should drop it for time series
            # df.drop(col, axis=1, inplace=True)

        return df

    def boolean_encode_columns(self) -> pd.DataFrame:
        """
        Applies boolean encoding to a list of columns:
        - Leaves column as-is if already int with only 0 and 1
        - Otherwise: sets 1 if value is present (notna), 0 if null/NaN/None

        Parameters:
            df (pd.DataFrame): Input dataframe
            columns (list): List of column names to encode

        Returns:
            pd.DataFrame: Updated dataframe with encoded columns
        """

        df: pd.DataFrame = self.data
        columns: list[str] = self.columns_boolean

        for column in columns:
            col = df[column]
            if pd.api.types.is_integer_dtype(col) and set(
                col.dropna().unique()
            ).issubset({0, 1}):
                continue  # already valid binary
            df[column] = col.notna().astype(int)
        return df

    def generate_target_encodings(self) -> pd.DataFrame:
        """
        Generate target encoding features (e.g., mean, median) for specified targets and group-by combinations.

        Parameters:
            df (pd.DataFrame): Input dataframe
            columns_te_groupby (list of list): Grouping keys, e.g., [["SECTOR", "DATE"], ["SUBINDUSTRY", "DATE"]]
            columns_te_target (list): Target columns to aggregate (e.g., ["RET", "VOLUME", "RSI_14"])
            statistics (list): List of aggregation statistics (e.g., ["mean", "median"])

        Returns:
            pd.DataFrame: Original dataframe with new encoded columns added
        """

        df: pd.DataFrame = self.data
        columns_te_groupby: list[list[str]] = self.columns_te_groupby
        columns_te_target: list[str] = self.columns_te_target
        statistics: list[str] = ["mean", "median"]

        df = df.copy()
        new_feature_cols = {}
        for group_cols, stat, target_col in product(
            columns_te_groupby, statistics, columns_te_target
        ):
            col_name = f"{target_col}_{'_'.join(group_cols)}_{stat.upper()}"
            new_feature_cols[col_name] = df.groupby(group_cols)[target_col].transform(
                stat
            )

        # merge all at once to improve performance
        df = pd.concat([df, pd.DataFrame(new_feature_cols)], axis=1)
        return df

    def fillna_at_training(self) -> pd.DataFrame:
        """
        Fill missing values in a DataFrame:
        - Numeric columns: fill with mean
        - Categorical columns: fill with mode
        Handles both NaN and None.

        Parameters:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: Cleaned DataFrame with missing values filled
        """

        df: pd.DataFrame = self.data.copy()

        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
                    logger.info(
                        f"Filled {missing_count} NaN values in numeric column '{col}' with mean."
                    )
                else:
                    mode = df[col].mode()
                    if not mode.empty:
                        mode_value = mode[0]
                        mode_count = (df[col] == mode_value).sum()
                        if mode_count > 100:
                            fill_value = mode_value
                        else:
                            fill_value = "unknown"
                    else:
                        fill_value = "unknown"

                    df[col] = df[col].fillna(fill_value)
                    logger.info(
                        f"Filled {missing_count} NaN values in categorical column '{col}' with '{fill_value}'."
                    )

        return df

    def fillna_at_inference(self) -> pd.DataFrame:

        df: pd.DataFrame = self.data

        missing_cols = df.columns[df.isnull().any()].tolist()

        if missing_cols:
            numeric_cols = [
                col for col in missing_cols if pd.api.types.is_numeric_dtype(df[col])
            ]
            non_numeric_cols = [col for col in missing_cols if col not in numeric_cols]

            logger.warning(
                f"Missing values found in inference data."
                f"Filling with 0 for numeric columns: {numeric_cols}, "
                f"and 'unknown' for non-numeric columns: {non_numeric_cols}"
            )

            df[numeric_cols] = df[numeric_cols].fillna(0)
            df[non_numeric_cols] = df[non_numeric_cols].fillna("unknown")

        return df


class PreprocessFeature:

    def __init__(
        self,
        data: pd.DataFrame,
        experiment,
        time_series: bool = False,
        date_column: str | None = None,
        group_column: str | None = None,
        val_size: float = 0.2,
        test_size: float = 0.2,
        columns_pca: list[str] = [],
        columns_onehot: list[str] = [],
        columns_binary: list[str] = [],
        columns_ordinal: list[str] = [],
        columns_frequency: list[str] = [],
        target_numbers: list = [],
        target_clf: list = [],
        **kwargs,
    ):
        self.data = data
        self.data.columns = self.data.columns.str.upper()

        self.experiment = experiment
        self.columns_pca = [col.upper() for col in columns_pca]
        self.columns_onehot = [col.upper() for col in columns_onehot]
        self.columns_binary = [col.upper() for col in columns_binary]
        self.columns_ordinal = [col.upper() for col in columns_ordinal]
        self.columns_frequency = [col.upper() for col in columns_frequency]
        self.target_numbers = target_numbers
        self.target_clf = target_clf

        self.time_series = time_series
        self.date_column = date_column
        self.group_column = group_column
        self.val_size = val_size
        self.test_size = test_size

        self.experiment_dir = self.experiment.path
        self.experiment_id = self.experiment.id
        self.data_dir = f"{self.experiment_dir}/data"
        self.preprocessing_dir = f"{self.experiment_dir}/preprocessing"

    def run(self):
        # Split
        train, val, test = (
            self.train_val_test_split_time_series()
            if self.time_series
            else self.train_val_test_split(
                stratify_col=f"TARGET_{self.target_numbers[0]}"
            )
        )  # TODO: only stratifying first target for now

        # PCA
        train, pcas = self.add_pca_features(train)
        val, _ = self.add_pca_features(val, pcas=pcas)
        test, _ = self.add_pca_features(test, pcas=pcas)

        joblib.dump(pcas, f"{self.preprocessing_dir}/pcas.pkl")

        # Save all features before encoding
        joblib.dump(
            list(train.columns),
            f"{self.preprocessing_dir}/all_features_before_encoding.pkl",
        )

        # Encoding
        train, transformer = self.encode_categorical_features(train)
        val, _ = self.encode_categorical_features(
            val,
            transformer=transformer,
        )
        test, _ = self.encode_categorical_features(
            test,
            transformer=transformer,
        )

        joblib.dump(self.data, f"{self.data_dir}/full.pkl")
        joblib.dump(transformer, f"{self.preprocessing_dir}/column_transformer.pkl")
        summary = summarize_dataframe(train)
        summary.to_csv(f"{self.experiment_dir}/feature_summary.csv", index=False)

        # Save all features before selection
        joblib.dump(
            list(train.columns),
            f"{self.preprocessing_dir}/all_features_before_selection.pkl",
        )

        return train, val, test

    def inference(self):
        data = self.data

        # PCA
        if os.path.exists(f"{self.preprocessing_dir}/pcas.pkl"):
            pcas = joblib.load(f"{self.preprocessing_dir}/pcas.pkl")
            data, _ = self.add_pca_features(data, pcas=pcas)

        # Encoding
        transformer = joblib.load(f"{self.preprocessing_dir}/column_transformer.pkl")
        data, _ = self.encode_categorical_features(
            data,
            transformer=transformer,
        )
        return data

    def train_val_test_split_time_series(self):
        df: pd.DataFrame = self.data
        date_column: str = self.date_column
        group_column: str = self.group_column
        val_size: float = self.val_size
        test_size: float = self.test_size

        if not date_column:
            ValueError("Please specify a date_column for time series")

        if group_column:
            df.sort_values([date_column, group_column], inplace=True)
        else:
            df.sort_values(date_column, inplace=True)

        dates = df[date_column].unique()

        val_first_id = int(len(dates) * (1 - val_size - test_size)) + 1
        test_first_id = int(len(dates) * (1 - test_size)) + 1

        train = df[df[date_column].isin(dates[:val_first_id])]
        val = df[df[date_column].isin(dates[val_first_id:test_first_id])]
        test = df[df[date_column].isin(dates[test_first_id:])]

        dates = {}
        for name, data in zip(["train", "val", "test"], [train, val, test]):
            dates[f"{name}_start_date"] = (
                data[date_column].map(pd.Timestamp.fromordinal).iat[0]
            )
            dates[f"{name}_end_date"] = (
                data[date_column].map(pd.Timestamp.fromordinal).iat[-1]
            )

            logger.info(
                f"{data.shape} {name} data from {dates[f"{name}_start_date"].strftime('%d/%m/%Y')} to {dates[f"{name}_end_date"].strftime('%d/%m/%Y')}"
            )

        Experiment.upsert(
            match_fields=["id"],
            id=self.experiment_id,
            train_size=len(train),
            val_size=len(val),
            test_size=len(test),
            **dates,
        )
        return (
            train.reset_index(drop=True),
            val.reset_index(drop=True),
            test.reset_index(drop=True),
        )

    def train_val_test_split(
        self,
        random_state: int = 42,
        stratify_col: str | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Splits a DataFrame into train, validation, and test sets.

        Parameters:
            df (pd.DataFrame): The full experiment
            val_size (float): Proportion of validation set (default 0.1)
            test_size (float): Proportion of test set (default 0.1)
            random_state (int): Random seed for reproducibility
            stratify_col (str | None): Optional column to stratify on (for classification tasks)

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        df: pd.DataFrame = self.data
        val_size: float = self.val_size
        test_size: float = self.test_size

        stratify_vals = df[stratify_col] if stratify_col else None

        # First split: train + (val + test)
        train, temp = train_test_split(
            df,
            test_size=val_size + test_size,
            random_state=random_state,
            stratify=stratify_vals,
        )

        # Adjust stratify target for val/test split
        stratify_temp = temp[stratify_col] if stratify_col else None

        # Compute val and test sizes relative to temp
        val_ratio = val_size / (val_size + test_size)

        val, test = train_test_split(
            temp,
            test_size=1 - val_ratio,
            random_state=random_state,
            stratify=stratify_temp,
        )

        for name, data in zip(["train", "val", "test"], [train, val, test]):
            logger.info(f"{data.shape} {name} data")

        Experiment.upsert(
            match_fields=["id"],
            id=self.experiment_id,
            train_size=len(train),
            val_size=len(val),
            test_size=len(test),
        )
        return (
            train.reset_index(drop=True),
            val.reset_index(drop=True),
            test.reset_index(drop=True),
        )

    # embedding and pca
    def add_pca_features(
        self, df: pd.DataFrame, n_components: int = 5, pcas=None
    ) -> tuple[pd.DataFrame, dict]:
        """
        Adds PCA components as new columns to a DataFrame from a column containing numpy arrays.
        NEED TRAIN/TEST SPLIT BEFORE APPLYING - LIKE ENCODING CATEGORICAL VARIABLES

        Parameters:
            df (pd.DataFrame): Input DataFrame
            column (str): Name of the column containing np.ndarray
            n_components (int): Number of PCA components to keep

        Returns:
            pd.DataFrame: DataFrame with new PCA columns added
        """
        columns: list[str] = self.columns_pca

        pcas_dict = {}
        for column in columns:
            # Convert text to embeddings if necessary
            if not isinstance(df[column].iloc[0], (np.ndarray, list)):
                sentences = df[column].astype(str).tolist()
                logger.info(
                    f"Total sentences to embed for column {column}: {len(sentences)}"
                )

                # Truncate each sentence
                truncate_sentences = [truncate_text(sentence) for sentence in sentences]

                # embedding
                embedding_matrix = get_openai_embeddings(truncate_sentences)
            else:
                logger.info(f"Column {column} is already embeddings")
                # Stack the vectors into a 2D array
                embedding_matrix = np.vstack(df[column].values)

            # Apply PCA
            if pcas:
                pca = pcas[column]
                pca_features = pca.transform(embedding_matrix)
            else:
                pca = PCA(n_components=n_components)
                pca_features = pca.fit_transform(embedding_matrix)

            # Add PCA columns
            for i in range(n_components):
                df[f"{column}_pca_{i+1}"] = pca_features[:, i]

            # Drop the original column
            df.drop(column, axis=1, inplace=True)
            pcas_dict.update({column: pca})

        return df, pcas_dict

    # encoding categorical features
    def encode_categorical_features(
        self,
        df: pd.DataFrame,
        transformer: ColumnTransformer | None = None,
    ) -> tuple[pd.DataFrame, ColumnTransformer]:
        """
        Encodes categorical columns using one-hot, binary, ordinal, and frequency encoding.

        Parameters:
            df (pd.DataFrame): Input DataFrame
            columns_onehot (list[str]) Creates one binary column per category forLow-cardinality categorical features
            columns_binary (list[str]) Converts categories into binary and splits bits across columns for Mid-to-high cardinality (e.g., 10–100 unique values)
            columns_ordinal (list[str]) Assigns integer ranks to categories When order matters (e.g., low < medium < high)
            columns_frequency (list[str]) Replaces each category with its frequency count, normalized to proportion. High-cardinality features with meaning in frequency
            transformer (ColumnTransformer, optional): if provided, applies transform only

        Returns:
            tuple: (transformed DataFrame, ColumnTransformer)
        """
        columns_onehot: list[str] = self.columns_onehot
        columns_binary: list[str] = self.columns_binary
        columns_ordinal: list[str] = self.columns_ordinal
        columns_frequency: list[str] = self.columns_frequency

        X = df.loc[:, ~df.columns.str.contains("^TARGET_")]
        y = df.loc[:, df.columns.str.contains("^TARGET_")]
        save_in_db = False

        all_columns = (
            columns_onehot + columns_binary + columns_ordinal + columns_frequency
        )

        if transformer:
            transformed = transformer.transform(X)
        else:
            transformer = ColumnTransformer(
                transformers=[
                    (
                        "onehot",
                        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        columns_onehot,
                    ),
                    (
                        "ordinal",
                        OrdinalEncoder(
                            handle_unknown="use_encoded_value", unknown_value=-1
                        ),
                        columns_ordinal,
                    ),
                    ("binary", BinaryEncoder(handle_unknown="value"), columns_binary),
                    ("freq", CountEncoder(normalize=True), columns_frequency),
                ],
                remainder="passthrough",
            )
            transformed = transformer.fit_transform(X)
            save_in_db = True

        # Build output column names
        column_names = []

        if columns_onehot:
            column_names.extend(
                transformer.named_transformers_["onehot"]
                .get_feature_names_out(columns_onehot)
                .tolist()
            )

        if columns_ordinal:
            column_names.extend(columns_ordinal)

        if columns_binary:
            column_names.extend(
                transformer.named_transformers_["binary"]
                .get_feature_names_out(columns_binary)
                .tolist()
            )

        if columns_frequency:
            column_names.extend(columns_frequency)

        # Add passthrough (non-encoded) columns
        passthrough_columns = [col for col in X.columns if col not in all_columns]
        column_names.extend(passthrough_columns)

        X_transformed = pd.DataFrame(transformed, columns=column_names, index=df.index)

        # Try to convert columns to best possible dtypes
        X_transformed = X_transformed.convert_dtypes()

        # Insert features in db
        if save_in_db:
            # Get feature types from transformed data
            categorical_features, numerical_features = get_features_by_types(
                X_transformed
            )

            # Get column names from DataFrames
            cat_feature_names = categorical_features.columns.tolist()
            num_feature_names = numerical_features.columns.tolist()

            # Combine all feature names and their types
            all_feature_names = cat_feature_names + num_feature_names
            all_feature_types = ["categorical"] * len(cat_feature_names) + [
                "numerical"
            ] * len(num_feature_names)

            # Upsert features in bulk if we have any features
            if all_feature_names:
                Feature.upsert_bulk(
                    match_fields=["name"],
                    name=all_feature_names,
                    type=all_feature_types,
                )

            # Upsert targets in bulk
            target_names = y.columns.tolist()
            target_types = [
                (
                    "classification"
                    if int(target.split("_")[1]) in self.target_clf
                    else "regression"
                )
                for target in target_names
            ]

            Target.upsert_bulk(
                match_fields=["name"], name=target_names, type=target_types
            )

            # Get all the upserted objects
            targets = Target.filter(name__in=target_names)

            # Update experiment with targets
            experiment = Experiment.get(self.experiment_id)
            if experiment:
                experiment.targets = targets
                experiment.save()

        return pd.concat([X_transformed, y], axis=1), transformer


# analysis & utils
def summarize_dataframe(
    df: pd.DataFrame, sample_categorical_threshold: int = 15
) -> pd.DataFrame:
    summary = []

    def is_hashable_series(series: pd.Series) -> bool:
        try:
            _ = series.dropna().unique()
            return True
        except TypeError:
            return False

    df = convert_object_columns_that_are_numeric(df)
    df = df.convert_dtypes()

    for col in df.columns:
        total_missing = df[col].isna().sum()
        col_data = df[col].dropna()
        dtype = col_data.dtype

        if col_data.empty:
            summary.append(
                {
                    "Column": col,
                    "Dtype": dtype,
                    "Type": "unknown",
                    "Detail": "No non-null values",
                    "Missing": total_missing,
                }
            )
            continue

        # Case 1: Numeric columns
        if pd.api.types.is_numeric_dtype(col_data):
            unique_vals = col_data.nunique()

            if set(col_data.unique()).issubset({0, 1}):
                col_type = "binary-categorical"
                detail = "0/1 values only"
            elif (
                pd.api.types.is_integer_dtype(col_data)
                and unique_vals <= sample_categorical_threshold
            ):
                col_type = "multi-categorical"
                top_vals = col_data.value_counts().head(10)
                detail = ", ".join(f"{k} ({v})" for k, v in top_vals.items())
            else:
                col_type = "numeric"
                q = col_data.quantile([0, 0.25, 0.5, 0.75, 1])
                detail = (
                    f"Min: {q.iloc[0]:.2f}, Q1: {q.iloc[1]:.2f}, Median: {q.iloc[2]:.2f}, "
                    f"Q3: {q.iloc[3]:.2f}, Max: {q.iloc[4]:.2f}"
                )

        # Case 2: Object or other hashable columns
        elif is_hashable_series(col_data):
            unique_vals = col_data.nunique()
            if unique_vals <= sample_categorical_threshold:
                col_type = "object-categorical"
                top_vals = col_data.value_counts().head(10)
                detail = ", ".join(f"{k} ({v})" for k, v in top_vals.items())
            else:
                col_type = "high-cardinality-categorical"
                detail = f"{unique_vals} unique values"

        # Case 3: Unusable columns
        else:
            col_type = "non-hashable"
            detail = f"Non-hashable type: {type(col_data.iloc[0])}"

        summary.append(
            {
                "Column": col,
                "Dtype": dtype,
                "Type": col_type,
                "Detail": detail,
                "Missing": total_missing,
            }
        )

    return pd.DataFrame(summary)


def convert_object_columns_that_are_numeric(df: pd.DataFrame) -> list:
    """
    Detect object columns that can be safely converted to numeric (float or int).

    Returns:
        List of column names that are object type but contain numeric values.
    """

    numeric_candidates = []

    for col in df.select_dtypes(include=["object"]).columns:
        try:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() / len(df) > 0.9:  # at least 90% convertible
                numeric_candidates.append(col)
        except Exception:
            continue

    for col in numeric_candidates:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def traditional_descriptive_analysis(df: pd.DataFrame, group_column: str | None = None):
    with pd.option_context("display.max_rows", None):
        results = {}

        # Shape
        results["Shape"] = f"{df.shape[0]} rows × {df.shape[1]} columns"

        # Create a copy of the DataFrame to avoid modifying the original
        df_check = df.copy()

        # Convert numpy arrays to tuples for hashing
        for col in df_check.columns:
            if df_check[col].apply(lambda x: isinstance(x, np.ndarray)).any():
                df_check[col] = df_check[col].apply(
                    lambda x: tuple(x) if isinstance(x, np.ndarray) else x
                )

        # Duplicated rows
        results["Duplicated rows"] = int(df_check.duplicated().sum())

        # Check for duplicated columns
        try:
            # Try to find duplicated columns
            duplicated_cols = []
            cols = df_check.columns
            for i, col1 in enumerate(cols):
                for col2 in cols[i + 1 :]:
                    if df_check[col1].equals(df_check[col2]):
                        duplicated_cols.append(f"{col1} = {col2}")

            results["Duplicated columns"] = (
                ", ".join(duplicated_cols) if duplicated_cols else "None"
            )
        except Exception as e:
            results["Duplicated columns"] = f"Could not check: {str(e)}"

        # Missing values
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        if len(missing) > 0:
            results["Missing values"] = missing.to_frame("Missing Count").to_markdown()
        else:
            results["Missing values"] = "No missing values"

        # Infinite values
        inf = df.replace([np.inf, -np.inf], np.nan)
        inf_count = inf.isnull().sum() - df.isnull().sum()
        inf_count = inf_count[inf_count > 0].sort_values(ascending=False)
        if len(inf_count) > 0:
            results["Infinite values"] = inf_count.to_frame("Inf Count").to_markdown()
        else:
            results["Infinite values"] = "No infinite values"

        # Constant columns
        constant_cols = [col for col in df.columns if df[col].nunique() == 1]
        results["Constant columns"] = (
            ", ".join(constant_cols) if len(constant_cols) > 0 else "None"
        )

        # Data types
        dtypes = df.dtypes.astype(str).sort_index()
        results["Data types"] = dtypes.to_frame("Type").to_markdown()

        # Unique values in group_column
        if group_column is not None:
            if group_column in df.columns:
                results[f"Unique values in '{group_column}'"] = int(
                    df[group_column].nunique()
                )
            else:
                results[f"Unique values in '{group_column}'"] = (
                    f"❌ Column '{group_column}' not found"
                )

        # Log all results
        for title, content in results.items():
            print(f"\n### {title}\n{content}")


def print_missing_values(df: pd.DataFrame):

    if len(df.isnull().sum().where(df.isnull().sum() != 0).dropna()):
        logger.info(
            f"Missing values : \n{df.isnull().sum().where(df.isnull().sum() != 0).dropna().sort_values(ascending=False).to_string()}"
        )
    else:
        logger.info("No missing values found")
