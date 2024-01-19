import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import numpy as np
import argparse
import math

ROOT_DIRECTORY = Path(__file__).parent

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

    # Determine the number of variables for each axis
    num_row_vars = math.ceil(num_vars / 2)
    num_col_vars = num_vars // 2

    y_vars = vars[:num_row_vars]  # Variables for y-axis
    x_vars = vars[num_row_vars:]  # Variables for x-axis

    plt.figure(figsize=(8, 6))
    sns.heatmap(kmap_matrix, annot=True, cmap="coolwarm", cbar=False,
                xticklabels=col_labels, yticklabels=row_labels, fmt="d",
                linewidths=.5)

    # Set x and y axis labels to vars
    plt.xlabel(" ".join(x_vars), fontsize=18)
    plt.ylabel(" ".join(y_vars), fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    plt.title(f"Karnaugh Map for {num_vars} variables", fontsize=20)

    # plt.show()

    # Output to image
    plt.savefig(ROOT_DIRECTORY / "frontend" / "build" / "kmap.png", dpi=300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot K-Map")
    parser.add_argument("num_vars", type=int, help="Number of variables")
    parser.add_argument("vars", type=str, nargs="+", help="Variables")
    parser.add_argument("row_labels", type=str, nargs="+", help="Row labels")
    parser.add_argument("col_labels", type=str, nargs="+", help="Column labels")
    parser.add_argument("kmap_matrix", type=str, help="K-Map matrix")
    args = parser.parse_args()

    # Convert the K-Map matrix from a string to a list of integers
    vars = args.vars[0].split("+")
    row_labels = args.row_labels[0].split("+")
    col_labels = args.col_labels[0].split("+")
    kmap_matrix_values = [int(x) for x in args.kmap_matrix.split("+")]
    
    # Reshape the flat matrix into a 2D matrix
    matrix_size = (2 ** (math.ceil(args.num_vars / 2)), 2 ** (math.floor(args.num_vars / 2)))
    kmap_matrix = np.array(kmap_matrix_values).reshape(matrix_size)

    # Plot the K-Map
    plot_kmap(kmap_matrix, row_labels, col_labels, vars)
