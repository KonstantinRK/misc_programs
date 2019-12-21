import numpy as np

n = 15

D = np.zeros((n,n))
np.fill_diagonal(D,n-1)

A = np.ones((n,n))
np.fill_diagonal(A,0)
X = np.subtract(D,A)

L = X[1:,1:]

K = np.copy(L)
K[0] = K[0] + K[1:].sum(axis=0)
K[1:] += K[0]

print(K)
print(np.linalg.det(L))
print(K.diagonal().prod())
print(np.linalg.det(L)-K.diagonal().prod())



T = np.copy(X)
O = T[0]






