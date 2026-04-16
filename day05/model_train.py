from sklearn.model_selection import train_test_split
import pandas as pd
# Sample Dataset: Hours Studied vs Exam Score
data = {'Hours': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
'Score': [35, 40, 55, 60, 68, 72, 81, 88, 92, 95]}
df = pd.DataFrame(data)
X = df[['Hours']] # Features (Capital X for matrix)
y = df['Score'] # Target (Lowercase y for vector)
# Split into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training items: {len(X_train)} | Testing items: {len(X_test)}")

from sklearn.linear_model import LinearRegression
# 1. Initialize the model
model = LinearRegression()
# 2. TRAIN: The "fit" function is where the learning happens
model.fit(X_train, y_train)
# 3. PREDICT: Ask the AI to guess the scores for the test hours
predictions = model.predict(X_test)
print("Predictions for Test Set:", predictions)
print("Actual Scores:", y_test.values)

from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions) # 1.0 is a perfect score!
print(f"Mean Squared Error: {mse:.2f}")
print(f"R-Squared Score: {r2:.2f}")

new_data = pd.DataFrame([[11]], columns=['Hours'])
prediction = model.predict(new_data)

print("Prediction for 11 hours:", prediction[0])

#REFECT 
# If the model is trained using only 2 rows of data instead of 8, it will not learn underlying patterns propelry, with such small dataset the model cannot generalie well and may either well and may either overfit those two points or produce an inaccurate regression line. As a result, predictions for new data will be unreliable, and the model’s performance will decrease while the error (MSE) will increase.