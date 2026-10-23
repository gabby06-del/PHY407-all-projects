import numpy as np 

def anotherCircuitMatrix(N_in):
    A = np.zeros([N_in, N_in], float)
    diagonal = np.ones(N_in, float) *4.0
    diagonal[0] = 3.0 
    diagonal[N_in-1] = 3.0 
    A+= np.diag(diagonal)
    minusOnes = np.ones(N_in-1, float)* -1.0
    A+= np.diag(minusOnes, 1)
    A+= np.diag(minusOnes, -1)
    minusOnes = np.ones(N_in-2, float)* -1.0
    A+= np.diag(minusOnes, 2)
    A+= np.diag(minusOnes, -2)
    return A

def wRHS(N_in, v_in=5.0):
    RHS = np.zeros(N_in, float)
    RHS[0] = v_in
    RHS[1] = v_in
    return RHS

from scipy.linalg import solve_banded
c = anotherCircuitMatrix(6)
print(c)
print (" Another circuit matrix for N=6", c)
c = anotherCircuitMatrix(100)
print(c)
print (" Another circuit matrix for N=100", c)



def bandedCircuitMatrix(N_in):
    ab = np.zeros([5,N_in], float)
    
    # All diagonal elements = 4, except first and last which are 3
    diagonal = np.ones(N_in, float) * 4.0
    diagonal[0] = 3.0
    diagonal[N_in-1] = 3.0
    ab[2] = diagonal

    # the two upper and two lower off-diagonals
    offdiag1 = np.ones(N_in, float) * -1.0
    ab[0] = offdiag1
    ab[1] = offdiag1
    ab[3] = offdiag1
    ab[4] = offdiag1
    
    return ab

# Sanity check, to see it gives the same answer with N=6 as we got in the previous part
C=bandedCircuitMatrix(6)
w=wRHS(6)
solve_banded((2,2),C,w)
print (" Banded circuit matrix for N=6", c)
print ("For wRHS for N=6", w)

C=bandedCircuitMatrix(100)
w=wRHS(100)
solve_banded((2,2),C,w)
print (" Banded circuit matrix for N=100", c)
print ("For wRHS for N=100", w)
C=bandedCircuitMatrix(3000)
w=wRHS(3000)
solve_banded((2,2),C,w)

print (" Banded circuit matrix for N=3000", c)
print ("For wRHS for N=3000", w)
