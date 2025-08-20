import os
from pathlib import Path

import pandas as pd
import joblib

# Set up coverage file path
os.environ["COVERAGE_FILE"] = str(Path(".coverage").resolve())

# Internal imports
from lecrapaud.directories import tmp_dir
from lecrapaud.db import Experiment, Target
from lecrapaud.db.session import get_db


def create_experiment(
    data: pd.DataFrame | str,
    corr_threshold,
    percentile,
    max_features,
    date_column,
    group_column,
    experiment_name,
    **kwargs,
):
    if isinstance(data, str):
        path = f"{data}/data/full.pkl"
        data = joblib.load(path)

    dates = {}
    if date_column:
        dates["start_date"] = pd.to_datetime(data[date_column].iat[0])
        dates["end_date"] = pd.to_datetime(data[date_column].iat[-1])

    groups = {}
    if group_column:
        groups["number_of_groups"] = data[group_column].nunique()
        groups["list_of_groups"] = data[group_column].unique().tolist().sort()

    with get_db() as db:
        all_targets = Target.get_all(db=db)
        targets = [
            target for target in all_targets if target.name in data.columns.str.upper()
        ]
        experiment_name = f"{experiment_name}_{groups["number_of_groups"] if group_column else 'ng'}_{corr_threshold}_{percentile}_{max_features}_{dates['start_date'].date() if date_column else 'nd'}_{dates['end_date'].date() if date_column else 'nd'}"

        experiment_dir = f"{tmp_dir}/{experiment_name}"
        preprocessing_dir = f"{experiment_dir}/preprocessing"
        data_dir = f"{experiment_dir}/data"
        os.makedirs(preprocessing_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        experiment = Experiment.upsert(
            match_fields=["name"],
            db=db,
            name=experiment_name,
            path=Path(experiment_dir).resolve(),
            type="training",
            size=data.shape[0],
            corr_threshold=corr_threshold,
            percentile=percentile,
            max_features=max_features,
            **groups,
            **dates,
            targets=targets,
            context={
                "corr_threshold": corr_threshold,
                "percentile": percentile,
                "max_features": max_features,
                "date_column": date_column,
                "group_column": group_column,
                "experiment_name": experiment_name,
                **kwargs,
            },
        )

        return experiment
