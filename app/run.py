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


# Add custom CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .prediction-highlight {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }
    
    .section-header {
        background: linear-gradient(45deg, #ff6b6b, #ffa726);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Use colored header
st.markdown('<div class="main-header"><h1>🎯 AISRM</h1><p>AI-powered Sales Agent Recommendation</p><p>Select a client and a product to get the recommended sales agent.</p></div>', unsafe_allow_html=True)

# Version selector
st.markdown('<div class="section-header">🔧 Model Configuration</div>', unsafe_allow_html=True)
version = st.selectbox("🤖 Model Version", sorted(
    VERSIONS, reverse=True), index=0)

try:
    # Get model info and feature categories
    info_response = requests.get(f"{API_BASE_URL}/{version}/info", timeout=10)
    if info_response.status_code == 200:
        model_info = info_response.json()

        # Feature inputs
        st.markdown('<div class="section-header">🎯 Input Features</div>', unsafe_allow_html=True)

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

                # Add emojis based on feature type
                emoji_map = {
                    'sector': '🏢',
                    'office': '🌍',
                    'product': '📦',
                    'location': '📍'
                }

                emoji = emoji_map.get(feature_name.lower(), '⚙️')

                selected_value = st.selectbox(
                    f"{emoji} Select {feature_name.replace('_', ' ').title()}",
                    category_values,
                    index=default_idx,
                )

                feature_inputs[feature_name] = selected_value

        # Prediction button
        if st.button("🚀 Get Prediction", type="primary"):
            with st.spinner("🔄 Analyzing sales agents..."):
                # Make prediction request
                predict_response = requests.get(
                    f"{API_BASE_URL}/{version}/predict",
                    params=feature_inputs,
                    timeout=10
                )

            if predict_response.status_code == 200:
                predictions = predict_response.json()

                st.markdown('<div class="section-header">📊 Predictions</div>', unsafe_allow_html=True)

                # Convert to DataFrame for better display
                pred_df = pd.DataFrame([
                    {"Sales Agent": agent, "Score": score}
                    for agent, score in predictions.items()
                ]).sort_values("Score", ascending=False)

                # Format the dataframe for better display
                pred_df['Sales Agent'] = pred_df['Sales Agent'].str.title()
                pred_df['Expected Close Value'] = pred_df['Score'].apply(lambda x: f"${x:,.2f}")
                pred_df = pred_df.drop('Score', axis=1)  # Remove the original Score column
                pred_df.insert(0, 'Rank', range(1, len(pred_df) + 1))

                # Display with better styling
                st.dataframe(
                    pred_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("🏆 Rank", width="small"),
                        "Sales Agent": st.column_config.TextColumn("👤 Sales Agent", width="medium"),
                        "Expected Close Value": st.column_config.TextColumn("💰 Expected Close Value", width="medium")
                    }
                )

                # Highlight best recommendation
                best_agent = pred_df.iloc[0]
                # Get the original score for formatting
                best_score = pred_df['Expected Close Value'].max()
                prediction_text = f"""
                <div class="prediction-highlight">
                    <h3>🏆 Recommended Sales Agent: {best_agent['Sales Agent']}</h3>
                    <p><strong>Expected close value:</strong> {best_score}</p>
                    <p>This agent has the highest predicted performance for your selected criteria.</p>
                </div>"""

                st.markdown(prediction_text, unsafe_allow_html=True)

                st.toast(f'Best recommendation: {best_agent["Sales Agent"]} with {best_score} expected close value!', icon='🎉')
            else:
                st.error(f"❌ Prediction failed: {predict_response.status_code}")

    else:
        st.error(f"Failed to load model info: {info_response.status_code}")
        st.error(f"Error: {info_response.text}")
        st.error(f"Base URL: {API_BASE_URL}")

except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    st.error(
        f"❌ Cannot connect to API server. Make sure the API is running on {API_BASE_URL}")
except requests.exceptions.RequestException as e:
    st.error(f"❌ API request failed: {str(e)}")
except ValueError as e:
    st.error(f"❌ Invalid response from API: {str(e)}")
except Exception as e:
    st.error(f"❌ An unexpected error occurred: {str(e)}")

# Feature importance visualization (optional)
if st.checkbox("📊 Show Feature Importances"):
    try:
        importance_response = requests.get(
            f"{API_BASE_URL}/{version}/feature-importances", timeout=10)
        if importance_response.status_code == 200:
            importances = importance_response.json()
            feature_names = list(importances['feature'].values())
            importance_values = list(importances['importance'].values())

            importance_df = pd.DataFrame({
                "Feature": feature_names,
                "Importance": importance_values
            }).sort_values("Importance", ascending=True)

            st.markdown('<div class="section-header">🔍 Feature Importances</div>', unsafe_allow_html=True)
            st.bar_chart(importance_df.set_index("Feature"))

    except (requests.exceptions.RequestException, ValueError) as e:
        st.error(f"❌ Failed to load feature importances: {str(e)}")

# Model information visualization (optional)
if st.checkbox("📊 Show Model Information"):
    try:
        info_response = requests.get(f"{API_BASE_URL}/{version}/info", timeout=10)
        if info_response.status_code == 200:
            model_info = info_response.json()

            st.markdown('<div class="section-header">📊 Model Information</div>', unsafe_allow_html=True)

            # Create colored metrics
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="🤖 Model Type",
                    value=model_info['model_type'],
                )

            with col2:
                st.metric(
                    label="📈 Test Score",
                    value=model_info['test_score']['summary'],
                )
        else:
            st.error(f"❌ Failed to load model info: {info_response.status_code}")
    except (requests.exceptions.RequestException, ValueError) as e:
        st.error(f"❌ Failed to load model information: {str(e)}")
