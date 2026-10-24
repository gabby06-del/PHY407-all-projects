from gauss import gaussxw, gaussxwab
import numpy as np 
from numpy import digitize, ones, copy, cos, tan, pi, linspace

#a. 
m = 1.0 
k = 12.0 
c = 3e8 
def g(x, x0):
    a = 0.5 * k * (x0**2 - x**2)       
    return c * np.sqrt(a * (2*m*c**2 + a)) / (m*c**2 + a)

def period(x0, N):
    x, w = gaussxwab(N, 0, x0)
    return sum(4 * w / g(x, x0))

T8= period(0.01, 8)
print("T for N = 16:", T8)
T16 = period(0.01, 16)
print("T for N = 16:", T16)

frac_e_est = abs(T16-T8)/T16

print("Fractional error estimate:", frac_e_est)

# b. 

import matplotlib.pyplot as plt 

x0 = 0.01 
fig, axs = plt.subplots(1, 2)
for N in (8, 16):
    x, w = gaussxwab(N, 0, x0)
    axs[0].plot(x, 4/g(x, x0), '--', label=f'N={N}')
    axs[1].plot(x, 4*w/g(x, x0), '-', label=f'N={N}')

axs[0].set_xlabel('x_k (m)'); axs[0].set_ylabel('4/g_k'); axs[0].set_title('integrand')
axs[1].set_xlabel('x_k (m)'); axs[1].set_ylabel('4 w_k/g_k'); axs[1].set_title('weighted values')
for ax in axs:
    ax.legend()
plt.tight_layout()
plt.savefig('q1b.png')
plt.show()

#c. 

xc= c* np.sqrt(m/k)
print(T16)
x0s = np.linspace(1, 10*xc, 60)
T = np.array([period(x0, 16) for x0 in x0s])
T_classical = 2*np.pi*np.sqrt(m/k) * np.ones_like(x0s)
T_relativistic = 4*x0s/c


plt.figure()
plt.plot(x0s, T, '.', label='Gaussian quadrature (N=16)', color='pink')
plt.plot(x0s, T_classical, '-', label='Classical', color='purple')
plt.plot(x0s, T_relativistic, '--', label='Relativistic', color='#D0F0C0')
plt.axvline(xc, color='gray', ls=':', label='$x_c$')
plt.xlabel('$x_0$ (m)'); plt.ylabel('T (s)')
plt.legend()
plt.savefig('q1c.png')
plt.show()