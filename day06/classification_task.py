import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
# Dataset: Hours Slept & Coffee Drank vs Pass/Fail (1=Pass,0=Fail)
data = {
'Hours_Sleep': [8, 7, 6, 5, 8, 4, 9, 5, 6, 4],
'Coffee_Cups': [1, 2, 2, 4, 0, 5, 1, 4, 3, 6],
'Passed': [1, 1, 1, 0, 1, 0, 1, 0, 0, 0]
}
df = pd.DataFrame(data)
X = df[['Hours_Sleep', 'Coffee_Cups']]
y = df['Passed']
# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y,
test_size=0.2, random_state=42)
# Train the Classifier
clf = LogisticRegression()
clf.fit(X_train, y_train)
print("Model Prediction for Test Data:", clf.predict(X_test))

from sklearn.metrics import confusion_matrix,classification_report
import seaborn as sns
import matplotlib.pyplot as plt
y_pred = clf.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()
print(classification_report(y_test, y_pred))

# The 'coefficients' tell us the importance of each feature
importance = clf.coef_[0]
for i, v in enumerate(importance):
    print(f'Feature: {X.columns[i]}, Score: {v:.4f}')

