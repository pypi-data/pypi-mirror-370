import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import json
import warnings
import joblib
import glob
from pathlib import Path
import pickle
from pydantic import BaseModel

os.environ["COVERAGE_FILE"] = str(Path(".coverage").resolve())

# ML models
from sklearn.model_selection import TimeSeriesSplit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    mean_absolute_percentage_error,
    root_mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    log_loss,
    roc_auc_score,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
    confusion_matrix,
)
from sklearn.preprocessing import LabelBinarizer
import lightgbm as lgb
import xgboost as xgb

# DL models
import tensorflow as tf
import keras
from keras.callbacks import EarlyStopping, TensorBoard
from keras.metrics import (
    Precision,
    Recall,
    F1Score,
)
from keras.losses import BinaryCrossentropy, CategoricalCrossentropy
from keras.optimizers import Adam

K = tf.keras.backend
from tensorboardX import SummaryWriter

# Optimization
import ray
from ray.tune import Tuner, TuneConfig, with_parameters
from ray.train import RunConfig
from ray.tune.search.hyperopt import HyperOptSearch
from ray.tune.search.bayesopt import BayesOptSearch
from ray.tune.logger import TBXLoggerCallback
from ray.tune.schedulers import ASHAScheduler
from ray.air import session

# Internal library
from lecrapaud.search_space import all_models
from lecrapaud.directories import clean_directory
from lecrapaud.utils import copy_any, contains_best, logger, serialize_for_json
from lecrapaud.config import PYTHON_ENV
from lecrapaud.feature_selection import load_train_data
from lecrapaud.db import (
    Model,
    ModelSelection,
    ModelTraining,
    Score,
    Target,
    Experiment,
)

# Reproducible result
keras.utils.set_random_seed(42)
np.random.seed(42)
tf.config.experimental.enable_op_determinism()


# test configuration
def test_hardware():
    devices = tf.config.list_physical_devices()
    logger.info("\nDevices: ", devices)

    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        details = tf.config.experimental.get_device_details(gpus[0])
        logger.info("GPU details: ", details)


# Suppress specific warning messages related to file system monitor
# logging.getLogger("ray").setLevel(logging.CRITICAL)
# logging.getLogger("ray.train").setLevel(logging.CRITICAL)
# logging.getLogger("ray.tune").setLevel(logging.CRITICAL)
# logging.getLogger("ray.autoscaler").setLevel(logging.CRITICAL)
# logging.getLogger("ray.raylet").setLevel(logging.CRITICAL)
# logging.getLogger("ray.monitor").setLevel(logging.CRITICAL)
# logging.getLogger("ray.dashboard").setLevel(logging.CRITICAL)
# logging.getLogger("ray.gcs_server").setLevel(logging.CRITICAL)

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


