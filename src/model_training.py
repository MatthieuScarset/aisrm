"""ML model module for the AISRM project.

This module contains definitions or functions related to model training.
"""
import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from src.config import RAW_DATA_PATH, HOLD_OUT


def _load_dataset() -> pd.DataFrame:
    """
    Load the raw dataset.
    """
    return pd.read_csv(RAW_DATA_PATH + "/dataset.csv")


def _clean_dataset(df: pd.DataFrame):
    """
    Prepare dataset before training.
    """

    # Drop useless columns
    useless_columns = ['Unnamed: 0']
    for col in useless_columns:
        if col in df.columns:
            df = df.drop(col, axis=1)

    # Remove NaN.
    df = df.dropna()

    return df


def _get_target_column(df: pd.DataFrame) -> str:
    return df.columns[-1]


def _split(df: pd.DataFrame, target_column: str) -> list:
    """
    Run train test split, assuming target is the last column.
    """
    feature_columns = [col for col in df.columns if col != target_column]

    X = df[feature_columns]
    y = df[target_column]

    return train_test_split(X, y, test_size=HOLD_OUT)


def _get_preprocessor(num_columns: list, cat_columns: list) -> ColumnTransformer:

    num_pipeline = Pipeline([
        ('scaler', RobustScaler())
    ])

    cat_pipeline = Pipeline([
        ('encoder', OneHotEncoder(sparse_output=False)),
    ])

    preprocessor = ColumnTransformer([
        ('num_transformer', num_pipeline, num_columns),
        ('cat_transformer', cat_pipeline, cat_columns),
    ])

    return preprocessor


def _get_model():
    """
    Get the estimator class.
    """
    return LinearRegression()


def _save_model(model, preprocessor, cv_results):
    """
    Save the trained model and preprocessor to pickle files.
    """
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)

    # Create timestamp for versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save model
    model_path = os.path.join(
        models_dir, f'linear_regression_model_{timestamp}.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    # Save preprocessor
    preprocessor_path = os.path.join(
        models_dir, f'preprocessor_{timestamp}.pkl')
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)

    # Save model metadata
    metadata = {
        'model_type': 'LinearRegression',
        'timestamp': timestamp,
        'cv_mean_score': cv_results['test_score'].mean(),
        'cv_std_score': cv_results['test_score'].std(),
        'cv_scores': cv_results['test_score'].tolist(),
        'model_path': model_path,
        'preprocessor_path': preprocessor_path
    }

    metadata_path = os.path.join(models_dir, f'model_metadata_{timestamp}.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    return model_path, preprocessor_path, metadata_path


def _load_model(model_path, preprocessor_path):
    """
    Load a saved model and preprocessor from pickle files.

    Args:
        model_path (str): Path to the saved model pickle file
        preprocessor_path (str): Path to the saved preprocessor pickle file

    Returns:
        tuple: (model, preprocessor)
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)

    return model, preprocessor


def load_latest_model():
    """
    Load the most recently saved model and preprocessor.

    Returns:
        tuple: (model, preprocessor, metadata)
    """
    models_dir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'models')

    # Find the latest model files
    model_files = [f for f in os.listdir(models_dir) if f.startswith(
        'linear_regression_model_') and f.endswith('.pkl')]

    if not model_files:
        raise FileNotFoundError(
            "No saved models found in the models directory")

    # Sort by timestamp (filename contains timestamp)
    latest_model_file = sorted(model_files)[-1]
    timestamp = latest_model_file.replace(
        'linear_regression_model_', '').replace('.pkl', '')

    model_path = os.path.join(models_dir, latest_model_file)
    preprocessor_path = os.path.join(
        models_dir, f'preprocessor_{timestamp}.pkl')
    metadata_path = os.path.join(models_dir, f'model_metadata_{timestamp}.pkl')

    # Load model and preprocessor
    model, preprocessor = _load_model(model_path, preprocessor_path)

    # Load metadata
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    return model, preprocessor, metadata


if __name__ == "__main__":
    """Model training pipeline"""
    df = _load_dataset()
    print(f"Raw dataset: {df.shape}")
    df = _clean_dataset(df)
    print(f"Clean dataset: {df.shape}")

    target_column = _get_target_column(df)
    X_train, X_test, y_train, y_test = _split(df, target_column)
    print(f"Train set: {1 - HOLD_OUT} = {X_train.shape[0]}")
    print(f"Test set: {HOLD_OUT} = {X_test.shape[0]}")

    # Verify train test split shapes.
    assert X_test.shape[0] + X_train.shape[0] == df.shape[0]

    features_df = df.drop(columns=[target_column])

    num_columns = features_df.select_dtypes(
        include=[np.number]).columns.tolist()

    cat_columns = features_df.select_dtypes(
        include=['object', 'string']).columns.tolist()

    preprocessor = _get_preprocessor(
        num_columns=num_columns, cat_columns=cat_columns)

    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    features_columns = preprocessor.get_feature_names_out()
    print(f"Features out: {len(features_columns)}")

    # Verify no missing values.
    X_train_array = np.asarray(X_train_transformed)
    assert not np.isnan(X_train_array).any(
    ), "Training data contains missing values"

    # Fit the model.
    model = _get_model()
    model.fit(X_train_transformed, y_train)

    cv_results = cross_validate(model, X_test_transformed, y_test, cv=5)
    score = cv_results['test_score']

    # Save model to a pickle file.
    model_path, preprocessor_path, metadata_path = _save_model(
        model, preprocessor, cv_results)

    print(f"\nTraining completed successfully!")
    print(f"Model saved to: {model_path}")
    print(f"Preprocessor saved to: {preprocessor_path}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"===============================")
    print(f"Test score: {score.mean():.4f} (+/- {score.std() * 2:.4f})")
    print(f"===============================")
