# Import libraries
import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from eqc_models.ml.regressor import LinearRegression

# Set parameters
SOLVER_ACCESS = "cloud"
IP_ADDR = os.environ.get("DEVICE_IP_ADDRESS", "172.18.41.58")
PORT = os.environ.get("DEVICE_PORT", "50051")

# Create sample data
np.random.seed(0)
X = np.random.rand(100, 1) * 10
y = 3 * X.squeeze() + 5 + np.random.randn(100) * 2

print(X.shape, y.shape)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0
)

# Initialize and fit the Ridge Regression model
model = LinearRegression(
    relaxation_schedule=2,
    num_samples=1,
    solver_access=SOLVER_ACCESS,
    ip_addr=IP_ADDR,
    port=PORT,                
    l2_reg_coef=0,
    alpha=1,
)
model.fit(X_train, y_train)

# Make predictions
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Evaluate the model
print("R^2 on train data:", r2_score(y_train, y_pred_train))
print("R^2 on test data:", r2_score(y_test, y_pred_test))
print("Regression Coefficients:", model.params)
