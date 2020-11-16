
import numpy as np

#%%

import pandas as pd


#%%

X_train = pd.read_csv('pre_train_data.csv')

#%%

y_train = pd.read_csv('dataset.csv')

#%%



#%%

y_train = y_train['Disease']

#%%



#%%

from sklearn.tree import DecisionTreeClassifier

#%%

X_train = X_train.drop("Unnamed: 0", axis = 1)

#%%

clf = DecisionTreeClassifier(random_state=0)

#%%

clf.fit(X_train, y_train)

#%%

clf.predict(X_train) == y_train

#%%

X = np.ones(131)

#%%

X = X.reshape(1,-1)

#%%



#%%

clf.predict(X)

#%%

import pickle

#%%

with open("dt.pickle", "wb") as file:
    pickle.dump(clf,file)