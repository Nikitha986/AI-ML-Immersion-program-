from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix

actual = [1,1,1,0,0]
predicted = [1,1,0,0,1]

precision = precision_score(actual, predicted)
recall = recall_score(actual, predicted)

tn, fp, fn, tp = confusion_matrix(
    actual,
    predicted
).ravel()

fpr = fp / (fp + tn)

print("Precision:", precision)
print("Recall:", recall)
print("False Positive Rate:", fpr)