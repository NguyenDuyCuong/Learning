import pandas as pd

dataset = pd.read_csv('..\dataset\pima-indians-diabetes.csv', header=0)

# print first 5 rows of data set
print(dataset.head())
