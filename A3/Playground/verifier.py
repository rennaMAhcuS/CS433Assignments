from pysat.formula import CNF
import subprocess
import sys
import matplotlib.pyplot as plt


def valid_region_centre(x, y, r):
    return (
        abs(x + 1) + abs(y) <= r
        and abs(x - 1) + abs(y) <= r
        and abs(x) + abs(y + 1) <= r
        and abs(x) + abs(y - 1) <= r
    ) and (
        int((2 * y - x) / 5) == (2 * y - x) / 5
        and int((2 * x - y) / 5) == (2 * x - y) / 5
    )


def give_region_for_node(x, y, r):
    if valid_region_centre(x + 1, y, r):
        return (x + 1, y)
    elif valid_region_centre(x - 1, y, r):
        return (x - 1, y)
    elif valid_region_centre(x, y + 1, r):
        return (x, y + 1)
    elif valid_region_centre(x, y - 1, r):
        return (x, y - 1)
    else:
        return None


def generate_plus_encoding(r, k):
    # Create grid points within Manhattan distance r from center
    curr_counter = 1
    grid = [
        (i, j)
        for i in range(-r, r + 1)
        for j in range(-r, r + 1)
        if abs(i) + abs(j) <= r
    ]

    # Create variables: x_v,c = 1 iff vertex v has color c
    var = {
        (v, c): i + 1
        for i, (v, c) in enumerate([(v, c) for v in grid for c in range(1, k + 1)])
    }
    curr_counter += len(var)
    r_Si_ci = {}
    for node in grid:
        if valid_region_centre(node[0], node[1], r):
            r_Si_ci[node] = curr_counter
            curr_counter += 1

    cnf = CNF()

    # Each vertex must have exactly one color
    for v in grid:
        cnf.append([var[(v, c)] for c in range(1, k + 1)])

    # Packing constraints (direct encoding for all colors)
    for c in range(1, k + 1):
        min_distance = c  # vertices with color c must be ≥ c+1 apart
        for i, v1 in enumerate(grid):
            for v2 in grid[i + 1 :]:
                if abs(v1[0] - v2[0]) + abs(v1[1] - v2[1]) <= min_distance:
                    cnf.append([-var[(v1, c)], -var[(v2, c)]])

    # Plus encoding for colors > 3 (if applicable)
    r_var = {}  # Initialize empty dict to avoid UnboundLocalError
    if k > 3:
        # Define '+' shaped regions (D1 neighborhoods)
        regions = []
        for v in grid:
            region = [
                v,
                (v[0] + 1, v[1]),
                (v[0] - 1, v[1]),
                (v[0], v[1] + 1),
                (v[0], v[1] - 1),
            ]
            # Filter to only include valid grid points
            valid_region = [u for u in region if u in grid]
            if len(valid_region) == 5:  # Only add complete '+' regions
                regions.append(valid_region)

        # Create regional variables r_S,c
        current_idx = len(var) + 1  # Start after existing vertex-color variables

        for c in range(4, k + 1):
            for S in regions:
                r_var[(tuple(S), c)] = current_idx
                current_idx += 1  # Increment for the next variable

        # Add regional clauses
        for (S, c), var_idx in r_var.items():
            # Region definition: if r_S,c is true, at least one v in S has color c
            cnf.append([-var_idx] + [var[(v, c)] for v in S])

            # Region membership: if v in S has color c, then r_S,c must be true
            for v in S:
                cnf.append([var_idx, -var[(v, c)]])

                # Distance constraints for regional variables
                for v in grid:
                    if v in S:
                        continue
                    if all(abs(v[0] - u[0]) + abs(v[1] - u[1]) < c + 1 for u in S):
                        cnf.append([-var_idx, -var[(v, c)]])

            # Inter-region constraints
            for (S2, c2), var_idx2 in r_var.items():
                if c == c2 and S != S2:
                    overlap = any(v in S2 for v in S)
                    if overlap:
                        continue
                    if all(
                        abs(u[0] - v[0]) + abs(u[1] - v[1]) < c + 1
                        for u in S
                        for v in S2
                    ):
                        cnf.append([-var_idx, -var_idx2])

    # At-Least-One-Distance (alod) clauses
    for v in grid:
        neighbors = [
            v,
            (v[0] + 1, v[1]),
            (v[0] - 1, v[1]),
            (v[0], v[1] + 1),
            (v[0], v[1] - 1),
        ]
        valid_nbrs = [n for n in neighbors if n in grid]
        cnf.append([var[(n, 1)] for n in valid_nbrs])

    # Layered symmetry breaking (for colors k, k-1, ..., k-L+1)
    L = min(3, k)  # Number of symmetry breaking layers
    for layer in range(L):
        c = k - layer
        radius = c // 2
        for i, j in grid:
            if abs(i) + abs(j) <= radius:
                if i < 0 or j < i:  # Outside N-N-E octant
                    cnf.append([-var[(i, j), c]])

    return cnf


def run_plus_encoding(r, k, plot=False):
    cnf = generate_plus_encoding(r, k)

    file = f"Z2_r{r}_k{k}"

    def result_plotter(k, result):
        pass

    # Write to DIMACS format
    cnf.to_file(f"{file}.cnf")
    kissat_run = subprocess.run(
        ["kissat", f"{file}.cnf", f"{file}.drat"], capture_output=True, text=True
    )

    if kissat_run.returncode == 20:
        print("UNSAT")
    elif kissat_run.returncode == 10:
        print("SAT")
        if plot:
            result = [
                int(val)
                for line in kissat_run.stdout.splitlines()
                if line.startswith("v")
                for val in line.split()
                if val.lstrip("-").isnumeric()
            ]
            if result[-1] == 0:
                result.pop()
            result_plotter(k, result)
    else:
        print("Some error occured.")


# Example usage:
n = int(input("Enter grid radius (r): "))
k = int(input("Enter number of colors (k): "))
run_plus_encoding(n, k)
