import subprocess
from joblib import Parallel, delayed
import matplotlib.pyplot as plt


def run_command(command: str = "", shell_output: bool = False) -> str:
    output = ""
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in proc.stdout:
        if shell_output:
            print(line, end="")
        output += line
    proc.wait()
    output = output.strip()
    return output


"""
--restart=bool             enable restarts [true]
--restartint=1..2e9        restart interval [2]
--restartmargin=0..1e2     slow fast margin in percent [10]
--restartreusetrail=bool   enable trail reuse [true]
--reluctant=0..2e9         reluctant doubling period [1024]
--reluctantmax=0..2e9      reluctant doubling period [1048576]
"""


def cadical_run(
    filehash: str,
    restart: bool = True,
    restartint: int = 2,
    restartmargin: int = 10,
    restartreusetrail: bool = True,
    reluctant: int = 1024,
    reluctantmax: int = 1048576,
    shell_output: bool = False,
):
    file = f"{filehash}*.cnf.xz"
    benchmarks_directory = "./benchmarks"

    options = f"--restart={str(restart).lower()} \
    --restartint={restartint} \
    --restartmargin={restartmargin} \
    --restartreusetrail={str(restartreusetrail).lower()} \
    --reluctant={reluctant} \
    --reluctantmax={reluctantmax}"

    # Expecting cadical is in the path and you are running this in A2 directory
    command = f"cadical {benchmarks_directory}/{file} {options}"
    command_output = run_command(command=command, shell_output=shell_output).split(
        "\n"
    )[-7:-4]
    return tuple(float(command_output[i].split()[-2]) for i in [0, 2])


def get_data(
    filehash: str, param: str, param_range: range, memory: bool = False
) -> list:
    def forloop(i: int) -> tuple:
        out = cadical_run(filehash=filehash, **({param: i}))[int(memory)]
        print(f"{i = }, {out = }")
        print("----------")
        return i, out

    filehash_out: list = list(
        Parallel(n_jobs=-1)(delayed(forloop)(i) for i in param_range)
    )

    return filehash_out


def plot_data(
    filehash: str, param: str, param_range: range, memory: bool = False
) -> None:
    filehash_out1: list = get_data("31c4aac", param, param_range, memory=memory)

    # Extract x and y coordinates from filehash_out1
    x_vals = [point[0] for point in filehash_out1]
    y_vals = [point[1] for point in filehash_out1]

    plt.step(x_vals, y_vals, where="post", marker="o")
    plt.xlabel(param)
    plt.ylabel("CPU Time Taken")
    plt.title(f"{param} vs {'memory' if memory else 'time'}")
    plt.grid(True)
    plt.savefig(f"images/{param}-{int(memory)}.png")
    plt.show()


def main() -> None:
    parameters = {
        "restartint",
        "restartmargin",
        "reluctant",
        "reluctantmax",
    }

    for param in parameters:
        param_range = range(1)
        if param == "restartmargin":
            param_range = range(0, 100, 1)
        else:
            param_range = range(0, int(1e4), 100)

        print(f"{param}: MEMORY")
        plot_data("31c4aac", param, param_range, memory=True)
        print(f"{param}: TIME")
        plot_data("31c4aac", param, param_range, memory=False)


if __name__ == "__main__":
    main()
