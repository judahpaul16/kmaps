from sympy import symbols, sympify, simplify_logic, Not, And, Or, Xor, Nand, Nor, Implies, Equivalent, ITE
from sympy.parsing.sympy_parser import parse_expr
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import numpy as np
import argparse
import sympy
import math
import re

# Path to the root directory
ROOT_DIRECTORY = Path(__file__).resolve().parent

# Helper function to generate Gray code sequence of n bits
def gray_code(n):
    if n == 0:
        return ['']
    first_half = gray_code(n - 1)
    second_half = first_half[::-1]
    return ['0' + code for code in first_half] + ['1' + code for code in second_half]

# Function to order Gray code for Karnaugh map indices
def order_gray_code(num_vars):
    gray_codes = gray_code(num_vars)
    rows = 2 ** math.ceil(num_vars / 2)
    cols = 2 ** math.floor(num_vars / 2)
    gray_order = np.zeros((rows, cols), dtype=int)
    binary_to_gray = {i: int(code, 2) for i, code in enumerate(gray_codes)}
    reflected_binary_row_values = [binary_to_gray[i] for i in range(rows)]
    standard_binary_col_values = [binary_to_gray[i] for i in range(cols)]
    for row in range(rows):
        for col in range(cols):
            combined_gray_value = (reflected_binary_row_values[row] << math.floor(num_vars / 2)) | standard_binary_col_values[col]
            gray_order[row, col] = gray_codes.index(bin(combined_gray_value)[2:].zfill(num_vars))
    return gray_order

# Function to find optimal groupings for Karnaugh map
def find_valid_groupings(kmap_matrix, sop_or_pos):
    rows, cols = kmap_matrix.shape
    valid_groupings = []
    visited = np.zeros_like(kmap_matrix, dtype=bool)  # Keep track of visited cells

    # Potential group sizes in descending order
    group_sizes = [(2, 4), (4, 2), (2, 2), (1, 4), (4, 1), (1, 2), (2, 1), (1, 1)]

    # If SOP, find 1s. If POS, find 0s
    if sop_or_pos == "sop":
        row_indices, col_indices = np.where(kmap_matrix == 1)
    elif sop_or_pos == "pos":
        row_indices, col_indices = np.where(kmap_matrix == 0)

    # Check if the cells are valid for grouping
    def check_group(row, col, size):
        r_size, c_size = size
        for i in range(r_size):
            for j in range(c_size):
                if visited[(row + i) % rows][(col + j) % cols] or kmap_matrix[(row + i) % rows][(col + j) % cols] != kmap_matrix[row][col]:
                    return False
        return True

    # Mark the grouped cells as visited
    def mark_visited(row, col, size):
        r_size, c_size = size
        for i in range(r_size):
            for j in range(c_size):
                visited[(row + i) % rows][(col + j) % cols] = True

    # Find groupings
    for row, col in zip(row_indices, col_indices):
        for size in group_sizes:
            r_size, c_size = size
            if check_group(row, col, size):
                valid_groupings.append((row, col, r_size, c_size))
                mark_visited(row, col, size)
                break

    return valid_groupings

def get_equation(grouping, vars):
    row, col, height, width = grouping
    terms = []
    num_vars = len(vars)
    row_vars_count = math.ceil(num_vars / 2)
    col_vars_count = num_vars - row_vars_count
    row_vars = vars[:row_vars_count]
    col_vars = vars[row_vars_count:]
    gray_order = order_gray_code(num_vars)
    
    # Helper function to convert binary to Gray code
    def binary_to_gray(binary):
        binary = int(binary, 2)
        gray = binary ^ (binary >> 1)
        return format(gray, '0' + str(num_vars) + 'b')

    # Helper function to get the binary representation of the Gray code index
    def gray_index_to_binary(index, num_vars):
        binary = format(index, '0' + str(num_vars) + 'b')
        gray = binary_to_gray(binary)
        return gray

    # Determine which variables are constant across the entire grouping
    for var_idx, var in enumerate(row_vars + col_vars):
        if var_idx < len(row_vars):  # Row variable
            group_range = [gray_order[(row + i) % (2 ** row_vars_count), 0] for i in range(height)]
        else:  # Column variable
            group_range = [gray_order[0, (col + i) % (2 ** col_vars_count)] for i in range(width)]
        
        # Convert Gray code indices to binary and check if variable is constant
        var_constant = True
        first_value = None
        for gray_index in group_range:
            binary_value = gray_index_to_binary(gray_index, num_vars)
            value = binary_value[var_idx]
            if first_value is None:
                first_value = value
            elif first_value != value:
                var_constant = False
                break
        
        # If variable is constant, determine if it's 0 or 1 and add to terms
        if var_constant:
            if first_value == '1':
                terms.append(var)
            else:
                terms.append(f"{var}'")

    return ' & '.join(terms)