class ModelEngine:

    def __init__(
        self,
        model_name: str = None,
        target_type: str = None,
        target_number: int = None,
        path: str = None,
        search_params: dict = {},
        create_model=None,
        plot: bool = False,
        log_dir: str = None,
    ):
        self.path = path
        if path:
            self.load()
        else:
            self.model_name = model_name
            self.target_type = target_type
            self.target_number = target_number

        config = [
            config for config in all_models if config["model_name"] == self.model_name
        ]
        if config is None or len(config) == 0:
            Exception(
                f"Model {self.model_name} is not supported by this library."
                f"Choose a model from the list of supported models: {[model['model_name'] for model in all_models].join(', ')}"
            )
        config = config[0]

        self.recurrent = config["recurrent"]
        self.need_scaling = config["need_scaling"]
        self.search_params = search_params
        self.create_model = create_model
        self.plot = plot
        self.log_dir = log_dir

        if self.path and self.need_scaling and self.target_type == "regression":
            self.scaler_y = joblib.load(f"{self.path}/scaler_y.pkl")
        else:
            self.scaler_y = None

        self.threshold = None

    def fit(self, *args):
        if self.recurrent:
            fit = self.fit_recurrent
        elif (self.create_model == "lgb") or (self.create_model == "xgb"):
            fit = self.fit_boosting
        else:
            fit = self.fit_sklearn
        model = fit(*args)
        return model

    # Functions to fit & evaluate models
    def fit_sklearn(self, x_train, y_train, x_val, y_val, params):

        # Create & Compile the model
        model = self.create_model(**params)

        # Train the model
        logger.info("Fitting the model...")
        logger.info(f"x_train shape: {x_train.shape}, x_val shape: {x_val.shape}")
        logger.info(f"y_train shape: {y_train.shape}, y_val shape: {y_val.shape}")

        model.fit(x_train, y_train)

        if (
            self.target_type == "classification"
            and "loss" in model.get_params().keys()
            and "hinge" in model.get_params()["loss"]
        ):
            # This is for SVC models with hinge loss
            # You should use CalibratedClassifierCV when you are working with classifiers that do not natively output well-calibrated probability estimates.
            # TODO: investigate if we should use calibration for random forest, gradiant boosting models, and bagging models
            logger.info(
                f"Re-Calibrating {self.model_name} to get predict probabilities..."
            )
            calibrator = CalibratedClassifierCV(model, cv="prefit", n_jobs=-1)
            model = calibrator.fit(x_train, y_train)

        # set model_name after calibrator
        model.model_name = self.model_name
        model.target_type = self.target_type

        logger.info(f"Successfully created a {model.model_name} at {datetime.now()}")

        self._model = model

        return model

    def fit_boosting(self, x_train, y_train, x_val, y_val, params):
        """
        This is using lightGBM or XGboost C++ librairies
        """
        lightGBM = self.create_model == "lgb"

        # Experiments
        boosting_dataset = lgb.Dataset if lightGBM else xgb.DMatrix
        train_data = boosting_dataset(x_train, label=y_train)
        val_data = boosting_dataset(x_val, label=y_val)

        # Create a TensorBoardX writer
        writer = SummaryWriter(self.log_dir)
        evals_result = {}

        # Training
        labels = np.unique(y_train)
        num_class = (
            labels.size
            if self.target_type == "classification" and labels.size > 2
            else 1
        )
        logger.info("Fitting the model...")
        logger.info(f"x_train shape: {x_train.shape}, x_val shape: {x_val.shape}")
        logger.info(f"y_train shape: {y_train.shape}, y_val shape: {y_val.shape}")

        if lightGBM:

            def tensorboard_callback(env):
                for i, metric in enumerate(env.evaluation_result_list):
                    metric_name, _, metric_value, _ = metric
                    writer.add_scalar(
                        f"LightGBM/{metric_name}", metric_value, env.iteration
                    )

            loss = (
                "regression"
                if self.target_type == "regression"
                else ("binary" if num_class <= 2 else "multiclass")
            )
            eval_metric = (
                "rmse"
                if self.target_type == "regression"
                else ("binary_logloss" if num_class <= 2 else "multi_logloss")
            )
            model = lgb.train(
                params={
                    **params["model_params"],
                    "objective": loss,
                    "metric": eval_metric,
                    "num_class": num_class,
                },
                num_boost_round=params["num_boost_round"],
                train_set=train_data,
                valid_sets=[train_data, val_data],
                valid_names=["train", "val"],
                callbacks=[
                    lgb.early_stopping(stopping_rounds=params["early_stopping_rounds"]),
                    lgb.record_evaluation(evals_result),
                    tensorboard_callback,
                ],
            )
        else:

            class TensorBoardCallback(xgb.callback.TrainingCallback):

                def __init__(self, log_dir: str):
                    self.writer = SummaryWriter(log_dir=log_dir)

                def after_iteration(
                    self,
                    model,
                    epoch: int,
                    evals_log: xgb.callback.TrainingCallback.EvalsLog,
                ) -> bool:
                    if not evals_log:
                        return False

                    for data, metric in evals_log.items():
                        for metric_name, log in metric.items():
                            score = (
                                log[-1][0] if isinstance(log[-1], tuple) else log[-1]
                            )
                            self.writer.add_scalar(f"XGBoost/{data}", score, epoch)

                    return False

            tensorboard_callback = TensorBoardCallback(self.log_dir)

            loss = (
                "reg:squarederror"
                if self.target_type == "regression"
                else ("binary:logistic" if num_class <= 2 else "multi:softprob")
            )
            eval_metric = (
                "rmse"
                if self.target_type == "regression"
                else ("logloss" if num_class <= 2 else "mlogloss")
            )
            model = xgb.train(
                params={
                    **params["model_params"],
                    "objective": loss,
                    "eval_metric": eval_metric,
                    "num_class": num_class,
                },
                num_boost_round=params["num_boost_round"],
                dtrain=train_data,
                evals=[(val_data, "val"), (train_data, "train")],
                callbacks=[
                    xgb.callback.EarlyStopping(
                        rounds=params["early_stopping_rounds"], save_best=True
                    ),
                    xgb.callback.EvaluationMonitor(),  # This shows evaluation results at each iteration
                    tensorboard_callback,
                ],
                evals_result=evals_result,  # Record evaluation result
                verbose_eval=0,
            )

        model.model_name = self.create_model
        model.target_type = self.target_type
        logger.info(f"Successfully created a {model.model_name} at {datetime.now()}")

        # Close the writer after training is done
        writer.close()

        if self.plot:
            # Plot training progress
            plot_training_progress(
                logs={
                    "train": evals_result["train"][eval_metric],
                    "val": evals_result["val"][eval_metric],
                },
                model_name=self.model_name,
                target_number=self.target_number,
                title_suffix=f"Training Progress - {eval_metric}",
            )

        self._model = model

        return model

    def fit_recurrent(self, x_train, y_train, x_val, y_val, params):

        # metrics functions
        def rmse_tf(y_true, y_pred):
            y_true, y_pred = unscale_tf(y_true, y_pred)
            results = K.sqrt(K.mean(K.square(y_pred - y_true)))
            return results

        def mae_tf(y_true, y_pred):
            y_true, y_pred = unscale_tf(y_true, y_pred)
            results = K.mean(K.abs(y_pred - y_true))
            return results

        def unscale_tf(y_true, y_pred):
            if self.target_type == "regression":
                scale = K.constant(self.scaler_y.scale_[0])
                mean = K.constant(self.scaler_y.mean_[0])

                y_true = K.mul(y_true, scale)
                y_true = K.bias_add(y_true, mean)

                y_pred = K.mul(y_pred, scale)
                y_pred = K.bias_add(y_pred, mean)
            return y_true, y_pred

        # Create the model
        labels = np.unique(y_train[:, 0])
        num_class = labels.size if self.target_type == "classification" else None
        input_shape = (x_train.shape[1], x_train.shape[2])
        model = self.create_model(params, input_shape, self.target_type, num_class)
        model.target_type = self.target_type

        # Compile the model
        loss = (
            rmse_tf
            if self.target_type == "regression"
            else (
                BinaryCrossentropy(from_logits=False)
                if num_class <= 2
                else CategoricalCrossentropy(from_logits=False)
            )
        )
        optimizer = Adam(
            learning_rate=params["learning_rate"], clipnorm=params["clipnorm"]
        )
        metrics = (
            [mae_tf]
            if self.target_type == "regression"
            else (
                ["accuracy", Precision(), Recall()]
                if num_class <= 2
                else ["categorical_accuracy"]
            )
        )
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

        # Callbacks
        tensorboard_callback = TensorBoard(log_dir=self.log_dir)
        early_stopping_callback = EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
            start_from_epoch=5,
        )

        # Custom callbacks
        class PrintTrainableWeights(keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs={}):
                logger.info(model.trainable_variables)

        class GradientCalcCallback(keras.callbacks.Callback):
            def __init__(self):
                self.epoch_gradient = []

            def get_gradient_func(self, model):
                # grads = K.gradients(model.total_loss, model.trainable_weights)
                grads = K.gradients(model.loss, model.trainable_weights)
                # inputs = model.model.inputs + model.targets + model.sample_weights
                # use below line of code if above line doesn't work for you
                # inputs = model.model._feed_inputs + model.model._feed_targets + model.model._feed_sample_weights
                inputs = (
                    model._feed_inputs
                    + model._feed_targets
                    + model._feed_sample_weights
                )
                func = K.function(inputs, grads)
                return func

            def on_epoch_end(self, epoch, logs=None):
                get_gradient = self.get_gradient_func(model)
                grads = get_gradient([x_val, y_val[:, 0], np.ones(len(y_val[:, 0]))])
                self.epoch_gradient.append(grads)

        # Train the model
        if self.target_type == "classification" and num_class > 2:
            lb = LabelBinarizer(sparse_output=False)  # Change to True for sparse matrix
            lb.fit(labels)
            y_train = lb.transform(y_train[:, 0].flatten())
            y_val = lb.transform(y_val[:, 0].flatten())
        else:
            y_train = y_train[:, 0].flatten()
            y_val = y_val[:, 0].flatten()

        logger.info("Fitting the model...")
        logger.info(f"x_train shape: {x_train.shape}, x_val shape: {x_val.shape}")
        logger.info(f"y_train shape: {y_train.shape}, y_val shape: {y_val.shape}")

        history = model.fit(
            x_train,
            y_train,
            batch_size=params["batch_size"],
            verbose=0,
            epochs=params["epochs"],
            shuffle=False,
            validation_data=(x_val, y_val),
            callbacks=[early_stopping_callback, tensorboard_callback],
        )

        logger.info(f"Successfully created a {model.model_name} at {datetime.now()}")
        # logger.info(pd.DataFrame(gradiant.epoch_gradient))

        if self.plot:
            # Plot training progress using the utility function
            plot_training_progress(
                logs=history.history,
                model_name=self.model_name,
                target_number=self.target_number,
            )

        self._model = model

        return model

    def predict(
        self,
        data: pd.DataFrame | np.ndarray,
        threshold: float = 0.5,
    ):
        """Function to get prediction from model. Support sklearn, keras and boosting models such as xgboost and lgboost

        Args:
            - data: the data for prediction
            - threshold: the threshold for classification
        """
        if not self._model:
            raise Exception(
                "Model is not fitted, cannot predict, run model.fit() first, or pass a fitted model when creating the Model object to the `model` parameter."
            )
        model = self._model

        if self.threshold and threshold == 0.5:
            threshold = self.threshold

        # Determine index for output
        if isinstance(data, pd.DataFrame):
            index = data.index
        elif isinstance(data, np.ndarray):
            index = pd.RangeIndex(start=0, stop=data.shape[0])
        else:
            raise ValueError(
                "Unsupported data type: expected pd.DataFrame or np.ndarray"
            )

        # Keras, LightGBM, XGBoost
        if self.recurrent or self.model_name in ["lgb", "xgb"]:
            if self.model_name == "xgb":
                data_input = xgb.DMatrix(data)
                pred_raw = model.predict(data_input)
            else:
                pred_raw = model.predict(data)

            if pred_raw.ndim == 1:
                pred_raw = pred_raw.reshape(-1, 1)

            if self.target_type == "classification":
                num_class = pred_raw.shape[1] if pred_raw.ndim > 1 else 2
                if num_class <= 2:
                    pred_proba = pd.DataFrame(
                        {0: 1 - pred_raw.ravel(), 1: pred_raw.ravel()}, index=index
                    )
                else:
                    pred_proba = pd.DataFrame(
                        pred_raw, columns=range(num_class), index=index
                    )

                pred_df = apply_thresholds(pred_proba, threshold, pred_proba.columns)
            else:
                pred_df = pd.Series(pred_raw.ravel(), index=index, name="PRED")

        # Sklearn
        else:
            if self.target_type == "classification":
                pred_proba = pd.DataFrame(
                    model.predict_proba(data),
                    index=index,
                    columns=[
                        int(c) if isinstance(c, float) and c.is_integer() else c
                        for c in model.classes_
                    ],
                )
                pred_df = apply_thresholds(pred_proba, threshold, model.classes_)
            else:
                pred_df = pd.Series(model.predict(data), index=index, name="PRED")

        return pred_df

    def save(self, path):
        if self.recurrent:
            path += "/" + self.model_name + ".keras"
            self._model.save(path)
        else:
            path += "/" + self.model_name + ".best"
            joblib.dump(self._model, path)
        self.path = path
        return path

    def load(self):
        if not self.path:
            raise ValueError("Path is not set, cannot load model")

        self._model = load_model(self.path)

        self.model_name = self._model.model_name
        self.target_type = self._model.target_type

        # Load threshold
        if (
            os.path.exists(f"{self.path}/thresholds.pkl")
            and self.target_type == "classification"
        ):
            self.threshold = joblib.load(f"{self.path}/thresholds.pkl")
        else:
            self.threshold = None

        logger.info(
            f"Loaded model {self._model.model_name} and threshold {self.threshold}"
        )


