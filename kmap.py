import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math

def gray_code(n):
    """Generate Gray code sequence of n bits."""
    if n == 0:
        return ['']
    first_half = gray_code(n - 1)
    second_half = first_half[::-1]
    return ['0' + code for code in first_half] + ['1' + code for code in second_half]

def plot_kmap(kmap_matrix, row_labels, col_labels, vars):
    """Plot the K-Map using Seaborn's heatmap."""
    num_vars = len(vars)
    plt.figure(figsize=(8, 6))
    sns.heatmap(kmap_matrix, annot=True, cmap="coolwarm", cbar=False,
                xticklabels=col_labels, yticklabels=row_labels, fmt="d",
                linewidths=.5)
    
    # Set x and y axis labels to vars
    plt.xlabel(" ".join(vars[math.ceil(num_vars / 2)]))
    plt.ylabel(" ".join(vars[:math.ceil(num_vars / 2):]))
    
    plt.title(f"Karnaugh Map for {num_vars} variables")
    plt.show()

# Get variables and determine the number of variables
vars = input("Enter the variables separated by spaces: ").split()
num_vars = len(vars)

# Generate Gray code labels for minterm inputs
gray_labels = gray_code(num_vars)

# Determine the dimensions of the K-Map
row_size = 2**(math.ceil(num_vars / 2))
col_size = 2**(math.floor(num_vars / 2))

# Initialize K-Map matrix with zeros
kmap_matrix = np.zeros((row_size, col_size), dtype=int)

# Generate the dynamic string for minterm input
dynamic_str = " ".join(gray_labels)

# Ask for minterms
minterms = list(map(int, input(f"Enter the minterms corresponding to {dynamic_str} separated by spaces: ").split()))

# Populate K-Map matrix based on the minterms
for idx, minterm in enumerate(minterms):
    row = idx // col_size
    col = idx % col_size
    kmap_matrix[row][col] = minterm

# Generate Gray code labels for row and column
row_labels = gray_code(math.ceil(num_vars / 2))
col_labels = gray_code(math.floor(num_vars / 2))

# Plot K-Map
plot_kmap(kmap_matrix, row_labels, col_labels, vars)
