"""ML model module for the AISRM project.

This module contains definitions or functions related to model training.
"""

from datetime import datetime
from pickle import dump, HIGHEST_PROTOCOL
import os
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from src.config import PROCESSED_DATA_PATH, MODELS_PATH, HOLD_OUT


def load_dataset() -> pd.DataFrame:
    """
    Load the raw dataset.
    """
    return pd.read_csv(PROCESSED_DATA_PATH + "/dataset.csv")


def clean_dataset(df: pd.DataFrame):
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


def get_target_column(df: pd.DataFrame) -> str:
    return df.columns[-1]


def split_dataset(df: pd.DataFrame, target_column: str) -> list:
    """
    Run train test split, assuming target is the last column.
    """
    feature_columns = [col for col in df.columns if col != target_column]

    X = df[feature_columns]  # pylint: disable=invalid-name
    y = df[target_column]

    return train_test_split(X, y, test_size=HOLD_OUT)


def get_preprocessor(num_columns: list, cat_columns: list) -> ColumnTransformer:

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

    preprocessor = ColumnTransformer(
        [
            ("num_transformer", num_pipeline, num_columns),
            ("cat_transformer", cat_pipeline, cat_columns),
        ]
    )

    return preprocessor


def initialize_model() -> GradientBoostingRegressor:
    """
    Get the estimator class.
    """
    return GradientBoostingRegressor()


def save_model(model, preprocessor, metadata) -> str:
    model_folder_path = MODELS_PATH + "/" + \
        str(datetime.now().timestamp()).split('.', maxsplit=1)[0]
    if model_folder_path not in os.listdir(MODELS_PATH):
        os.mkdir(model_folder_path)
    with open(model_folder_path + "/model.pkl", "wb") as f:
        dump(model, f, protocol=HIGHEST_PROTOCOL)
    with open(model_folder_path + "/preprocessor.pkl", "wb") as f:
        dump(preprocessor, f, protocol=HIGHEST_PROTOCOL)
    with open(model_folder_path + "/metadata.pkl", "wb") as f:
        dump(metadata, f, protocol=HIGHEST_PROTOCOL)

    return model_folder_path


def get_feature_importance(model, preprocessor):
    """Get feature importance from the trained model."""
    if not hasattr(model, 'feature_importances_'):
        return None

    # Get feature names after preprocessing
    if hasattr(preprocessor, 'get_feature_names_out'):
        feature_names = preprocessor.get_feature_names_out()
    else:
        feature_names = [f"feature_{i}" for i in range(
            len(model.feature_importances_))]

    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    return importance_df.to_dict()


def train_and_save():
    # Load
    df = load_dataset()
    print(f"Raw dataset: {df.shape}")

    # Clean
    df = clean_dataset(df)
    print(f"Clean dataset: {df.shape}")

    # Split
    target_column = get_target_column(df)
    X_train, X_test, y_train, y_test = split_dataset(df, target_column)
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
    preprocessor = get_preprocessor(
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
    model = initialize_model()
    model.fit(X_train_transformed, y_train)

    # Score
    # @todo Save results
    cv_results = cross_validate(model, X_test_transformed, y_test, cv=5)
    test_score = cv_results["test_score"]

    # Metadata
    feature_importances = get_feature_importance(model, preprocessor)
    feature_defaults = {}
    for col in features_df.columns:
        # Most frequent values for categories.
        feature_defaults[col] = features_df[col].mode()
        if col in numerical_columns:
            # Mean values for numbers.
            feature_defaults[col] = features_df[col].mean()

    feature_categories = {}
    for col in textual_columns:
        feature_categories[col] = features_df[col].unique()

    metadata = {
        "model_type": str(model).replace("()", ""),
        "test_score": test_score,
        "feature_importances": feature_importances,
        "feature_defaults": feature_defaults,
        "feature_categories": feature_categories,
    }

    # Export
    model_folder_path = save_model(model, preprocessor, metadata)

    print(f"Score: {test_score.mean():.4f} (+/- {test_score.std() * 2:.4f})")
    print(f"Model saved: {model_folder_path}")


if __name__ == "__main__":
    train_and_save()
