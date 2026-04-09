import pandas as pd
# Load the file into a "DataFrame" (The industry standard data structure)
df = pd.read_csv("C:/Users/shiva/OneDrive/Desktop/AI-ML/datasets/day03/data.csv")
# Look at the 'Shape' of your data
print("Table Preview:\n", df.head())
# The Magic Command: .describe()
# This instantly gives you the mean, standard deviation, and quartiles.
print("\nStatistical Insights:\n", df.describe())
# Target a specific column for analysis
print(f"\nAverage Score: {df['Score'].mean()}")