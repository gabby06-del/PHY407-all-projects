import numpy as np
import matplotlib.pyplot as plt

N = np.array([100, 500, 1000])
loops = [0.544, 67.34, 542.90]
dots = [0.00066, 0.00198, 0.00664]

# Store the combinations to loop through them cleanly
x_data = [N, N**3, N, N**3]
y_data = [loops, loops, dots, dots]
titles = ["Loops vs N", "Loops vs N^3", "np.dot vs N", "np.dot vs N^3"]

for i in range(4):
    plt.subplot(2, 2, i + 1)
    plt.plot(x_data[i], y_data[i], "o-", color="blue" if i < 2 else "orange")
    plt.title(titles[i])
    plt.grid(True)

plt.tight_layout()
plt.show()
plt.savefig("plot for 1")


