import joblib
from scripts.load_data import load_data
from sklearn.preprocessing import LabelEncoder

# Load model and encoder
model = joblib.load("models/model.joblib")
y_encoder = joblib.load("models/y_encoder.joblib")

# Load data
df = load_data()

# Take one random sample as a test input
X_new = df.drop(columns=["opportunity_id", "sales_agent", "deal_stage"]).sample(1, random_state=42)

# Encode features in the same way as during training
X_new_encoded = X_new.apply(LabelEncoder().fit_transform)

# Predict sales agent
y_pred = model.predict(X_new_encoded)
predicted_agent = y_encoder.inverse_transform(y_pred)

print("🧠 Recommended Sales Agent:", predicted_agent[0])
print("Input features used:", X_new.to_dict('records')[0])
