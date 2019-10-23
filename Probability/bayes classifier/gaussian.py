# Import packages
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn import metrics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()
# Import data
training = pd.read_csv('data/iris_train.csv')
test = pd.read_csv('data/iris_test.csv')

# Create the X, Y, Training and Test
xtrain = training.drop('Species', axis=1)
ytrain = training.loc[:, 'Species']
xtest = test.drop('Species', axis=1)
ytest = test.loc[:, 'Species']

# Visualizing the distribution of a dataset
# sns.distplot(xtrain.iloc[:, 0], rug=True)
# plt.show()
# sns.pairplot(xtrain)
# plt.show()
# sns.jointplot(x="Sepal.Length", y="Sepal.Width", data=xtrain, kind="hex")
# plt.show()
# sns.jointplot(x="Petal.Length", y="Petal.Width", data=xtrain, kind="kde")
# plt.show()

# Init the Gaussian Classifier
model = GaussianNB()

# Train the model
model.fit(xtrain, ytrain)

# Predict Output
pred = model.predict(xtest)
print("Accuracy:", metrics.accuracy_score(ytest, pred))

# Plot Confusion Matrix
mat = confusion_matrix(pred, ytest)
names = np.unique(pred)
sns.heatmap(mat, square=True, annot=True, fmt='d', cbar=False,
            xticklabels=names, yticklabels=names)
plt.xlabel('Truth')
plt.ylabel('Predicted')
plt.show()
