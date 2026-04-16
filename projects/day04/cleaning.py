import pandas as pd
df = pd.read_csv("C:/Users/shiva/OneDrive/Desktop/AI-ML/datasets/day04/data.csv")
# 1. IDENTIFY: Where are the holes?
print("Missing Values:\n", df.isnull().sum())
# 2. FIX: Fill missing Age with the Average (Mean)
# This is called 'Imputation'
df['Age'] = df[' Age'].fillna(df[' Age'].mean())
# 3. FIX: Fill missing Score with a default value (e.g., 0)
df['Score'] = df[' Score'].fillna(0)
print("\nCleaned Data:\n", df)

from sklearn.preprocessing import MinMaxScaler
import numpy as np
# Sample data: [Age, Salary]
data = np.array([[22, 50000], [45, 120000], [30, 80000]])
# Initialize the Scaler to put everything between 0 and 1
scaler = MinMaxScaler()
# Transform the data
scaled_data = scaler.fit_transform(data)
print("Original Data:\n", data)
print("\nScaled Data (Everything is now 0 to 1):\n", scaled_data)

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
# Let's create a quick correlation map
# This shows how much 'Age' affects 'Score'
data = {'Age': [21, 22, 23, 24, 25], 'Score': [80, 82, 88, 92, 95]}
df = pd.DataFrame(data)
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')

plt.title("Feature Correlation Map")
plt.show()

