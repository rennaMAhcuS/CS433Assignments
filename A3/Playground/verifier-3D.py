from pysat.formula import CNF
import subprocess


def valid_region_centre_3d(x, y, z, r):
    # A valid cross region has the center and all 6 neighbors inside the L1-ball.
    nbrs = [
        (x + 1, y, z),
        (x - 1, y, z),
        (x, y + 1, z),
        (x, y - 1, z),
        (x, y, z + 1),
        (x, y, z - 1),
    ]
    return all(abs(nx) + abs(ny) + abs(nz) <= r for nx, ny, nz in nbrs)


def generate_plus_encoding_3d(r, k, fix_center=None):
    # Build 3D grid: all points (i,j,l) with Manhattan distance <= r.
    grid = [
        (i, j, l)
        for i in range(-r, r + 1)
        for j in range(-r, r + 1)
        for l in range(-r, r + 1)
        if abs(i) + abs(j) + abs(l) <= r
    ]

    # Create variables: each vertex v gets a color c.
    # var[(v, c)] is a positive integer.
    var = {
        (v, c): idx + 1
        for idx, (v, c) in enumerate([(v, c) for v in grid for c in range(1, k + 1)])
    }
    curr_counter = len(var) + 1

    cnf = CNF()

    # 1. Each vertex must get at least one color.
    for v in grid:
        cnf.append([var[(v, c)] for c in range(1, k + 1)])

    # 2. Packing constraints: vertices with the same color c must be > c apart.
    for c in range(1, k + 1):
        for i, v1 in enumerate(grid):
            for v2 in grid[i + 1 :]:
                # If L1 distance <= c, then v1 and v2 cannot both be color c.
                if abs(v1[0] - v2[0]) + abs(v1[1] - v2[1]) + abs(v1[2] - v2[2]) <= c:
                    cnf.append([-var[(v1, c)], -var[(v2, c)]])

    # 3. Plus (cross) encoding for colors > 3.
    r_var = {}
    if k > 3:
        # Collect all cross regions (center + its 6 neighbors) fully inside the grid.
        regions = []
        for v in grid:
            region = [
                v,
                (v[0] + 1, v[1], v[2]),
                (v[0] - 1, v[1], v[2]),
                (v[0], v[1] + 1, v[2]),
                (v[0], v[1] - 1, v[2]),
                (v[0], v[1], v[2] + 1),
                (v[0], v[1], v[2] - 1),
            ]
            valid_region = [u for u in region if u in grid]
            if len(valid_region) == 7:
                regions.append(valid_region)
        current_idx = len(var) + 1
        for c in range(4, k + 1):
            for S in regions:
                r_var[(tuple(S), c)] = current_idx
                current_idx += 1

        # Regional clauses.
        for (S, c), r_idx in r_var.items():
            # (a) Region definition: if r_S,c is true, then at least one vertex in S is colored c.
            cnf.append([-r_idx] + [var[(v, c)] for v in S])
            # (b) Region membership: for each v in S, if v is colored c then r_S,c must be true.
            for v in S:
                cnf.append([r_idx, -var[(v, c)]])
            # (c) Distance constraints: for every vertex v outside S that is too close to all of S.
            for v in grid:
                if v in S:
                    continue
                if all(
                    (abs(v[0] - u[0]) + abs(v[1] - u[1]) + abs(v[2] - u[2])) <= c
                    for u in S
                ):
                    cnf.append([-r_idx, -var[(v, c)]])
            # (d) Inter-region constraints: if two disjoint regions S and S' are so close that every pair (u,v) has distance <= c.
            for (S2, c2), r_idx2 in r_var.items():
                if c == c2 and S != S2:
                    if any(u in S2 for u in S):
                        continue
                    if all(
                        (abs(u[0] - v[0]) + abs(u[1] - v[1]) + abs(u[2] - v[2])) <= c
                        for u in S
                        for v in S2
                    ):
                        cnf.append([-r_idx, -r_idx2])

    # 4. At-Least-One-Distance (alod) clauses:
    # For each vertex v, at least one vertex in its immediate neighborhood (including itself)
    # must be colored 1.
    for v in grid:
        nbrs = [
            v,
            (v[0] + 1, v[1], v[2]),
            (v[0] - 1, v[1], v[2]),
            (v[0], v[1] + 1, v[2]),
            (v[0], v[1] - 1, v[2]),
            (v[0], v[1], v[2] + 1),
            (v[0], v[1], v[2] - 1),
        ]
        valid_nbrs = [n for n in nbrs if n in grid]
        cnf.append([var[(n, 1)] for n in valid_nbrs])

    # 5. Layered symmetry breaking.
    L = min(3, k)
    for layer in range(L):
        c = k - layer
        radius = c // 2
        for i, j, l in grid:
            if abs(i) + abs(j) + abs(l) <= radius:
                cnf.append([-var[((i, j, l), c)]])

    # 6. Optionally, fix the color at the center (0,0,0) to break symmetry.
    if fix_center is not None and (0, 0, 0) in grid and 1 <= fix_center <= k:
        cnf.append([var[((0, 0, 0), fix_center)]])

    return cnf


def run_plus_encoding_3d(r, k, fix_center=None):
    cnf = generate_plus_encoding_3d(r, k, fix_center)
    file_prefix = f"Z3_r{r}_k{k}"
    cnf.to_file(f"{file_prefix}.cnf")

    # Run a SAT solver (e.g., kissat) on the CNF.
    result = subprocess.run(
        ["kissat", f"{file_prefix}.cnf", f"{file_prefix}.drat"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 20:
        print("UNSAT")
    elif result.returncode == 10:
        # Extract solution if needed.
        sol = [
            int(val)
            for line in result.stdout.splitlines()
            if line.startswith("v")
            for val in line.split()
            if val.lstrip("-").isnumeric()
        ]
        if sol and sol[-1] == 0:
            sol.pop()
        print("SAT")
    else:
        print("Solver error.")


# Example usage:
n = int(input("Enter grid radius (r): "))
k = int(input("Enter number of colors (k): "))
# Optionally, fix the center to a specific color (e.g., k//2 or any value between 1 and k).
center_color = None  # Or set to a number, e.g., center_color = k//2
run_plus_encoding_3d(n, k, fix_center=center_color)
