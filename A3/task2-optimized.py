from pysat.formula import CNF
import subprocess
import sys
import matplotlib.pyplot as plt

def valid_region_centre_3d(x, y, z, r):
    # A valid cross region has the center and all 6 neighbors inside the L1-ball.
    nbrs = [(x+1,y,z), (x-1,y,z), (x,y+1,z), (x,y-1,z), (x,y,z+1), (x,y,z-1)]
    return all(abs(nx) + abs(ny) + abs(nz) <= r for nx,ny,nz in nbrs)

def generate_amod_clauses(grid, var, k):
    # For each color, precompute possible offsets with L1 norm in [1, c]
    clauses = []
    for c in range(1, k+1):
        offsets = [(dx,dy,dz) for dx in range(-c, c+1)
                             for dy in range(-c, c+1)
                             for dz in range(-c, c+1)
                             if 1 <= abs(dx)+abs(dy)+abs(dz) <= c]
        seen = set()  # To avoid duplicate clauses
        for dx, dy, dz in offsets:
            for v in grid:
                v2 = (v[0]+dx, v[1]+dy, v[2]+dz)
                if v2 in grid:
                    # Order vertices to add each pair only once.
                    if v < v2 and ((v, v2, c) not in seen):
                        clauses.append([-var[(v, c)], -var[(v2, c)]])
                        seen.add((v, v2, c))
    return clauses



def generate_plus_encoding_3d(r, k, fix_center=None):
    grid = [(i, j, l) for i in range(-r, r+1)
                     for j in range(-r, r+1)
                     for l in range(-r, r+1)
                     if abs(i)+abs(j)+abs(l) <= r]
    var = { (v, c): idx+1 for idx, (v, c) in enumerate([(v, c) for v in grid for c in range(1, k+1)]) }
    curr_counter = len(var) + 1
    cnf = CNF()

    # 1. Each vertex gets at least one color.
    for v in grid:
        cnf.append([var[(v, c)] for c in range(1, k+1)])

    # 2. Packing constraints using the new offset-based amod clause generation.
    for clause in generate_amod_clauses(grid, var, k):
        cnf.append(clause)

    # (The rest of the plus encoding remains unchanged.)
    # 3. Plus (cross) encoding for colors > 3.
    r_var = {}
    if k > 3:
        regions = []
        for v in grid:
            region = [v,
                      (v[0]+1, v[1], v[2]),
                      (v[0]-1, v[1], v[2]),
                      (v[0], v[1]+1, v[2]),
                      (v[0], v[1]-1, v[2]),
                      (v[0], v[1], v[2]+1),
                      (v[0], v[1], v[2]-1)]
            valid_region = [u for u in region if u in grid]
            if len(valid_region) == 7:
                regions.append(valid_region)
        current_idx = len(var) + 1
        for c in range(4, k+1):
            for S in regions:
                r_var[(tuple(S), c)] = current_idx
                current_idx += 1
        for (S, c), r_idx in r_var.items():
            cnf.append([-r_idx] + [var[(v, c)] for v in S])
            for v in S:
                cnf.append([r_idx, -var[(v, c)]])
            for v in grid:
                if v in S:
                    continue
                if all((abs(v[0]-u[0]) + abs(v[1]-u[1]) + abs(v[2]-u[2])) <= c for u in S):
                    cnf.append([-r_idx, -var[(v, c)]])
            for (S2, c2), r_idx2 in r_var.items():
                if c == c2 and S != S2:
                    if any(u in S2 for u in S):
                        continue
                    if all((abs(u[0]-v[0]) + abs(u[1]-v[1]) + abs(u[2]-v[2])) <= c for u in S for v in S2):
                        cnf.append([-r_idx, -r_idx2])
    
    # 4. At-Least-One-Distance clauses.
    for v in grid:
        nbrs = [v,
                (v[0]+1, v[1], v[2]),
                (v[0]-1, v[1], v[2]),
                (v[0], v[1]+1, v[2]),
                (v[0], v[1]-1, v[2]),
                (v[0], v[1], v[2]+1),
                (v[0], v[1], v[2]-1)]
        valid_nbrs = [n for n in nbrs if n in grid]
        cnf.append([var[(n, 1)] for n in valid_nbrs])
    
    # 5. Layered symmetry breaking.
    L = min(3, k)
    for layer in range(L):
        c = k - layer
        radius = c // 2
        for (i, j, l) in grid:
            if abs(i)+abs(j)+abs(l) <= radius:
                cnf.append([-var[((i, j, l), c)]])
    
    if fix_center is not None and (0,0,0) in grid and 1 <= fix_center <= k:
        cnf.append([var[((0,0,0), fix_center)]])
    
    return cnf


def run_plus_encoding_3d(r, k, fix_center=None):
    cnf = generate_plus_encoding_3d(r, k, fix_center)
    file_prefix = f"Z3_r{r}_k{k}"
    cnf.to_file(f"{file_prefix}.cnf")
    
    # Run a SAT solver (e.g., kissat) on the CNF.
    result = subprocess.run(["kissat", f"{file_prefix}.cnf", f"{file_prefix}.drat"],
                              capture_output=True, text=True)
    
    if result.returncode == 20:
        print("UNSAT")
    elif result.returncode == 10:
        # Extract solution if needed.
        sol = [int(val) for line in result.stdout.splitlines() if line.startswith("v")
               for val in line.split() if val.lstrip("-").isnumeric()]
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
