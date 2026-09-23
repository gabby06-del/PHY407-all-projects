import time
import numpy as np
import matplotlib.pyplot as plt
import sys


size_min = 2
size_max = 30

#N = int(sys.argv[1])
N=25
def matrix_multiplication(A, B):
    N = len(A[0])
    C = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            for k in range(N):
                C[i,j] += A[i,k] * B[k,j]
    return C



    # Create constant random matrices
A = np.random.random((N, N))
B = np.random.random((N, N))
    
    # 1. Time the loop method
t_start = time.time()
C_loop = matrix_multiplication(A, B)
t_end = time.time()
loop_duration_manual=t_end - t_start
print("time in seconds for N= " , N, "with loops: ",  loop_duration_manual)
    
    # 2. Time the dot method
t_start_dot = time.time()
C_dot = np.dot(A, B)
t_end_dot = time.time()
dot_duration_manual=t_end_dot - t_start_dot
   

print("time in seconds for N= " , N, "with dot: ", dot_duration_manual)