def trainable(
    params,
    x_train,
    y_train,
    x_val,
    y_val,
    model_name,
    target_type,
    experiment_name,
    target_number,
    create_model,
    type_name="hyperopts",
    plot=False,
    log_dir=None,
    target_clf_thresholds: dict = None,
):
    """Standalone version of train_model that doesn't depend on self"""
    # Create model engine
    model = ModelEngine(
        model_name=model_name,
        target_type=target_type,
        target_number=target_number,
        create_model=create_model,
        plot=plot,
        log_dir=log_dir,
    )

    logger.info(
        f"TARGET_{target_number} - Training a {model.model_name} at {datetime.now()} : {experiment_name}, TARGET_{target_number}"
    )

    if model.recurrent:
        timesteps = params["timesteps"]
        x_train = x_train[:, -timesteps:, :]
        x_val = x_val[:, -timesteps:, :]

    # Compile and fit model on train set
    start = time.time()
    model.fit(x_train, y_train, x_val, y_val, params)
    stop = time.time()

    # Prediction on val set
    y_pred = model.predict(x_val)

    # fix for recurrent model because x_val has no index as it is a 3D np array
    if model.recurrent:
        y_val = pd.DataFrame(y_val, columns=["TARGET", "index"]).set_index("index")
        y_pred.index = y_val.index

    prediction = pd.concat([y_val, y_pred], axis=1)

    # Unscale the data
    if (
        model.need_scaling
        and model.target_type == "regression"
        and model.scaler_y is not None
    ):
        # scaler_y needs 2D array with shape (-1, 1)
        prediction.loc[:, "TARGET"] = model.scaler_y.inverse_transform(
            prediction[["TARGET"]].values
        )
        prediction.loc[:, "PRED"] = model.scaler_y.inverse_transform(
            prediction[["PRED"]].values
        )

    # Evaluate model
    score = {
        "DATE": datetime.now(),
        "MODEL_NAME": model.model_name,
        "TYPE": type_name,
        "TRAINING_TIME": stop - start,
        "EVAL_DATA_STD": prediction["TARGET"].std(),
    }

    score.update(evaluate(prediction, target_type, target_clf_thresholds))

    metric = "RMSE" if target_type == "regression" else "LOGLOSS"
    logger.info(f"{model.model_name} scores on validation set: {score[metric]:.4f}")

    if type_name == "hyperopts":
        session.report(metrics=score)
        return score

    return score, model, prediction


