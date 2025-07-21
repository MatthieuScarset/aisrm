"""ML model module for the AISRM project.

This module contains definitions or functions related to model training.
"""

from datetime import datetime
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from src.config import PROCESSED_DATA_PATH, MODELS_PATH, HOLD_OUT


def _load_dataset() -> pd.DataFrame:
    """
    Load the raw dataset.
    """
    return pd.read_csv(PROCESSED_DATA_PATH + "/dataset.csv")


def _clean_dataset(df: pd.DataFrame):
    """
    Prepare dataset before training.
    """
    # Remove NaN.
    target_column = df.columns[-1]
    df = df.dropna(subset=[target_column])

    # Drop useless columns
    for col in df.columns:
        if col.startswith("Unnamed:"):
            df = df.drop(col, axis=1)

    return df


def _get_target_column(df: pd.DataFrame) -> str:
    return df.columns[-1]


def _split(df: pd.DataFrame, target_column: str) -> list:
    """
    Run train test split, assuming target is the last column.
    """
    feature_columns = [col for col in df.columns if col != target_column]

    X = df[feature_columns]  # pylint: disable=invalid-name
    y = df[target_column]

    return train_test_split(X, y, test_size=HOLD_OUT)


def _getpreprocessor(num_columns: list, cat_columns: list) -> ColumnTransformer:

    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", RobustScaler()),
        ]
    )

    cat_pipeline = Pipeline(
        [
            ("encoder", OneHotEncoder(sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        [
            ("num_transformer", num_pipeline, num_columns),
            ("cat_transformer", cat_pipeline, cat_columns),
        ]
    )


def _get_model():
    """
    Get the estimator class.
    """
    return LinearRegression()


def _save_model(model, preprocessor, cv_results):
    """
    Save the trained model and preprocessor to pickle files.
    """
    # Create timestamp for versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save model
    model_path = os.path.join(MODELS_PATH, f"model_{timestamp}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Save preprocessor
    preprocessor_path = os.path.join(
        MODELS_PATH, f"preprocessor_{timestamp}.pkl")
    with open(preprocessor_path, "wb") as f:
        pickle.dump(preprocessor, f)

    # Save model metadata
    metadata = {
        "model_type": str(model).replace("()", ""),
        "timestamp": timestamp,
        "cv_mean_score": cv_results["test_score"].mean(),
        "cv_std_score": cv_results["test_score"].std(),
        "cv_scores": cv_results["test_score"].tolist(),
        "model_path": model_path,
        "preprocessor_path": preprocessor_path,
    }

    metadata_path = os.path.join(MODELS_PATH, f"metadata_{timestamp}.pkl")
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    return model_path, preprocessor_path, metadata_path


def _load_model(model_path):
    """
    Load a saved model, preprocessor and metadata from pickle files.

    Args:
        model_path (str): Path to the saved model pickle file

    Returns:
        tuple: (model, preprocessor, metadata)
    """
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    preprocessor_path = model_path.replace("model_", "preprocessor_")
    with open(preprocessor_path, "rb") as f:
        preprocessor = pickle.load(f)

    metadata_path = model_path.replace("model_", "metadata_")
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    return model, preprocessor, metadata


def load_latest_model():
    """
    Load the most recently saved model and preprocessor.

    Returns:
        tuple: (model, preprocessor, metadata)
    """
    # Find the latest model files
    model_files = [
        f for f in os.listdir(MODELS_PATH) if "model_" in f and f.endswith(".pkl")
    ]

    if not model_files:
        raise FileNotFoundError(
            "No saved models found in the models directory")

    # Sort by timestamp (filename contains timestamp)
    latest_model_file = sorted(model_files)[-1]

    # Load model, preprocessor and metadata
    model_path = os.path.join(MODELS_PATH, latest_model_file)

    return _load_model(model_path)


if __name__ == "__main__":
    # Load
    df = _load_dataset()
    print(f"Raw dataset: {df.shape}")

    # Clean
    df = _clean_dataset(df)
    print(f"Clean dataset: {df.shape}")

    # Split
    target_column = _get_target_column(df)
    X_train, X_test, y_train, y_test = _split(df, target_column)
    print(f"Train set: {1 - HOLD_OUT} = {X_train.shape[0]}")
    print(f"Test set: {HOLD_OUT} = {X_test.shape[0]}")
    print(f"Y train mean ({target_column}): {y_train.mean()}")
    assert X_test.shape[0] + X_train.shape[0] == df.shape[0]

    features_df = df.drop(columns=[target_column])

    numerical_columns = features_df.select_dtypes(
        include=[np.number]).columns.tolist()

    textual_columns = features_df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    # Preprocess
    preprocessor = _getpreprocessor(
        num_columns=numerical_columns, cat_columns=textual_columns
    )

    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)
    features_columns = preprocessor.get_feature_names_out()
    print(f"Features out: {len(features_columns)}")
    X_train_array = np.asarray(X_train_transformed)
    assert not np.isnan(X_train_array).any(
    ), "Training data contains missing values"

    # Fit
    model = _get_model()
    model.fit(X_train_transformed, y_train)

    # Score
    cv_results = cross_validate(model, X_test_transformed, y_test, cv=5)
    score = cv_results["test_score"]

    # Export
    model_path, preprocessor_path, metadata_path = _save_model(
        model, preprocessor, cv_results
    )

    print(f"Test score: {score.mean():.4f} (+/- {score.std() * 2:.4f})")
