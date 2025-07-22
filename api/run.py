"""
FastAPI application for AISRM CRM Sales Opportunities API.

This module provides the main FastAPI application with CORS middleware
and basic endpoints for the CRM sales opportunities system.
"""

from datetime import datetime
from fastapi import FastAPI
from src.model import load_model
from typing import Optional

app = FastAPI()


@app.get("/")
def root():
    """
    Root endpoint that returns a greeting and current timestamp.

    Returns:
        dict: A dictionary containing greeting message and current timestamp.
    """
    _, _, metadata = load_model()

    return {
        "greeting": "Hello from AISMR",
        "timestamp": datetime.now(),
        "model_type": metadata['model_type'],
        "test_score": metadata['test_score'].mean(),
    }


@app.get("/predict")
def predict(
    sales_agent: Optional[str] = None,
    account: Optional[str]  = None,
    series: Optional[str]  = None,
):
    """
    Root endpoint that returns a prediction from our model.

    Returns:
        dict: A dictionary containing prediction and current timestamp.
    """
    model, preprocessor, metadata = load_model()

    # Default features required for prediction
    features = metadata['feature_defaults']
    
    if sales_agent != None:
        features['sales_agent'] = sales_agent
        
    if account != None:
        features['account'] = account

    if series != None:
        features['series'] = series

    # Transform features using the trained preprocessor
    X_transformed = preprocessor.transform(features)

    # Make prediction
    prediction = model.predict(X_transformed)

    return {
        "prediction": float(prediction[0]),
        "timestamp": datetime.now()
    }
