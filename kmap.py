import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import subprocess
import math

ROOT_DIRECTORY = Path(__file__).parent

def gray_code(n):
    """Generate Gray code sequence of n bits."""
    if n == 0:
        return ['']
    first_half = gray_code(n - 1)
    second_half = first_half[::-1]
    return ['0' + code for code in first_half] + ['1' + code for code in second_half]

async def plot_kmap(kmap_matrix, row_labels, col_labels, vars):
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
    
    # plt.show()

    # Output to image
    plt.savefig(ROOT_DIRECTORY / "frontend" / "build" / "kmap.png", dpi=300)


