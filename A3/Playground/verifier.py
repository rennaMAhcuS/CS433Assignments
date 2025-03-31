from pysat.formula import CNF
from itertools import combinations
import matplotlib.pyplot as plt
import math
import subprocess

def var(i, c, k):
    return i * k + c

def get_results_1D(n, k):

    def get_cnf(n: int, k: int) -> CNF:
        """
        n: number of nodes in graph
        k: number of colors
        """

        cnf = CNF()
        for i in range(n):
            cnf.append([var(i, c, k) for c in range(1, k + 1)])

        for i in range(n):
            for c0, c1 in combinations(range(1, k + 1), 2):
                cnf.append([-var(i, c0, k), -var(i, c1, k)])


        for c in range(0, k + 1):
            for i in range(n):
                for j in range(i, min(i + c + 1, n)):
                    if i == j: continue
                    cnf.append([-var(i, c, k), -var(j, c, k)])

        return cnf
        
    file = f'Z_{n}_{k}'
    cnf = get_cnf(n, k)
    cnf.to_file(f'{file}.cnf')

    result = subprocess.run(['kissat', f'{file}.cnf', f'{file}.drat'], capture_output=True, text=True).stdout

    if 's UNSATISFIABLE' in result.splitlines():
        print('UNSAT')
    else:
        print(result)

    def get_colors(arr, k):
        colors = []
        for var in arr:
            if var <= 0: continue
            colors.append((var - 1) % k + 1)
        return colors

def node_index(i, j):
    res = 2 * (abs(i) + abs(j)) * (abs(i) + abs(j) - 1)
    r = abs(i) + abs(j) - 1
    eta = 0
    if i >= 0 and j >= 0:
        eta = j + 1
    elif i < 0:
        eta = 2 * r + 1 - j
    else:
        eta = 4 * r + 1 + j
    res += eta
    return res + 1

def get_ij(node):
    if node == 1:
        return (0, 0)

    node -= 1
    # Have to find r such that 2r(r + 1) < node <= 2(r + 1)(r + 2)
    if node <= 4:
        return get_ij_from_residual(1, node)

    r = (-1 + math.sqrt(1 + 2 * node)) // 2
    while (2 * r * (r + 1) < node):
        r += 1
    r = int(r)

    residual = node - 2 * r * (r - 1)
    return get_ij_from_residual(r, residual)

def get_ij_from_residual(r, residual):
    """
    Basically that eta
    """
    if residual <= r:
        return (r - residual + 1, residual - 1)
    elif residual > r and residual <= 2 * r:
        residual -= r
        return (-residual + 1, r - residual + 1)
    elif residual > 2 * r and residual <= 3 * r:
        residual -= 2 * r
        return (-r + residual - 1, -residual + 1)
    else:
        residual -= 3 * r
        return (residual - 1, residual - r - 1)

def dist(node1, node2):
    i1, j1 = get_ij(node1)
    i2, j2 = get_ij(node2)
    return abs(i1 - i2) + abs(j1 - j2)  # l1 (Manhattan) Distance

def get_cnf2(r, k, c):
    """
    r: radius of the l1 circle being considered.
    k: number of colors we have
    c: color of (0, 0)
    Return: CNF formula of D_{r, k, c} which is true iff there's a valid packing
    for the circle with k colors with (0, 0) being of color c
    """

    cnf = CNF()

    # Every node has atleast one color
    for node in range(1, 2 * r * (r + 1) + 2):
        cnf.append([var(node, c1, k) for c1 in range(1, k + 1)])
    
    # A node can't have two colors simultaneously
    for node in range(1, 2 * r * (r + 1) + 2):
        for c0, c1 in combinations(range(1, k + 1), 2):
            cnf.append([-var(node, c0, k), -var(node, c1, k)])
    
    # If two nodes have distance d, both can't have same color <= d
    for node1 in range(1, 2 * r * (r + 1) + 2):
        for node2 in range(1, 2 * r * (r + 1) + 2):
            if node1 == node2: continue
            for c1 in range(dist(node1, node2), k + 1):
               cnf.append([-var(node1, c1, k), -var(node2, c1, k)])
    
    cnf.append([var(0, c, k)])
    
    return cnf

def plot_colored_grid(data):
    """
    data: List of (i, j, c) tuples where (i, j) is grid position in (x, y) format and c is the color ID.
    """
    if not data:
        print("No data to plot!")
        return
    
    # Get coordinate limits
    min_x = min(i for i, _, _ in data)
    max_x = max(i for i, _, _ in data)
    min_y = min(j for _, j, _ in data)
    max_y = max(j for _, j, _ in data)
    
    fig, ax = plt.subplots()
    
    # Create color map (each c gets a unique color)
    unique_colors = list(set(c for _, _, c in data))
    cmap = plt.get_cmap("tab10", len(unique_colors))
    
    # Plot each cell
    for x, y, c in data:
        ax.add_patch(plt.Rectangle((x, y), 1, 1, color=cmap(unique_colors.index(c)), ec='black'))
        ax.text(x + 0.5, y + 0.5, str(c), ha='center', va='center', color='white', fontsize=6, weight='bold')
    
    # Set axis limits and properties to match the xy-plane
    ax.set_xticks(range(min_x, max_x + 2))
    ax.set_yticks(range(min_y, max_y + 2))
    ax.set_xlim(min_x, max_x + 1)
    ax.set_ylim(min_y, max_y + 1)
    ax.set_aspect('equal')
    ax.grid(True, which='both', linestyle='-', linewidth=1)
    plt.xticks(range(min_x, max_x + 2))
    plt.yticks(range(min_y, max_y + 2))
    
    plt.show()

def get_results_2D(r, k, c):
    file = f'Z2_{r}_{k}_{c}'
    cnf = get_cnf2(r, k, c)
    cnf.to_file(f'{file}.cnf')

    result = subprocess.run(["kissat", f'{file}.cnf', f'{file}.drat'], capture_output=True, text=True).stdout

    if 's UNSATISFIABLE' in result.splitlines():
        print('UNSAT')
    else:
        print(result)

    # def get_node_color(var, k):
    #     var = var - 1
    #     node_idx, color = var // k, var % k
    #     color += 1
    #     a, b = get_ij(node_idx)
    #     return (a, b, color)

    # arr = []
    # for line in result.splitlines():
    #     if not line.startswith('v'):
    #         continue
    #     arr.extend(list(map(int, line.split()[1:])))

    # # Remove the trailing 0 if present
    # if arr and arr[-1] == 0:
    #     arr = arr[:-1]

    # data = []
    # for elem in arr:
    #     if elem <= 0:
    #         continue
    #     i, j, color = get_node_color(elem, k)
    #     # Only include nodes within distance r from node 1
    #     if dist(1, node_index(i, j)) > r:
    #         continue
    #     data.append((i, j, color))

    # plot_colored_grid(data)

r, k, c = 6, 11, 6
cnf = get_results_2D(r, k, c)
