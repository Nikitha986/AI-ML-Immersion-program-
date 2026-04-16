from sklearn.datasets import fetch_california_housing
import pandas as pd
# 1. Load the dataset
data = fetch_california_housing()
df = pd.DataFrame(data.data, columns=data.feature_names)
df['MedHouseVal'] = data.target # This is our 'y' (Price in $100,000s)
print("Dataset Overview:")
print(df.head())
print("\nBasic Statistics:")
print(df.describe())

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
# Define Features and Target
X = df.drop('MedHouseVal', axis=1)
y = df['MedHouseVal']
# 1. Split: 80% Train, 20% Test
X_train, X_test, y_train, y_test = train_test_split(X, y,
test_size=0.2, random_state=42)
# 2. Scale: Standardize features (Mean=0, Variance=1)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

from sklearn.metrics import mean_absolute_error, r2_score
# 3. Train
model = LinearRegression()
model.fit(X_train_scaled, y_train)
# 4. Predict
predictions = model.predict(X_test_scaled)
# 5. Evaluate

None
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
print(f"Mean Absolute Error: ${mae * 100000:.2f}")
print(f"R-Squared Score: {r2:.2f}")

import matplotlib.pyplot as plt
residuals = y_test - predictions
plt.scatter(y_test, residuals)
plt.axhline(y=0, color='r', linestyle='--')
plt.title("Residual Plot (Checking for Patterns)")
plt.show()