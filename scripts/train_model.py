from scripts.load_data import load_data
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# 1. Load data
df = load_data()

# 2. Define X (features) and y (target)
X = df.drop(columns=["opportunity_id", "sales_agent", "deal_stage"])
y = df["sales_agent"]

# 3. Encode categorical features
X = X.apply(LabelEncoder().fit_transform)
y_encoder = LabelEncoder()
y = y_encoder.fit_transform(y)

# 4. Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 6. Evaluate
y_pred = model.predict(X_test)
print("✅ Model trained.")
print("🔍 Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 7. Save model and encoder
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.joblib")
joblib.dump(y_encoder, "models/y_encoder.joblib")
