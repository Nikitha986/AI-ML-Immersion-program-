# --- 1. DATA CONTAINERS ---
# How we store information for the model to read.
name = "Developer_Alpha" # String (Labels/Names)
age = 24 # Integer (Discrete data)
marks = [85, 92, 78, 95, 88] # List (A 'Vector' of data points)
# --- 2. THE PROCESSING LOOP ---
# AI models iterate over thousands of rows. This is how that starts:
for i in marks:
    print(f"Validating Data Point: {i}")
# --- 3. ANALYTICAL FUNCTIONS ---
def analyze_numbers(numbers):
    """Calculates key statistics used in Data Science."""
    min_val = min(numbers)
    max_val = max(numbers)
    avg_val = sum(numbers) / len(numbers)
    return min_val, max_val, avg_val
# Running the Analysis
results = analyze_numbers(marks)
print(f"\n--- Statistics Report ---")
print(f"Low: {results[0]} | High: {results[1]} | Average: {results[2]}")