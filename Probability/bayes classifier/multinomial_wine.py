# Import packages
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn import metrics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets


sns.set()
# Load dataset
wine = datasets.load_wine()
print(wine['data'])
data = StandardScaler().fit_transform(wine['data'])
print(data)
print(wine['target'])
print(wine['feature_names'])
print(wine['target_names'])

X_train, X_test, y_train, y_test = train_test_split(
    wine['data'], wine['target'], test_size=0.3, random_state=109)

model = MultinomialNB()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
