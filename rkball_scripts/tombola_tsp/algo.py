import heapq
import numpy as np

def mst_prim(w):
    n = w.shape[0]
    A = np.full(n, np.inf)
    Q = heapq.PriorityQueue(n)
    data_list = []
    for i in range(n):
        data = (i,A[i])
        data_list[i]=data
        Q.put(data)
    S = {}
    while Q.full():
        v = Q.get()
        S = S + {v}
        for u in range(n):
            if u not in S and w[v][u]<A[u]:
                A[u]=w[v][u]


