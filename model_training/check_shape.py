import numpy as np

X_train = np.load("X_train.npy", allow_pickle=True)  # Load with allow_pickle=True
print(type(X_train))
print(X_train.dtype)
