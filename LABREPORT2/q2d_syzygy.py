import numpy as np
import time
from numpy import empty, copy 
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
    

Ns = [1000, 2000, 3000, 4000, 6000, 8000, 10000]
np.random.seed(0)
t_partial = []
t_linalg = []
err_partial_list = []
err_linalg_list = []
with open('q2d_results.txt', 'w') as f:
    f.write('# N  t_partial_ms  t_linalg_ms  err_partial  err_linalg\n')
for N in Ns:
    A = np.random.rand(N, N)
    v = np.random.rand(N)

#partial pivot 
    t_start_part = time.perf_counter()
    x_soln_partialpivot = PartialPivot(A, v)
    t_end_part = time.perf_counter()
    time_ms_partial = (t_end_part - t_start_part) * 1000 #Multiplied by 1000 to get miliseconds which has a higher accuracy
    t_partial.append(time_ms_partial) 
#linalg.solve
    t_start_lin = time.perf_counter()
    x_soln_linalg= np.linalg.solve(A, v)
    t_end_lin = time.perf_counter()
    time_ms_linalg = (t_end_lin - t_start_lin) * 1000 #Multiplied by 1000 to get miliseconds which has a higher accuracy
    t_linalg.append(time_ms_linalg)

#error associated with each method 
    error_partial = np.mean(abs(v - np.dot(A, x_soln_partialpivot)))
    err_partial_list.append(error_partial)
    error_linalg = np.mean(abs(v - np.dot(A, x_soln_linalg)))
    err_linalg_list.append(error_linalg)

    with open('q2d_results.txt', 'a') as f:
        f.write(f'{N} {time_ms_partial:.6e} {time_ms_linalg:.6e} {error_partial:.6e} {error_linalg:.6e}\n')