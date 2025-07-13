"""
FastAPI application for AISRM CRM Sales Opportunities API.

This module provides the main FastAPI application with CORS middleware
and basic endpoints for the CRM sales opportunities system.
"""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def root():
    """
    Root endpoint that returns a greeting and current timestamp.

    Returns:
        dict: A dictionary containing greeting message and current timestamp.
    """
    response = {"greeting": "Hello from AISMR", "timestamp": datetime.now()}

    return response