def simplify_equation(equation, sop_or_pos):
    # print(equation)
    # Parse the string into a sympy expression
    equation = re.sub(r"\+", r"|", equation) # Replace + with |
    equation = re.sub(r"([a-zA-Z])'?([a-zA-Z])'?", r"\1 & \2", equation) # Place & between all variables
    equation = re.sub(r"\)\(", r" & ", equation)
    equation = re.sub(r"([a-zA-Z])'", r"~\1", equation) # Replace ' with ~
    equation = re.sub(r"([a-zA-Z])~?([a-zA-Z])", r"\1 & \2", equation)
    equation = re.sub(r"\(", r"", equation) # Remove (
    equation = re.sub(r"\)", r"", equation) # Remove )
    # print(equation)

    expr = parse_expr(equation)

    # Simplify the expression using sympy's simplify_logic function
    if sop_or_pos == "sop":
        simplified_expr = simplify_logic(expr, form='dnf')
    elif sop_or_pos == "pos":
        simplified_expr = simplify_logic(expr, form='cnf')
        # apply De Morgan's law
        simplified_expr = apply_demorgans_law(simplified_expr)
    
    # Convert the sympy expression back to a string
    simplified_str = str(simplified_expr)
    simplified_str = re.sub(r"~([a-zA-Z])", r"\1'", simplified_str)
    simplified_str = re.sub(r"\|", r"+", simplified_str)
    simplified_str = re.sub(r"&", r")(", simplified_str)
    simplified_str = re.sub(r"([a-zA-Z]) & ([a-zA-Z])", r"\1\2", simplified_str)
    simplified_str = re.sub(r"\(", r"", simplified_str)
    simplified_str = re.sub(r"\)", r"", simplified_str)
    simplified_str = re.sub(r"([a-zA-Z]) +([a-zA-Z])", r"\1\2", simplified_str)
    
    return simplified_str
    
def apply_demorgans_law(equation):
    # print(equation)
    # print(equation.__class__)
    if isinstance(equation, And):
        args = list(equation.args)
        for i in range(len(args)):
            args[i] = apply_demorgans_law(args[i])
        return Or(*args)
    elif isinstance(equation, Or):
        args = list(equation.args)
        for i in range(len(args)):
            args[i] = apply_demorgans_law(args[i])
        return And(*args)
    elif isinstance(equation, Not):
        return equation.args[0]
    elif isinstance(equation, sympy.core.symbol.Symbol):
        return Not(equation)
    else:
        return equation

# Plot the K-map with highlighted groupings
def plot_kmap(kmap_matrix, row_labels, col_labels, vars, sop_or_pos):
    num_vars = len(vars)
    num_row_vars = math.ceil(num_vars / 2)
    num_col_vars = num_vars // 2
    y_vars = vars[:num_row_vars]
    x_vars = vars[num_row_vars:]
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(kmap_matrix, annot=True, cmap="coolwarm", cbar=False,
                xticklabels=col_labels, yticklabels=row_labels, fmt="d",
                linewidths=.5, ax=ax)

    # Find and highlight the groupings
    groupings = find_valid_groupings(kmap_matrix, sop_or_pos)
    colors = ['green', 'blue', 'yellow', 'purple']
    for idx, (row, col, height, width) in enumerate(groupings):
        color = colors[idx % len(colors)]  # Cycle through colors
        ax.add_patch(Rectangle((col, row), width, height, fill=None,
                               linewidth=2 * math.sqrt(height + width),
                               edgecolor=color))
        
    # Define the equations for the groupings in legend corresponding to the colors
    equations = [eq for eq in [get_equation(grouping, vars) for grouping in groupings]]
    # Plot the empty lines with corresponding colors and labels
    for i in range(len(groupings)):
        plt.plot([], [], color=colors[i % len(colors)], label=equations[i])

    if sop_or_pos == "sop":
        equation = " + ".join(equations)
    elif sop_or_pos == "pos":
        equation = ") + (".join(equations)

    simplified_equation = simplify_equation(equation, sop_or_pos)

    # Display the simplified equation
    plt.text(0.666, 1.25 * kmap_matrix.shape[0], f"Equation: {simplified_equation}", fontsize=20)

    plt.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', borderaxespad=0., fontsize=18)
    plt.xlabel(" ".join(x_vars), fontsize=18)
    plt.ylabel(" ".join(y_vars), fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.title(f"Karnaugh Map for {num_vars} variables", fontsize=20)
    plt.tight_layout()

    # Output to image
    plt.savefig(ROOT_DIRECTORY / "frontend" / "build" / "kmap.png", dpi=300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot K-Map")
    parser.add_argument("vars", type=str, nargs="+", help="Variables")
    parser.add_argument("row_labels", type=str, nargs="+", help="Row labels")
    parser.add_argument("col_labels", type=str, nargs="+", help="Column labels")
    parser.add_argument("kmap_matrix", type=str, help="K-Map matrix")
    parser.add_argument("sop_or_pos", type=str, help="SOP or POS")
    args = parser.parse_args()

    # Convert the K-Map matrix from a string to a list of integers
    vars = args.vars[0].split("+")
    num_vars = len(vars)
    row_labels = args.row_labels[0].split("+")
    col_labels = args.col_labels[0].split("+")
    kmap_matrix_values = [int(x, 2) for x in args.kmap_matrix.split("+")]
    sop_or_pos = args.sop_or_pos

    # Create an empty K-Map matrix
    matrix_size = (2 ** (math.ceil(num_vars / 2)), 2 ** (math.floor(num_vars / 2)))
    kmap_matrix = np.zeros(matrix_size, dtype=int)

    # Fill in the K-Map matrix
    gray_order = order_gray_code(num_vars)
    for i in range(len(kmap_matrix_values)):
        kmap_matrix[gray_order == i] = kmap_matrix_values[i]

    # Plot the K-Map
    plot_kmap(kmap_matrix, row_labels, col_labels, vars, sop_or_pos)
