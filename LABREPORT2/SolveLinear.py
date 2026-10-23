# SolveLinear.py
# Python module for PHY407
# Paul Kushner, 2015-09-26
# Modifications by Nicolas Grisouard, 2018-09-26
# This module contains useful routines for solving linear systems of equations.
# Based on gausselim.py from Newman
import numpy as np
from numpy import empty, copy 


def GaussElim(A_in, v_in):
    """Implement Gaussian Elimination. This should be non-destructive for input
    arrays, so we will copy A and v to temporary variables
    IN:
    A_in, the matrix to pivot and triangularize
    v_in, the RHS vector
    OUT:
    x, the vector solution of A_in x = v_in """
    # copy A and v to temporary variables using copy command
    A = copy(A_in) * 1.0
    v = copy(v_in) * 1.0
    N = len(v)

    for m in range(N):
        # Divide by the diagonal element
        div = A[m, m] * 1.0
        A[m, :] /= div
        v[m] /= div

        # Now subtract from the lower rows
        for i in range(m+1, N):
            mult = A[i, m]
            A[i, :] -= mult*A[m, :]
            v[i] -= mult*v[m]

    # Backsubstitution
    # create an array of the same type as the input array
    x = empty(N, dtype=v.dtype)
    for m in range(N-1, -1, -1):
        x[m] = v[m]
        for i in range(m+1, N):
            x[m] -= A[m, i]*x[i]
    return x


def PartialPivot(A_in, v_in):
    """ In this function, code the partial pivot (see Newman p. 222) """
    A = copy(A_in) * 1.0 #copy of the matrix, 1.0 is just to make the inputs int he matrix floats
    v = copy(v_in) * 1.0 #copy of the vector on the right hand side Av = but *1.0 makes it floats
    N = len(v) # number of equations

    for m in range(N):
        # Divide by the diagonal element
        p = m + np.argmax(abs(A[m:, m])) #row number of the largest entry in column m at or below row m 
        if p != m: #this is telling us to only swap if there are better rows, p!= m means if p is not equal to m
            A[[m, p], :] = A[[p, m], :] # if thinking this as a linear operator T: V -> W => A[[p,m], :] is our domain and A[[m, p], :] is our target 
            v[[m, p]] = v[[p, m]] # same reasoning as A
        #this is normalizing the pivot row so that the pivot entries become 1
        div = A[m, m] * 1.0 #largest entry in row m with *0.1 making it a float 
        A[m, :] /= div #ddivide in place so that each entry is divided by div 
        v[m] /= div #divided by the same div number 

        # Now subtract from the lower rows
        for i in range(m+1, N): #visits every row below the one just evaluated 
            mult = A[i, m]
            A[i, :] -= mult*A[m, :]
            v[i] -= mult*v[m]

    # Backsubstitution
    # create an array of the same type as the input array
    x = empty(N, dtype=v.dtype)
    for m in range(N-1, -1, -1):
        x[m] = v[m]
        for i in range(m+1, N):
            x[m] -= A[m, i]*x[i]
    return x
    
