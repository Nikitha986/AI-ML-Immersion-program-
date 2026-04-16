import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
# 1. Load and Scale (Same as Day 8)
data = fetch_california_housing()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
# 2. Define the "Grid" of parameters to try
# We want to test different values of 'alpha'
param_grid = {'alpha': [0.1, 1.0, 10.0, 100.0, 500.0]}
# 3. Initialize Grid Search
# cv=5 means 5-fold Cross-Validation (splitting data 5 times to be sure)
grid_search = GridSearchCV(Ridge(), param_grid, cv=5, scoring='r2')
# 4. RUN THE SEARCH
grid_search.fit(X_train_scaled, y_train)

print(f"Best Alpha Found: {grid_search.best_params_}")
print(f"Best R2 Score: {grid_search.best_score_:.4f}")