class ModelSelectionEngine:

    def __init__(
        self,
        data,
        reshaped_data,
        target_number,
        target_clf,
        experiment,
        models_idx,
        time_series,
        date_column,
        group_column,
        target_clf_thresholds,
        **kwargs,
    ):
        self.data = data
        self.reshaped_data = reshaped_data
        self.target_number = target_number
        self.experiment = experiment
        self.target_clf = target_clf
        self.models_idx = models_idx
        self.time_series = time_series
        self.date_column = date_column
        self.group_column = group_column
        self.target_clf_thresholds = (
            target_clf_thresholds[target_number]
            if target_number in target_clf_thresholds.keys()
            else None
        )

        self.target_type = (
            "classification" if self.target_number in self.target_clf else "regression"
        )
        self.experiment_dir = self.experiment.path
        self.experiment_id = self.experiment.id
        self.data_dir = f"{self.experiment_dir}/data"
        self.preprocessing_dir = f"{self.experiment_dir}/preprocessing"
        self.target_dir = f"{self.experiment_dir}/TARGET_{self.target_number}"
        self.metric = "RMSE" if self.target_type == "regression" else "LOGLOSS"
        self.features = self.experiment.get_features(self.target_number)
        self.all_features = self.experiment.get_all_features(
            date_column=self.date_column, group_column=self.group_column
        )

    # Main training function
    def run(
        self,
        experiment_name,
        perform_hyperopt=True,
        number_of_trials=20,
        perform_crossval=False,
        plot=True,
        clean_dir=False,  # TODO: This has been unused because now feature_selection is in the target directory
        preserve_model=True,
        best_params=None,
    ):
        """
        Selects the best models based on a target variable, optionally performing hyperparameter optimization
        and cross-validation, and manages outputs in a session-specific directory.
        """
        self.experiment_name = experiment_name
        self.plot = plot
        self.number_of_trials = number_of_trials

        if self.experiment_id is None:
            raise ValueError("Please provide a experiment.")

        if self.data:
            train = self.data["train"]
            val = self.data["val"]
            test = self.data["test"]
            train_scaled = self.data["train_scaled"]
            val_scaled = self.data["val_scaled"]
            test_scaled = self.data["test_scaled"]
        else:
            (
                train,
                val,
                test,
                train_scaled,
                val_scaled,
                test_scaled,
            ) = load_train_data(
                self.experiment_dir, self.target_number, self.target_clf
            )

        if (
            any(all_models[i].get("recurrent") for i in self.models_idx)
            and not self.time_series
        ):
            ValueError(
                "You need to set time_series to true to use recurrent model, or remove recurrent models from models_idx chosen"
            )

        if (
            any(all_models[i].get("recurrent") for i in self.models_idx)
            and self.time_series
        ):
            if self.reshaped_data is None:
                raise ValueError("reshaped_data is not provided.")

            logger.info("Loading reshaped data...")
            x_train_reshaped = self.reshaped_data["x_train_reshaped"]
            y_train_reshaped = self.reshaped_data["y_train_reshaped"]
            x_val_reshaped = self.reshaped_data["x_val_reshaped"]
            y_val_reshaped = self.reshaped_data["y_val_reshaped"]
            x_test_reshaped = self.reshaped_data["x_test_reshaped"]
            y_test_reshaped = self.reshaped_data["y_test_reshaped"]

        # create model selection in db
        target = Target.find_by(name=f"TARGET_{self.target_number}")
        model_selection = ModelSelection.upsert(
            match_fields=["target_id", "experiment_id"],
            target_id=target.id,
            experiment_id=self.experiment_id,
        )

        # recurrent models starts at 9 # len(list_models)
        for i in self.models_idx:
            config = all_models[i]
            recurrent = config["recurrent"]
            need_scaling = config["need_scaling"]
            model_name = config["model_name"]

            if recurrent is False and config[self.target_type] is None:
                continue  # for naive bayes models that cannot be used in regression

            self.results_dir = f"{self.target_dir}/{model_name}"
            if not os.path.exists(f"{self.results_dir}"):
                os.makedirs(f"{self.results_dir}")
            elif preserve_model and contains_best(self.results_dir):
                continue
            elif perform_hyperopt:
                clean_directory(self.results_dir)

            logger.info(f"Training a {model_name}")
            model = Model.upsert(
                match_fields=["name", "type"],
                name=model_name,
                type=self.target_type,
            )
            model_training = ModelTraining.upsert(
                match_fields=["model_id", "model_selection_id"],
                model_id=model.id,
                model_selection_id=model_selection.id,
            )

            # getting data
            if recurrent:
                # Clear cluster from previous Keras session graphs.
                K.clear_session()

                features_idx = [
                    i
                    for i, e in enumerate(self.all_features)
                    if e in set(self.features)
                ]
                # TODO: Verify that features_idx are the right one, because scaling can re-arrange columns...
                x_train = x_train_reshaped[:, :, features_idx]
                y_train = y_train_reshaped[:, [self.target_number, 0]]
                x_val = x_val_reshaped[:, :, features_idx]
                y_val = y_val_reshaped[:, [self.target_number, 0]]
                x_test = x_test_reshaped[:, :, features_idx]
                y_test = y_test_reshaped[:, [self.target_number, 0]]
            else:
                config = config[self.target_type]

                if need_scaling and self.target_type == "regression":
                    x_train = train_scaled[self.features]
                    y_train = train_scaled[f"TARGET_{self.target_number}"].rename(
                        "TARGET"
                    )
                    x_val = val_scaled[self.features]
                    y_val = val_scaled[f"TARGET_{self.target_number}"].rename("TARGET")
                    x_test = test_scaled[self.features]
                    y_test = test_scaled[f"TARGET_{self.target_number}"].rename(
                        "TARGET"
                    )
                else:
                    x_train = train[self.features]
                    y_train = train[f"TARGET_{self.target_number}"].rename("TARGET")
                    x_val = val[self.features]
                    y_val = val[f"TARGET_{self.target_number}"].rename("TARGET")
                    x_test = test[self.features]
                    y_test = test[f"TARGET_{self.target_number}"].rename("TARGET")

            log_dir = get_log_dir(self.target_dir, model_name)
            # instantiate model
            model = ModelEngine(
                target_number=self.target_number,
                model_name=model_name,
                search_params=config["search_params"],
                target_type=self.target_type,
                create_model=config["create_model"],
                plot=self.plot,
                log_dir=log_dir,
            )

            start = time.time()
            # Tuning hyperparameters
            if perform_hyperopt:
                model_best_params = self.hyperoptimize(
                    x_train, y_train, x_val, y_val, model
                )
            elif best_params:
                model_best_params = best_params[model_name]
            else:
                try:
                    with open(f"{self.target_dir}/best_params.json") as f:
                        json_dict = json.load(f)
                        model_best_params = json_dict[model_name]
                except Exception:
                    raise FileNotFoundError(
                        f"Could not find {model_name} in current data. Try to run an hyperoptimization by setting `perform_hyperopt` to true, or pass `best_params`"
                    )

            # save best params
            best_params_file = f"{self.target_dir}/best_params.json"
            try:
                with open(best_params_file, "r") as f:
                    json_dict = json.load(f)
            except FileNotFoundError:
                json_dict = {}

            json_dict[model.model_name] = serialize_for_json(model_best_params)
            with open(best_params_file, "w") as f:
                json.dump(json_dict, f, indent=4)

            # Perform cross-validation of the best model on k-folds of train + val set
            if perform_crossval:
                x_train_val = pd.concat([x_train, x_val, x_test], axis=0)
                y_train_val = pd.concat([y_train, y_val, y_test], axis=0)
                n_splits = 4
                n_samples = len(x_train_val)
                test_size = int(n_samples / (n_splits + 4))
                tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)

                # Store the scores
                cv_scores = []

                for i, (train_index, val_index) in enumerate(tscv.split(x_train_val)):
                    self.type_name = f"crossval_fold_{i}"

                    if self.time_series:
                        date_series = pd.concat(
                            [
                                train[self.date_column],
                                val[self.date_column],
                                test[self.date_column],
                            ],
                            axis=0,
                        ).reset_index(drop=True)

                        date_series = date_series.map(pd.Timestamp.fromordinal)

                        # Now you can use the actual train/val indices to extract ranges
                        train_start = date_series.iloc[train_index[0]]
                        train_end = date_series.iloc[train_index[-1]]
                        val_start = date_series.iloc[val_index[0]]
                        val_end = date_series.iloc[val_index[-1]]

                        logger.info(
                            f"[Fold {i}] Train: {len(train_index)} samples from {train_start.date()} to {train_end.date()} | "
                            f"Validation: {len(val_index)} samples from {val_start.date()} to {val_end.date()}"
                        )
                    else:
                        logger.info(
                            f"[Fold {i}] Train: {len(train_index)} samples | Validation: {len(val_index)} samples"
                        )

                    # Train the model and get the score
                    if recurrent:
                        cv_score, _, _ = self.train_model(
                            params=model_best_params,
                            x_train=x_train_val[train_index],
                            y_train=y_train_val[train_index],
                            x_val=x_train_val[val_index],
                            y_val=y_train_val[val_index],
                            model=model,
                        )
                    else:
                        cv_score, _, _ = self.train_model(
                            params=model_best_params,
                            x_train=x_train_val.iloc[train_index],
                            y_train=y_train_val.iloc[train_index],
                            x_val=x_train_val.iloc[val_index],
                            y_val=y_train_val.iloc[val_index],
                            model=model,
                        )

                    # Append score to the list
                    cv_scores.append(cv_score)

                # Calculate mean of all numerical metrics across all cross-validation folds
                cv_scores_df = pd.DataFrame(cv_scores)
                # Get mean of all numeric columns
                cv_means = cv_scores_df.mean(numeric_only=True).to_dict()

                logger.info(f"👉 {model.model_name} mean cv scores on full dataset:")
                for metric, value in cv_means.items():
                    logger.info(f"  {metric}: {value:.4f}")

                # Retrain on entire training set, but keep score on cross-validation folds
                # Get the test score using the best model
                test_score, best_model, best_pred = self.train_model(
                    params=model_best_params,
                    x_train=pd.concat([x_train, x_val], axis=0),
                    y_train=pd.concat([y_train, y_val], axis=0),
                    x_val=x_test,
                    y_val=y_test,
                    model=model,
                )

                # Update all metrics with cross-validation means
                for metric, value in cv_means.items():
                    if metric in test_score:  # Only update existing metrics
                        test_score[metric] = value
                best_score = test_score
                best_score["TYPE"] = "crossval"
            else:
                # Evaluate on test set
                self.type_name = "testset"
                best_score, best_model, best_pred = self.train_model(
                    params=model_best_params,
                    x_train=pd.concat([x_train, x_val], axis=0),
                    y_train=pd.concat([y_train, y_val], axis=0),
                    x_val=x_test,
                    y_val=y_test,
                    model=model,
                )

                logger.info(f"👉 {model.model_name} scores on test set:")
                for metric, value in best_score.items():
                    if isinstance(value, (int, float)):
                        logger.info(f"  {metric}: {value:.4f}")

            # Save predictions
            best_pred.to_csv(
                f"{self.results_dir}/prediction.csv",
                index=True,
                header=True,
                index_label="ID",
            )

            # Save best model
            model_path = best_model.save(self.results_dir)

            model_path = Path(model_path).resolve()
            best_score["MODEL_PATH"] = model_path

            # Save best scores
            scores_tracking_path = f"{self.target_dir}/scores_tracking.csv"
            best_score_df = pd.DataFrame([best_score])

            if os.path.exists(scores_tracking_path):
                existing_scores = pd.read_csv(scores_tracking_path)
                common_cols = existing_scores.columns.intersection(
                    best_score_df.columns
                )
                best_score_df = best_score_df[common_cols]
                scores_tracking = pd.concat(
                    [existing_scores, best_score_df], ignore_index=True
                )
            else:
                scores_tracking = best_score_df

            scores_tracking.sort_values(self.metric, ascending=True, inplace=True)
            scores_tracking.to_csv(scores_tracking_path, index=False)

            # Save model training metadata
            stop = time.time()
            training_time = stop - start
            model_training.best_params = model_best_params
            model_training.model_path = model_path
            model_training.training_time = training_time
            model_training.save()

            # Store metrics in DB
            drop_cols = [
                "DATE",
                "MODEL_NAME",
                "MODEL_PATH",
            ]
            best_score = {k: v for k, v in best_score.items() if k not in drop_cols}
            score_data = {k.lower(): v for k, v in best_score.items()}

            Score.upsert(
                match_fields=["model_training_id"],
                model_training_id=model_training.id,
                **score_data,
            )

            logger.info(f"Model training finished in {training_time:.2f} seconds")

        # find best model type
        scores_tracking_path = f"{self.target_dir}/scores_tracking.csv"
        scores_tracking = pd.read_csv(scores_tracking_path)
        best_score_overall = scores_tracking.iloc[0, :]
        best_model_name = best_score_overall["MODEL_NAME"]
        if self.target_type == "classification":
            best_thresholds = best_score_overall["THRESHOLDS"]
            joblib.dump(best_thresholds, f"{self.target_dir}/thresholds.pkl")
        else:
            best_thresholds = None

        # Remove any .best or .keras files
        for file_path in glob.glob(os.path.join(self.target_dir, "*.best")) + glob.glob(
            os.path.join(self.target_dir, "*.keras")
        ):
            os.remove(file_path)
        # Copy the best model in root training folder for this target
        best_model_path = Path(
            f"{self.target_dir}/{os.path.basename(best_score_overall['MODEL_PATH'])}"
        ).resolve()
        copy_any(
            best_score_overall["MODEL_PATH"],
            best_model_path,
        )

        with open(f"{self.target_dir}/best_params.json", "r") as f:
            best_model_params = json.load(f)[best_model_name]

        # Save model_selection results to db
        model_selection = ModelSelection.get(model_selection.id)
        model_selection.best_model_id = Model.find_by(
            name=best_score_overall["MODEL_NAME"], type=self.target_type
        ).id
        model_selection.best_model_params = best_model_params
        model_selection.best_thresholds = best_thresholds
        model_selection.best_model_path = best_model_path
        model_selection.save()

        logger.info(f"Best model overall is : {best_score_overall}")

        # Consolidate best parameters from all targets into a single file
        self.consolidate_best_params()

        best_model = joblib.load(best_model_path)
        return best_model

    def hyperoptimize(self, x_train, y_train, x_val, y_val, model: ModelEngine):
        self.type_name = "hyperopts"

        def collect_error_logs(target_dir: int, storage_path: str):
            output_error_file = f"{target_dir}/errors.log"

            with open(output_error_file, "a") as outfile:
                # Walk through the ray_results directory
                for root, dirs, files in os.walk(storage_path):
                    # Check if 'error.txt' exists in the current directory
                    if "error.txt" in files:
                        error_file_path = os.path.join(root, "error.txt")
                        logger.info(f"Processing error file: {error_file_path}")
                        # Read and append the content of the error.txt file
                        with open(error_file_path, "r") as infile:
                            outfile.write(f"\n\n=== Error from {error_file_path} ===\n")
                            outfile.write(infile.read())
            logger.info(f"All errors written to {output_error_file}")

        logger.info("Start tuning hyperparameters...")

        storage_path = f"{self.results_dir}/ray_results"

        # Initialize Ray with the runtime environment
        ray.init(
            runtime_env={
                "excludes": [
                    ".git/**/*",
                    "**/*.pyc",
                    "**/__pycache__",
                    "**/data/*",
                    "**/notebooks/*",
                    "**/tests/*",
                    "**/docs/*",
                    "**/.pytest_cache/*",
                    "**/venv/*",
                    "**/.venv/*",
                    "**/build/*",
                    "**/dist/*",
                    "**/*.egg-info/*",
                ]
            }
        )

        tuner = Tuner(
            trainable=with_parameters(
                trainable,
                x_train=x_train,
                y_train=y_train,
                x_val=x_val,
                y_val=y_val,
                model_name=model.model_name,
                target_type=self.target_type,
                experiment_name=self.experiment_name,
                target_number=self.target_number,
                create_model=model.create_model,
                type_name="hyperopts",
                plot=model.plot,
                log_dir=model.log_dir,
                target_clf_thresholds=self.target_clf_thresholds,
            ),
            param_space=model.search_params,
            tune_config=TuneConfig(
                metric=self.metric,
                mode="min",
                search_alg=HyperOptSearch(),
                num_samples=self.number_of_trials,
                scheduler=ASHAScheduler(max_t=100, grace_period=10),
            ),
            run_config=RunConfig(
                stop={"training_iteration": 100},
                storage_path=storage_path,
                callbacks=[TBXLoggerCallback()],
            ),
        )
        try:
            results = tuner.fit()

            best_result = results.get_best_result(self.metric, "min")
            best_params = best_result.config
            best_score = best_result.metrics

            # log results
            logger.info(f"Best hyperparameters found were:\n{best_params}")
            logger.info(f"Best Scores found were:\n{best_score}")
            logger.info(
                f"Markdown table with all trials :\n{results.get_dataframe().to_markdown()}"
            )
            # Collect errors in single file
            collect_error_logs(target_dir=self.target_dir, storage_path=storage_path)

        except Exception as e:
            raise Exception(e)

        finally:
            ray.shutdown()

        return best_params

    def train_model(self, params, x_train, y_train, x_val, y_val, model: ModelEngine):
        # Use the standalone training function to avoid duplication
        # For train_model, we pass the data directly (not as Ray references)
        return trainable(
            params,
            x_train,
            y_train,
            x_val,
            y_val,
            model.model_name,
            self.target_type,
            self.experiment_name,
            self.target_number,
            model.create_model,
            self.type_name,
            model.plot,
            log_dir=model.log_dir,
            target_clf_thresholds=self.target_clf_thresholds,
        )

    def consolidate_best_params(self):
        """
        Consolidate best parameters from all targets into a single JSON file in the preprocessing folder.
        The output will be a dictionary with target numbers as keys and their best parameters as values.
        """
        # Initialize the consolidated parameters dictionary
        all_best_params = {}

        # Find all target directories
        target_dirs = [
            d for d in os.listdir(self.experiment_dir) if d.startswith("TARGET_")
        ]

        for target_dir in target_dirs:
            target_number = target_dir.split("_")[1]
            best_params_file = os.path.join(
                self.experiment_dir, target_dir, "best_params.json"
            )

            # Check if best_params.json exists for this target
            if os.path.exists(best_params_file):
                try:
                    with open(best_params_file, "r") as f:
                        target_params = json.load(f)
                        all_best_params[int(target_number)] = target_params
                except Exception as e:
                    logger.warning(
                        f"Error loading best params for {target_dir}: {str(e)}"
                    )

        # Save consolidated parameters to preprocessing folder
        if all_best_params:
            output_file = os.path.join(
                self.preprocessing_dir, "all_targets_best_params.json"
            )
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(all_best_params, f, indent=4)
            logger.info(f"Consolidated best parameters saved to {output_file}")

        return all_best_params


