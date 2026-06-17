import numpy as np
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# Load saved features
X = np.load("X.npy")
y = np.load("y.npy")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Model with scaling
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(class_weight='balanced', max_iter=1000)
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))

joblib.dump(model, "model.pkl")
print("Model saved as model.pkl")
print("Labels:", y)