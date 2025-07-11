import streamlit as st
import pandas as pd
import joblib
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
    # Filter dataframe for this combination
    row = df[(df['account'] == account) & (df['product'] == product)]
    if len(row) == 0:
        st.warning("No matching opportunity found in the historical data.")
    else:
        # Use the first match (could extend to allow editing other fields!)
        X_new = row.drop(columns=["opportunity_id", "sales_agent", "deal_stage"])
        X_new_encoded = X_new.apply(LabelEncoder().fit_transform)
        y_pred = model.predict(X_new_encoded)
        predicted_agent = y_encoder.inverse_transform(y_pred)[0]
        st.success(f"🧠 Recommended Sales Agent: **{predicted_agent}**")
        with st.expander("Show input features"):
            st.json(X_new.to_dict('records')[0])