def evaluate(
    prediction: pd.DataFrame,
    target_type: str,
    target_clf_thresholds: dict = None,
):
    """
    Function to evaluate model performance

    Args:
        - prediction: the prediction dataframe containing TARGET and PRED columns, as well as predicted probablities for each class for classification tasks
        - target_type: classification or regression
        - target_clf_thresholds: thresholds for classification tasks like {"recall": 0.9} or {"precision": 0.9}
    """
    score = {}
    y_true = prediction["TARGET"]
    y_pred = prediction["PRED"]

    # Set default threshold if not provided
    if target_clf_thresholds is None:
        target_clf_thresholds = {"precision": 0.80}

    if target_type == "regression":
        # Main metrics
        score["RMSE"] = root_mean_squared_error(y_true, y_pred)
        score["MAE"] = mean_absolute_error(y_true, y_pred)
        score["MAPE"] = mean_absolute_percentage_error(y_true, y_pred)
        score["R2"] = r2_score(y_true, y_pred)

        # Robustness: avoid division by zero
        std_target = y_true.std()
        mean_target = y_true.mean()
        median_target = y_true.median()

        # RMSE / STD
        score["RMSE_STD_RATIO"] = (
            float(100 * score["RMSE"] / std_target) if std_target else 1000
        )

        # Median absolute deviation (MAD)
        mam = (y_true - mean_target).abs().median()  # Median Abs around Mean
        mad = (y_true - median_target).abs().median()  # Median Abs around Median
        score["MAM"] = mam
        score["MAD"] = mad
        score["MAE_MAM_RATIO"] = (
            float(100 * score["MAE"] / mam) if mam else 1000
        )  # MAE / MAD → Plus stable, moins sensible aux outliers.
        score["MAE_MAD_RATIO"] = (
            float(100 * score["MAE"] / mad) if mad else 1000
        )  # MAE / Médiane des écarts absolus autour de la moyenne: Moins robuste aux outliers

    else:

        labels = np.unique(y_true)
        num_classes = labels.size
        y_pred_proba = (
            prediction[1] if num_classes == 2 else prediction.iloc[:, 2:].values
        )
        if num_classes > 2:
            lb = LabelBinarizer(sparse_output=False)  # Change to True for sparse matrix
            lb.fit(labels)
            y_true_onhot = lb.transform(y_true)
            y_pred_onehot = lb.transform(y_pred)

        score["LOGLOSS"] = log_loss(y_true, y_pred_proba)
        score["ACCURACY"] = accuracy_score(y_true, y_pred)
        score["PRECISION"] = precision_score(
            y_true,
            y_pred,
            average=("binary" if num_classes == 2 else "macro"),
        )
        score["RECALL"] = recall_score(
            y_true,
            y_pred,
            average=("binary" if num_classes == 2 else "macro"),
        )
        score["F1"] = f1_score(
            y_true,
            y_pred,
            average=("binary" if num_classes == 2 else "macro"),
        )
        score["ROC_AUC"] = float(roc_auc_score(y_true, y_pred_proba, multi_class="ovr"))

        # Store the complete thresholds dictionary
        if len(target_clf_thresholds.keys()) > 1:
            raise ValueError(
                f"Only one metric can be specified for threshold optimization. found {target_clf_thresholds.keys()}"
            )
        # Get the single key-value pair or use defaults
        metric, value = (
            next(iter(target_clf_thresholds.items()))
            if target_clf_thresholds
            else ("precision", 0.8)
        )

        score["THRESHOLDS"] = find_best_threshold(prediction, metric, value)

        # Collect valid metrics across all classes (works for both binary and multiclass)
        valid_metrics = [
            m for m in score["THRESHOLDS"].values() if m["threshold"] is not None
        ]

        if valid_metrics:
            score["PRECISION_AT_THRESHOLD"] = np.mean(
                [m["precision"] for m in valid_metrics]
            )
            score["RECALL_AT_THRESHOLD"] = np.mean([m["recall"] for m in valid_metrics])
            score["F1_AT_THRESHOLD"] = np.mean([m["f1"] for m in valid_metrics])
        else:
            score["PRECISION_AT_THRESHOLD"] = None
            score["RECALL_AT_THRESHOLD"] = None
            score["F1_AT_THRESHOLD"] = None

    return score


