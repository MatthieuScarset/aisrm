import streamlit as st
import pandas as pd
import joblib
import numpy as np
from scripts.load_data import load_data
from sklearn.preprocessing import LabelEncoder

# Load data and models
df = load_data()
model = joblib.load("models/model.joblib")
y_encoder = joblib.load("models/y_encoder.joblib")

# Sidebar - choose account and product
accounts = df['account'].unique()
products = df['product'].unique()

st.title("Sales Agent Recommendation")
st.write("Select a client and a product to get the recommended sales agent.")

account = st.selectbox("Client (Account)", accounts)
product = st.selectbox("Product", products)

if st.button("Recommend Sales Agent"):
    row = df[(df['account'] == account) & (df['product'] == product)]
    if len(row) == 0:
        st.warning("No matching opportunity found in the historical data.")
    else:
        X_new = row.drop(columns=["opportunity_id", "sales_agent", "deal_stage"])
        X_new_encoded = X_new.apply(LabelEncoder().fit_transform)
        proba = model.predict_proba(X_new_encoded)[0]
        top3_idx = np.argsort(proba)[::-1][:3]
        top3_agents = y_encoder.inverse_transform(top3_idx)
        top3_probs = proba[top3_idx]
        st.markdown("### 🧠 Top 3 Recommended Sales Agents")
        for agent, prob in zip(top3_agents, top3_probs):
            st.write(f"**{agent}**: {prob:.0%} probability")

        # 👉 PLACE THE "WHY?" BLOCK **HERE**
        top_agent = top3_agents[0]
        similar_deals = df[
            (df['sales_agent'] == top_agent) &
            (
                (df['sector'] == row['sector'].values[0]) |
                (df['product'] == product)
            )
        ]
        num_deals = len(similar_deals)
        if num_deals == 0:
            st.info(f"Why? **{top_agent}** is recommended based on other factors (such as similar account size, location, or revenue), but has not yet closed a deal in the {row['sector'].values[0]} sector or with product **{product}**.")
        else:
            st.info(f"Why? **{top_agent}** closed {num_deals} deals in the {row['sector'].values[0]} sector or with product **{product}**.")

        # Optionally show input features used
        with st.expander("Show input features"):
            st.json(X_new.to_dict('records')[0])
