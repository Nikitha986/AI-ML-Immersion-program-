import numpy as np
# Create a 1D Array
data_points = np.array([10, 20, 30, 40])
# Reshaping: Changing the 'View' of data (e.g., turning a line into a square)
# This is how AI reshapes image pixels to be read by a model.
matrix = data_points.reshape(2, 2)
print("Data Reshaped into 2x2 Matrix:\n", matrix)
# Scaling: Doubling all values instantly without a loop
processed_data = data_points * 2
print("Scaled Data (All values doubled):", processed_data)