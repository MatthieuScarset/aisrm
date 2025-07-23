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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(PROJECT_ROOT, "models")

app = FastAPI()


###############################################################################
# Helpers
###############################################################################


def get_model_folder_path(version: str):
    # Load model from versioned folder (ex: ../models/v1).
    if version != 'dev':
        return os.path.join(MODELS_PATH, version)

    # Get latest trained model by default, for development purpose.
    model_dirs = [d for d in os.listdir(MODELS_PATH)
                  if os.path.isdir(os.path.join(MODELS_PATH, d))]

    model_dirs.sort(reverse=True)
    latest_model_dir = model_dirs[0]
    return os.path.join(MODELS_PATH, latest_model_dir)


def load_model(version: str):
    """
    Load the most recent model from MODELS_PATH.

    Params:
        latest: If False, get latest model by folders name.
    """
    model_folder_path = get_model_folder_path(version)

    # Load the model components
    with open(os.path.join(model_folder_path, "model.pkl"), "rb") as f:
        model = load(f)
    with open(os.path.join(model_folder_path, "preprocessor.pkl"), "rb") as f:
        preprocessor = load(f)
    with open(os.path.join(model_folder_path, "metadata.pkl"), "rb") as f:
        metadata = load(f)

    return model, preprocessor, metadata

###############################################################################
# Routes
###############################################################################


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


@app.get("/{version}/info")
def info(version: str):
    """
    Root endpoint that returns information about the model.

    Returns:
        dict: A dictionary containing info about the latest model.
    """
    _, _, metadata = load_model(version)

    model_type = metadata["model_type"]
    test_score = metadata["test_score"]
    features_out = metadata["features_out"]
    feature_defaults = metadata["feature_defaults"]

    feature_categories = {}
    for k,v in metadata['feature_categories'].items():
        feature_categories[k] = [str(item) for item in v if item is not None and str(item) != 'nan']

    return {
        "model_type": model_type,
        'test_score': {
            "summary": f"{test_score.mean():.4f} (+/- {test_score.std() * 2:.4f})",
            "mean": metadata['test_score'].mean(),
            "std": metadata['test_score'].std(),
        },
        "features": {
            "out": features_out,
            "defaults": feature_defaults,
            "categories": feature_categories
        }
    }


@app.get("/{version}/predict")
def predict(
    version: str,
    sales_agent: Optional[str] = None,
    account: Optional[str] = None,
    series: Optional[str] = None,
    product: Optional[str] = None,
):
    """
    Root endpoint that returns a prediction from our model.

    Returns:
        dict: A dictionary of prediction, keyed by sale_agent.
    """
    model, preprocessor, metadata = load_model(version)

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

        if product is not None:
            features['product'] = product

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


@app.get("/{version}/feature-importances")
def feature_importance(version: str):
    _, _, metadata = load_model(version)
    return metadata['feature_importances']
