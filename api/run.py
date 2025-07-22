"""
FastAPI application for AISRM CRM Sales Opportunities API.

This module provides the main FastAPI application with CORS middleware
and basic endpoints for the CRM sales opportunities system.
"""

import os
from pickle import load
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
import pandas as pd

ENV = os.getenv('ENV', "prod") 
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(PROJECT_ROOT, "models")

app = FastAPI()


def get_model_folder_path():
    model_folder_path = os.path.join(MODELS_PATH, 'production')

    if ENV is not 'prod':
        # Get all directories in MODELS_PATH.
        model_dirs = [d for d in os.listdir(MODELS_PATH)
                      if os.path.isdir(os.path.join(MODELS_PATH, d))]

        if not model_dirs:
            raise FileNotFoundError(
                "No model directories found in MODELS_PATH")

        # Sort directories by name.
        model_dirs.sort(reverse=True)
        latest_model_dir = model_dirs[0]
        model_folder_path = os.path.join(MODELS_PATH, latest_model_dir)

    return model_folder_path


def load_model():
    """
    Load the most recent model from MODELS_PATH.

    Params:
        latest: If False, get latest model by folders name.
    """
    model_folder_path = get_model_folder_path()

    # Load the model components
    with open(os.path.join(model_folder_path, "model.pkl"), "rb") as f:
        model = load(f)
    with open(os.path.join(model_folder_path, "preprocessor.pkl"), "rb") as f:
        preprocessor = load(f)
    with open(os.path.join(model_folder_path, "metadata.pkl"), "rb") as f:
        metadata = load(f)

    return model, preprocessor, metadata


@app.get("/")
def root():
    """
    Root endpoint that returns a greeting and current timestamp.

    Returns:
        dict: A dictionary containing greeting message and current timestamp.
    """
    return {
        "greeting": "Hello from AISMR",
        "timestamp": datetime.now(),
    }


@app.get("/info")
def info():
    """
    Root endpoint that returns information about the model.

    Returns:
        dict: A dictionary containing info about the latest model.
    """
    _, _, metadata = load_model()

    return {
        "model_type": metadata['model_type'],
        "test_score": metadata['test_score'].mean(),
    }


@app.get("/predict")
def predict(
    sales_agent: Optional[str] = None,
    account: Optional[str] = None,
    series: Optional[str] = None,
):
    """
    Root endpoint that returns a prediction from our model.

    Returns:
        dict: A dictionary of prediction, keyed by sale_agent.
    """
    model, preprocessor, metadata = load_model()

    # Default features required for prediction
    all_agents = metadata['feature_categories']['sales_agent']
    features = metadata['feature_defaults']

    if sales_agent is not None:
        all_agents = [sales_agent]

    # Make predictions
    predictions = {}
    for sales_agent in all_agents:
        features['sales_agent'] = sales_agent

        if account is not None:
            features['account'] = account

        if series is not None:
            features['series'] = series

        # Convert dictionary to DataFrame (required by preprocessor)
        features_df = pd.DataFrame(features)

        # Transform features using the trained preprocessor
        X_transformed = preprocessor.transform(features_df)

        # Predict now
        prediction = float(model.predict(X_transformed)[0])
        predictions[sales_agent] = prediction

    return predictions
