import os
import subprocess
import itertools
from concurrent.futures import ThreadPoolExecutor
import json

# Path to the CaDiCal binary
CADICAL_BIN = "./cadical/build/cadical"

# Testcases directory
TESTCASES_DIR = "selected_benchmarks"

# Output CSV file
OUTPUT_CSV = "cadical_results.csv"
OUTPUT_JSON = "cadical_results.json"

# Parameter values
reduce_values = [1]
reduceint_values = [200]
reducetarget_values = [60]
emaglueslow_values = [100]

# Get all test files
test_files = [
    os.path.join(TESTCASES_DIR, f)
    for f in os.listdir(TESTCASES_DIR)
    if f.endswith(".cnf.xz")
]

# Generate all parameter combinations
param_combinations = list(
    itertools.product(
        reduce_values, reduceint_values, reducetarget_values, emaglueslow_values
    )
)


def run_cadical(file_and_params):
    """Runs CaDiCal on a given file with specific parameters and extracts results."""
    f, (reduce, reduceint, reducetarget, emaglueslow) = file_and_params
    FLAGS = f"--stats=true -n --reduce={reduce} --reduceint={reduceint} --reducetarget={reducetarget} --emaglueslow={emaglueslow}"

    try:
        result = subprocess.run(
            [CADICAL_BIN] + FLAGS.split() + [f],
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = result.stdout
    except subprocess.TimeoutExpired:
        return [
            f,
            reduce,
            reduceint,
            reducetarget,
            emaglueslow,
            "TIMEOUT",
            None,
            None,
            None,
            None,
            None,
            None,
        ]

    status = "UNKNOWN"
    time_elapsed = conflicts = decisions = propagations = reduced_clauses = (
        peak_memory
    ) = None

    for line in output.splitlines():
        if line.startswith("s "):
            status = line.split()[1]
        elif "c total process time since initialization:" in line:
            time_elapsed = line.split()[6]
        elif "c conflicts:" in line:
            conflicts = line.split()[2]
        elif "c decisions:" in line:
            decisions = line.split()[2]
        elif "c propagations:" in line:
            propagations = line.split()[2]
        elif "c reduced:" in line:
            reduced_clauses = line.split()[2]
        elif "c maximum resident set size of process:" in line:
            peak_memory = line.split()[7]

    return [
        f,
        reduce,
        reduceint,
        reducetarget,
        emaglueslow,
        status,
        time_elapsed,
        conflicts,
        decisions,
        propagations,
        reduced_clauses,
        peak_memory,
    ]


def load_results():
    """Load results from a CSV file."""
    results = {}
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as jsonfile:
            results = json.load(jsonfile)
    return results


def save_results(results):
    """Save results to a CSV file."""
    with open(OUTPUT_JSON, "w") as jsonfile:
        json.dump(results, jsonfile)


def run_cadical_wrapper(file_and_params, DATA):
    """Wrapper function to run CaDiCal and store results in a shared dictionary."""
    # Check if the parameter combination already exists in the results
    for existing_result in DATA[file_and_params[0]]:
        if (
            existing_result[1],
            existing_result[2],
            existing_result[3],
            existing_result[4],
        ) == file_and_params[1]:
            print(
                f"Skipping {file_and_params[0]} with {file_and_params[1]} as it already exists in the results"
            )
            return existing_result
    print(f"Running {file_and_params[0]} with {file_and_params[1]}")
    result = run_cadical(file_and_params)
    print(f"Finished {file_and_params[0]} with {file_and_params[1]}")
    if result[0] not in DATA:
        print(f"Timeout for {file_and_params[0]} with {file_and_params[1]}")
    DATA[file_and_params[0]].append(result)

    return result


if __name__ == "__main__":
    # Create a list of all tasks (file, parameter combination)
    tasks = list(itertools.product(test_files, param_combinations))

    DATA = load_results()
    for f in test_files:
        if f not in DATA:
            DATA[f] = []

    threadCount = os.cpu_count()
    print(f"Running CaDiCal on {len(tasks)} tasks with {threadCount} threads")
    pool = ThreadPoolExecutor(threadCount)

    tasks_pool = []

    try:
        for task in tasks:
            tasks_pool.append(pool.submit(run_cadical_wrapper, task, DATA))

        pool.shutdown(wait=True)
        save_results(DATA)
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating threads...")
        pool.shutdown(wait=False)
        save_results(DATA)
        print("Results saved to", OUTPUT_JSON)
        exit(1)
    except Exception as e:
        print("Caught exception", e)
        pool.shutdown(wait=False)
        save_results(DATA)
        print("Results saved to", OUTPUT_JSON)
        exit(1)
