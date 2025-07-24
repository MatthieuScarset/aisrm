"""
Streamlit application for AISRM CRM Sales Opportunities frontend.
"""

import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8500')
DEFAULT_VERSION = "v2"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(PROJECT_ROOT, "models")
VERSIONS = [dir for dir in os.listdir(
    MODELS_PATH) if os.path.isdir(os.path.join(MODELS_PATH, dir))]

st.title("Sales Agent Recommendation")
st.write("Select a client and a product to get the recommended sales agent.")

# Version selector
version = st.selectbox("Model Version", sorted(
    VERSIONS, reverse=True), index=0)

try:
    # Get model info and feature categories
    info_response = requests.get(f"{API_BASE_URL}/{version}/info")
    if info_response.status_code == 200:
        model_info = info_response.json()

        st.subheader("Model Information")
        st.write(f"Model Type: {model_info['model_type']}")
        st.write(f"Test Score: {model_info['test_score']['summary']}")

        # Feature inputs
        st.subheader("Input Features")

        feature_inputs = {}
        categories = model_info['features']['categories']
        defaults = model_info['features']['defaults']

        # Create input widgets for each feature category
        for feature_name, category_values in categories.items():
            if feature_name == 'sales_agent':
                continue

            if category_values:  # Only show if there are category values
                default_idx = 0
                if feature_name in defaults:
                    try:
                        default_idx = category_values.index(
                            str(defaults[feature_name]))
                    except ValueError:
                        default_idx = 0

                selected_value = st.selectbox(
                    f"Select {feature_name.replace('_', ' ').title()}",
                    category_values,
                    index=default_idx,
                )

                feature_inputs[feature_name] = selected_value

        # Prediction button
        if st.button("Get Prediction"):
            # Make prediction request
            predict_response = requests.get(
                f"{API_BASE_URL}/{version}/predict",
                params=feature_inputs
            )

            if predict_response.status_code == 200:
                predictions = predict_response.json()

                st.subheader("Predictions")

                # Convert to DataFrame for better display
                pred_df = pd.DataFrame([
                    {"Sales Agent": agent, "Score": score}
                    for agent, score in predictions.items()
                ]).sort_values("Score", ascending=False)

                st.dataframe(pred_df, use_container_width=True)

                # Highlight best recommendation
                best_agent = pred_df.iloc[0]
                st.success(
                    f"🎯 **Recommended Sales Agent:** {best_agent['Sales Agent']} (Score: {best_agent['Score']:.4f})")

            else:
                st.error(f"Prediction failed: {predict_response.status_code}")

    else:
        st.error(f"Failed to load model info: {info_response.status_code}")

except requests.exceptions.ConnectionError:
    st.error(
        f"❌ Cannot connect to API server. Make sure the API is running on {API_BASE_URL}")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Feature importance visualization (optional)
if st.checkbox("Show Feature Importances"):
    try:
        importance_response = requests.get(
            f"{API_BASE_URL}/{version}/feature-importances")
        if importance_response.status_code == 200:
            importances = importance_response.json()
            feature_names = list(importances['feature'].values())
            importance_values = list(importances['importance'].values())

            importance_df = pd.DataFrame({
                "Feature": feature_names,
                "Importance": importance_values
            }).sort_values("Importance", ascending=True)

            st.subheader("Feature Importances")
            st.bar_chart(importance_df.set_index("Feature"))

    except Exception as e:
        st.error(f"Failed to load feature importances: {str(e)}")
