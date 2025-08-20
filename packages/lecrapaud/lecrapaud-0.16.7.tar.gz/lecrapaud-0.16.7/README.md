<div align="center">

<img src="https://s3.amazonaws.com/pix.iemoji.com/images/emoji/apple/ios-12/256/frog-face.png" width=120 alt="crapaud"/>

## Welcome to LeCrapaud

**An all-in-one machine learning framework**

[![GitHub stars](https://img.shields.io/github/stars/pierregallet/lecrapaud.svg?style=flat&logo=github&colorB=blue&label=stars)](https://github.com/pierregallet/lecrapaud/stargazers)
[![PyPI version](https://badge.fury.io/py/lecrapaud.svg)](https://badge.fury.io/py/lecrapaud)
[![Python versions](https://img.shields.io/pypi/pyversions/lecrapaud.svg)](https://pypi.org/project/lecrapaud)
[![License](https://img.shields.io/github/license/pierregallet/lecrapaud.svg)](https://github.com/pierregallet/lecrapaud/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/pierregallet/lecrapaud/branch/main/graph/badge.svg)](https://codecov.io/gh/pierregallet/lecrapaud)

</div>

## 🚀 Introduction

LeCrapaud is a high-level Python library for end-to-end machine learning workflows on tabular data, with a focus on financial and stock datasets. It provides a simple API to handle feature engineering, model selection, training, and prediction, all in a reproducible and modular way.

## ✨ Key Features

- 🧩 Modular pipeline: Feature engineering, preprocessing, selection, and modeling as independent steps
- 🤖 Automated model selection and hyperparameter optimization
- 📊 Easy integration with pandas DataFrames
- 🔬 Supports both regression and classification tasks
- 🛠️ Simple API for both full pipeline and step-by-step usage
- 📦 Ready for production and research workflows

## ⚡ Quick Start


### Install the package

```sh
pip install lecrapaud
```

### How it works

This package provides a high-level API to manage experiments for feature engineering, model selection, and prediction on tabular data (e.g. stock data).

### Typical workflow

```python
from lecrapaud import LeCrapaud

# 1. Create the main app
app = LeCrapaud(uri=uri)

# 2. Define your experiment context (see your notebook or api.py for all options)
context = {
    "data": your_dataframe,
    "columns_drop": [...],
    "columns_date": [...],
    # ... other config options
}

# 3. Create an experiment
experiment = app.create_experiment(**context)

# 4. Run the full training pipeline
experiment.train(your_dataframe)

# 5. Make predictions on new data
predictions = experiment.predict(new_data)
```

### Database Configuration (Required)

LeCrapaud requires access to a MySQL database to store experiments and results. You must either:

- Pass a valid MySQL URI to the `LeCrapaud` constructor:
  ```python
  app = LeCrapaud(uri="mysql+pymysql://user:password@host:port/dbname")
  ```
- **OR** set the following environment variables before using the package:
  - `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
  - Or set `DB_URI` directly with your full connection string.

If neither is provided, database operations will not work.

### Using OpenAI Embeddings (Optional)

If you want to use the `columns_pca` embedding feature (for advanced feature engineering), you must set the `OPENAI_API_KEY` environment variable with your OpenAI API key:

```sh
export OPENAI_API_KEY=sk-...
```

If this variable is not set, features relying on OpenAI embeddings will not be available.

### Experiment Context Arguments

Below are the main arguments you can pass to `create_experiment` (or the `Experiment` class):

| Argument             | Type      | Description                                                                              | Example/Default    |
| -------------------- | --------- | ---------------------------------------------------------------------------------------- | ------------------ |
| `columns_binary`     | list      | Columns to treat as binary                                                               | `['flag']`         |
| `columns_boolean`    | list      | Columns to treat as boolean                                                              | `['is_active']`    |
| `columns_date`       | list      | Columns to treat as dates                                                                | `['date']`         |
| `columns_drop`       | list      | Columns to drop during feature engineering                                               | `['col1', 'col2']` |
| `columns_frequency`  | list      | Columns to frequency encode                                                              | `['category']`     |
| `columns_onehot`     | list      | Columns to one-hot encode                                                                | `['sector']`       |
| `columns_ordinal`    | list      | Columns to ordinal encode                                                                | `['grade']`        |
| `columns_pca`        | list      | Columns to use for PCA/embeddings (requires `OPENAI_API_KEY` if using OpenAI embeddings) | `['text_col']`     |
| `columns_te_groupby` | list      | Columns for target encoding groupby                                                      | `['sector']`       |
| `columns_te_target`  | list      | Columns for target encoding target                                                       | `['target']`       |
| `data`               | DataFrame | Your main dataset (required for new experiment)                                          | `your_dataframe`   |
| `date_column`        | str       | Name of the date column                                                                  | `'date'`           |
| `experiment_name`    | str       | Name for the training session                                                            | `'my_session'`     |
| `group_column`       | str       | Name of the group column                                                                 | `'stock_id'`       |
| `max_timesteps`      | int       | Max timesteps for time series models                                                     | `30`               |
| `models_idx`         | list      | Indices of models to use for model selection                                             | `[0, 1, 2]`        |
| `number_of_trials`   | int       | Number of trials for hyperparameter optimization                                         | `20`               |
| `perform_crossval`   | bool      | Whether to perform cross-validation                                                      | `True`/`False`     |
| `perform_hyperopt`   | bool      | Whether to perform hyperparameter optimization                                           | `True`/`False`     |
| `plot`               | bool      | Whether to plot results                                                                  | `True`/`False`     |
| `preserve_model`     | bool      | Whether to preserve the best model                                                       | `True`/`False`     |
| `target_clf`         | list      | List of classification target column indices/names                                       | `[1, 2, 3]`        |
| `target_mclf`        | list      | Multi-class classification targets (not yet implemented)                                 | `[11]`             |
| `target_numbers`     | list      | List of regression target column indices/names                                           | `[1, 2, 3]`        |
| `test_size`          | int/float | Test set size (count or fraction)                                                        | `0.2`              |
| `time_series`        | bool      | Whether the data is time series                                                          | `True`/`False`     |
| `val_size`           | int/float | Validation set size (count or fraction)                                                  | `0.2`              |

**Note:**
- Not all arguments are required; defaults may exist for some.
- For `columns_pca` with OpenAI embeddings, you must set the `OPENAI_API_KEY` environment variable.



### Modular usage

You can also use each step independently:

```python
data_eng = experiment.feature_engineering(data)
train, val, test = experiment.preprocess_feature(data_eng)
features = experiment.feature_selection(train)
std_data, reshaped_data = experiment.preprocess_model(train, val, test)
experiment.model_selection(std_data, reshaped_data)
```

## ⚠️ Using Alembic in Your Project (Important for Integrators)

If you use Alembic for migrations in your own project and you share the same database with LeCrapaud, you must ensure that Alembic does **not** attempt to drop or modify LeCrapaud tables (those prefixed with `{LECRAPAUD_TABLE_PREFIX}_`).

By default, Alembic's autogenerate feature will propose to drop any table that exists in the database but is not present in your project's models. To prevent this, add the following filter to your `env.py`:

```python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name.startswith(f"{LECRAPAUD_TABLE_PREFIX}_"):
        return False  # Ignore LeCrapaud tables
    return True

context.configure(
    # ... other options ...
    include_object=include_object,
)
```

This will ensure that Alembic ignores all tables created by LeCrapaud when generating migrations for your own project.

---

## 🤝 Contributing

### Reminders for Github usage

1. Creating Github repository

```sh
$ brew install gh
$ gh auth login
$ gh repo create
```

2. Initializing git and first commit to distant repository

```sh
$ git init
$ git add .
$ git commit -m 'first commit'
$ git remote add origin <YOUR_REPO_URL>
$ git push -u origin master
```

3. Use conventional commits  
https://www.conventionalcommits.org/en/v1.0.0/#summary

4. Create environment

```sh
$ pip install virtualenv
$ python -m venv .venv
$ source .venv/bin/activate
```

5. Install dependencies

```sh
$ make install
```

6. Deactivate virtualenv (if needed)

```sh
$ deactivate
```

---

Pierre Gallet © 2025