# utils
def get_log_dir(target_dir: str, model_name="test_model"):
    """Generates a structured log directory path for TensorBoard."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_dir = Path(target_dir + "/tensorboard") / model_name / f"run_{timestamp}"
    log_dir.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
    return str(log_dir)


def load_model(target_dir: str):
    target_dir = Path(target_dir)
    # Search for files that contain '.best' or '.keras' in the name
    best_files = list(target_dir.glob("*.best*")) + list(target_dir.glob("*.keras*"))
    # If any files are found, try loading the first one (or process as needed)
    if best_files:
        file_path = best_files[0]  # Assuming you want to open the first matching file
        try:
            # Attempt to load the file as a scikit-learn, XGBoost, or LightGBM model (Pickle format)
            return joblib.load(file_path)
        except (pickle.UnpicklingError, EOFError):
            # If it's not a pickle file, try loading it as a Keras model
            try:
                # Attempt to load the file as a Keras model
                return keras.models.load_model(file_path)
            except Exception as e:
                raise FileNotFoundError(
                    f"Model could not be loaded from path: {file_path}: {e}"
                )
    else:
        raise FileNotFoundError(
            f"No files with '.best' or '.keras' found in the specified folder: {target_dir}"
        )


def plot_training_progress(
    logs, model_name, target_number, title_suffix="Training Progress"
):
    """
    Plot training and validation metrics during model training.

    Args:
        logs: DataFrame or dict containing training history
        model_name: Name of the model being trained
        target_number: Target number for the model
        title_suffix: Optional suffix for the plot title
    """
    if isinstance(logs, dict):
        logs = pd.DataFrame(logs)

    plt.figure(figsize=(14, 4))

    # Plot all metrics that exist in the logs
    if "loss" in logs.columns:
        plt.plot(logs["loss"], lw=2, label="Training loss")
    if "val_loss" in logs.columns:
        plt.plot(logs["val_loss"], lw=2, label="Validation loss")

    # If no specific loss columns, plot all available metrics
    if "loss" not in logs.columns and "val_loss" not in logs.columns and not logs.empty:
        for col in logs.columns:
            if col.startswith("val_"):
                plt.plot(logs[col], "--", lw=2, label=f"Validation {col[4:]}")
            else:
                plt.plot(logs[col], lw=2, label=f"Training {col}")

    plt.title(f"{model_name} - Target {target_number}\n{title_suffix}")
    plt.xlabel("Epoch")
    plt.ylabel("Metric Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


# plots
def plot_evaluation_for_classification(prediction: dict):
    """
    Plot evaluation metrics for classification tasks (both binary and multiclass).

    Args:
        prediction (pd.DataFrame): Should be a df with:
            - TARGET: true labels
            - PRED: predicted labels
            - For binary: column '1' or 1 for positive class probabilities
            - For multiclass: columns 2 onwards for class probabilities
    """
    y_true = prediction["TARGET"]
    y_pred = prediction["PRED"]

    # Plot confusion matrix
    plot_confusion_matrix(y_true, y_pred)

    # Determine if binary or multiclass
    unique_labels = np.unique(y_true)
    unique_labels = np.sort(unique_labels)
    n_classes = len(unique_labels)

    if n_classes <= 2:
        # Binary classification
        y_pred_proba = prediction[1] if 1 in prediction.columns else prediction["1"]

        # Compute and plot ROC curve
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(8, 8))
        plt.plot(
            fpr,
            tpr,
            color="darkorange",
            lw=2,
            label=f"ROC curve (area = {roc_auc:0.2f})",
        )
        plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend(loc="lower right")
        plt.show()

        # Compute and plot precision-recall curve
        precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
        average_precision = average_precision_score(y_true, y_pred_proba)

        plt.figure(figsize=(8, 8))
        plt.step(recall, precision, color="b", alpha=0.2, where="post")
        plt.fill_between(recall, precision, step="post", alpha=0.2, color="b")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title(f"Precision-Recall Curve: AP={average_precision:0.2f}")
        plt.show()

    else:
        # Multiclass classification
        # Get class probabilities
        pred_cols = [
            col for col in prediction.columns if col not in ["ID", "TARGET", "PRED"]
        ]
        y_pred_proba = prediction[pred_cols].values

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()

        plt.figure(figsize=(10, 8))
        colors = plt.cm.get_cmap("tab10")(np.linspace(0, 1, n_classes))

        for i, (label, color) in enumerate(zip(unique_labels, colors)):
            y_true_binary = (y_true == label).astype(int)
            y_score = y_pred_proba[:, i]

            fpr[i], tpr[i], _ = roc_curve(y_true_binary, y_score)
            roc_auc[i] = auc(fpr[i], tpr[i])

            plt.plot(
                fpr[i],
                tpr[i],
                color=color,
                lw=2,
                label=f"Class {label} (area = {roc_auc[i]:0.2f})",
            )

        plt.plot([0, 1], [0, 1], "k--", lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Multiclass ROC Curves (One-vs-Rest)")
        plt.legend(loc="lower right")
        plt.show()

        # Compute PR curve for each class
        plt.figure(figsize=(10, 8))

        for i, (label, color) in enumerate(zip(unique_labels, colors)):
            y_true_binary = (y_true == label).astype(int)
            y_score = y_pred_proba[:, i]

            precision, recall, _ = precision_recall_curve(y_true_binary, y_score)
            average_precision = average_precision_score(y_true_binary, y_score)

            plt.step(
                recall,
                precision,
                color=color,
                alpha=0.8,
                where="post",
                label=f"Class {label} (AP = {average_precision:0.2f})",
            )

        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title("Multiclass Precision-Recall Curves")
        plt.legend(loc="lower left")
        plt.show()


def plot_confusion_matrix(y_true, y_pred):
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Get unique, sorted class labels
    labels = np.unique(np.concatenate((y_true, y_pred)))
    labels = np.sort(labels)

    # Calculate class distribution
    class_dist = np.bincount(y_true.astype(int))
    class_dist_pct = class_dist / len(y_true) * 100

    # Create figure with two subplots stacked vertically
    fig = plt.figure(figsize=(10, 12))

    # Subplot 1: Confusion Matrix
    ax1 = plt.subplot(2, 1, 1)  # Changed to 2 rows, 1 column, first subplot

    # Create a custom colormap (blue to white to red)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Plot heatmap with better styling
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap=cmap,
        center=0,
        linewidths=0.5,
        linecolor="lightgray",
        cbar_kws={"label": "Number of Samples"},
        ax=ax1,
    )

    # Add title and labels with better styling
    ax1.set_title("Confusion Matrix", fontsize=14, pad=20, weight="bold")
    ax1.set_xlabel("Predicted Label", fontsize=12, labelpad=10)
    ax1.set_ylabel("True Label", fontsize=12, labelpad=10)

    # Set tick labels to be centered and more readable
    ax1.set_xticks(np.arange(len(labels)) + 0.5)
    ax1.set_yticks(np.arange(len(labels)) + 0.5)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_yticklabels(labels, fontsize=10, rotation=0)

    # Add grid lines for better readability
    ax1.set_xticks(np.arange(len(labels) + 1) - 0.5, minor=True)
    ax1.set_yticks(np.arange(len(labels) + 1) - 0.5, minor=True)
    ax1.grid(which="minor", color="w", linestyle="-", linewidth=2)
    ax1.tick_params(which="minor", bottom=False, left=False)

    # Subplot 2: Class Distribution
    ax2 = plt.subplot(2, 1, 2)  # Changed to 2 rows, 1 column, second subplot

    # Create a bar plot for class distribution
    bars = ax2.bar(
        labels.astype(str),
        class_dist_pct,
        color=sns.color_palette("viridis", len(labels)),
    )

    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Add title and labels
    ax2.set_title("Class Distribution", fontsize=14, pad=20, weight="bold")
    ax2.set_xlabel("Class", fontsize=12, labelpad=10)
    ax2.set_ylabel("Percentage of Total Samples", fontsize=12, labelpad=10)
    ax2.set_ylim(0, 100)
    ax2.grid(axis="y", linestyle="--", alpha=0.7)

    # Add total count annotation
    total = len(y_true)
    ax2.text(
        0.5,
        -0.15,  # Adjusted y-position for better spacing
        f"Total samples: {total:,}",
        transform=ax2.transAxes,
        ha="center",
        fontsize=10,
        bbox=dict(
            facecolor="white",
            alpha=0.8,
            edgecolor="lightgray",
            boxstyle="round,pad=0.5",
        ),
    )

    # Adjust layout to prevent overlap with more vertical space
    plt.tight_layout(rect=[0, 0.03, 1, 0.98])
    plt.show()


class Threshold(BaseModel):
    threshold: float
    precision: float
    recall: float
    f1: float


class Thresholds(BaseModel):
    thresholds: dict[str, Threshold]


def find_best_threshold(
    prediction: pd.DataFrame, metric: str = "recall", target_value: float | None = None
) -> Thresholds:
    """
    General function to find best threshold optimizing recall, precision, or f1.

    Supports both binary and multiclass classification.

    Parameters:
    - prediction (pd.DataFrame): must contain 'TARGET' and class probability columns.
    - metric (str): 'recall', 'precision', or 'f1'.
    - target_value (float | None): minimum acceptable value for the chosen metric.

    Returns:
    - Thresholds: {class_label: {'threshold', 'precision', 'recall', 'f1'}}
    """
    assert metric in {"recall", "precision", "f1"}, "Invalid metric"
    y_true = prediction["TARGET"]
    pred_cols = [
        col for col in prediction.columns if col not in ["ID", "TARGET", "PRED"]
    ]
    classes = [1] if len(pred_cols) <= 2 else sorted(y_true.unique())

    results = {}
    for cls in classes:
        cls_str = str(cls)
        if cls_str not in prediction.columns and cls not in prediction.columns:
            logger.warning(f"Missing predicted probabilities for class '{cls}'")
            results[cls_str] = {
                "threshold": None,
                "precision": None,
                "recall": None,
                "f1": None,
            }
            continue

        # Binarize for one-vs-rest
        y_binary = (y_true == int(cls)).astype(int)
        y_scores = prediction[cls] if cls in prediction.columns else prediction[cls_str]

        precision, recall, thresholds = precision_recall_curve(y_binary, y_scores)
        precision, recall = precision[1:], recall[1:]  # Align with thresholds
        thresholds = thresholds

        f1 = 2 * (precision * recall) / (precision + recall + 1e-10)

        metric_values = {"precision": precision, "recall": recall, "f1": f1}

        values = metric_values[metric]

        if target_value is not None:
            if metric == "recall":
                # Only keep recall >= target
                valid_indices = [i for i, r in enumerate(recall) if r >= target_value]
                if valid_indices:
                    # Pick the highest threshold
                    best_idx = max(valid_indices, key=lambda i: thresholds[i])
                else:
                    logger.warning(
                        f"[Class {cls}] No threshold with recall ≥ {target_value}"
                    )
                    best_idx = int(np.argmax(recall))  # fallback

            elif metric == "precision":
                # Only keep precision ≥ target and recall > 0
                valid_indices = [
                    i
                    for i, (p, r) in enumerate(zip(precision, recall))
                    if p >= target_value and r > 0
                ]
                if valid_indices:
                    # Among valid ones, pick the one with highest recall
                    best_idx = max(valid_indices, key=lambda i: recall[i])
                else:
                    logger.warning(
                        f"[Class {cls}] No threshold with precision ≥ {target_value}"
                    )
                    best_idx = int(np.argmax(precision))  # fallback

            elif metric == "f1":
                valid_indices = [i for i, val in enumerate(f1) if val >= target_value]
                if valid_indices:
                    best_idx = max(valid_indices, key=lambda i: f1[i])
                else:
                    logger.warning(
                        f"[Class {cls}] No threshold with f1 ≥ {target_value}"
                    )
                    best_idx = int(np.argmax(f1))  # fallback
        else:
            best_idx = int(np.argmax(values))  # no constraint, get best value

        results[cls_str] = {
            "threshold": float(thresholds[best_idx]),
            "precision": float(precision[best_idx]),
            "recall": float(recall[best_idx]),
            "f1": float(f1[best_idx]),
        }

    return results


def apply_thresholds(
    pred_proba: pd.DataFrame, threshold: Thresholds | float, classes
) -> pd.DataFrame:
    """
    Apply thresholds to predicted probabilities.

    Parameters:
    - pred_proba (pd.DataFrame): Probabilities per class.
    - threshold (Thresholds | float): Global threshold (float) or per-class dict from `find_best_threshold`.
    - classes (iterable): List or array of class labels (used for binary classification).

    Returns:
    - pd.DataFrame with "PRED" column and original predicted probabilities.
    """

    # Case 1: Per-class thresholds
    if isinstance(threshold, dict):
        class_predictions = []
        class_probabilities = []

        for class_label, metrics in threshold.items():
            # Get threshold from structured dict
            _threshold = (
                metrics.get("threshold") if isinstance(metrics, dict) else metrics[0]
            )
            if _threshold is not None:
                if class_label not in pred_proba.columns:
                    continue  # skip missing class
                col = pred_proba[class_label]
                exceeded = col >= _threshold
                class_predictions.append(
                    pd.Series(
                        np.where(exceeded, class_label, -1), index=pred_proba.index
                    )
                )
                class_probabilities.append(
                    pd.Series(np.where(exceeded, col, -np.inf), index=pred_proba.index)
                )

        # For each row:
        # 1. If any threshold is exceeded, take the class with highest probability among exceeded
        # 2. If no threshold is exceeded, take the class with highest probability overall
        if class_predictions:
            preds_df = pd.concat(class_predictions, axis=1)
            probs_df = pd.concat(class_probabilities, axis=1)

            def select_class(row_pred, row_prob, row_orig):
                exceeded = row_pred >= 0
                if exceeded.any():
                    return row_pred.iloc[row_prob.argmax()]
                return row_orig.idxmax()

            pred = pd.Series(
                [
                    select_class(
                        preds_df.loc[idx], probs_df.loc[idx], pred_proba.loc[idx]
                    )
                    for idx in pred_proba.index
                ],
                index=pred_proba.index,
                name="PRED",
            )
        else:
            # fallback: take max probability if no thresholds apply
            pred = pred_proba.idxmax(axis=1).rename("PRED")

    # Case 2: Global scalar threshold (e.g., 0.5 for binary)
    else:
        if len(classes) == 2:
            # Binary classification: threshold on positive class
            pos_class = classes[1]
            pred = (pred_proba[pos_class] >= threshold).astype(int).rename("PRED")
        else:
            # Multiclass: default to max probability
            pred = pred_proba.idxmax(axis=1).rename("PRED")

    return pd.concat([pred, pred_proba], axis=1)


def plot_threshold(prediction, threshold, precision, recall):
    y_pred_proba = prediction[1] if 1 in prediction.columns else prediction["1"]
    y_true = prediction["TARGET"]

    predicted_positive = (y_pred_proba >= threshold).sum()
    predicted_negative = (y_pred_proba < threshold).sum()
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
    per_predicted_positive = predicted_positive / len(y_pred_proba)
    per_predicted_negative = predicted_negative / len(y_pred_proba)

    print(
        f"""Threshold: {threshold*100:.2f}
        Precision: {precision*100:.2f}
        Recall: {recall*100:.2f}
        F1-score: {f1_scores*100:.2f}
        % of score over {threshold}: {predicted_positive}/{len(y_pred_proba)} = {per_predicted_positive*100:.2f}%
        % of score under {threshold}: {predicted_negative}/{len(y_pred_proba)} = {per_predicted_negative*100:.2f}%"""
    )

    # Visualizing the scores of positive and negative classes
    plt.figure(figsize=(10, 6))
    sns.histplot(
        y_pred_proba[y_true == 1],
        color="blue",
        label="Positive Class",
        bins=30,
        kde=True,
        alpha=0.6,
    )
    sns.histplot(
        y_pred_proba[y_true == 0],
        color="red",
        label="Negative Class",
        bins=30,
        kde=True,
        alpha=0.6,
    )
    plt.axvline(
        x=threshold,
        color="green",
        linestyle="--",
        label=f"Threshold at {round(threshold,3)}",
    )
    plt.title("Distribution of Predicted Probabilities")
    plt.xlabel("Predicted Probabilities")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()
    return threshold


# OLD - to sort out
def print_model_estimators(target_dir: str, model_name="linear"):
    """
    Look at a specific trained model
    """
    model = joblib.load(f"{target_dir}/{model_name}/{model_name}.best")
    for i in range(0, 100):
        logger.info(model.estimators_[i].get_depth())


def get_model_info(model):
    model.count_params()
    model.summary()
