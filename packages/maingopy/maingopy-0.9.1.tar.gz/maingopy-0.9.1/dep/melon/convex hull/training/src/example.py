#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 02:57:11 2020

@author: christian
"""
from scipy.spatial import ConvexHull
import numpy as np
import json
import os
import matplotlib.pyplot as plt

def main(): 
    X= np.array([[1,1],[2,3],[-1,1],[10,2]])
    hull = ConvexHull(X)

    input_dim = X.shape[1]
    
    hull_pts = []
    for simplex in hull.simplices:
        hull_pts += list(X[simplex])
    hull_pts = np.array(hull_pts)
    
    u_c = np.mean(hull_pts, axis = 0,keepdims = True).transpose()
    A = hull.equations[:,:input_dim]
    b = hull.equations[:,input_dim:]
    
    res = np.matmul(A,u_c)+b # assert that A*u_c+b <= 0
                             # see https://www.sciencedirect.com/science/article/abs/pii/S0255270107001134
    for r in res:
        assert(r[0]<0)

 

    data_out = {"A": [list(a) for a in A], "b": [_b[0] for _b in b]}
    if not os.path.exists("ExamplePath"):
        os.mkdir(os.path.join("ExamplePath"))
    with open(os.path.join("ExamplePath", 'convex_hull.json'), 'w') as f:
        json.dump(data_out, f)
    plt.figure()
    plt.scatter(X[:,0],X[:,1])
    for simplex in hull.simplices:
        plt.plot(X[simplex, 0], X[simplex,1], "k-")
    plt.show()

    c = np.matmul(A,np.ones((2,1))) + b
    print(c)

if __name__ == "__main__":
    main()