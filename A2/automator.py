import subprocess
from joblib import Parallel, delayed


def run_command(command: str = '', shell_output: bool = False) -> str:
    output = ""
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        if shell_output:
            print(line, end='')
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
        shell_output: bool = False
    ):

    file = f"{filehash}*.cnf.xz"
    benchmarks_directory = './benchmarks'

    options = f'--restart={str(restart).lower()} \
    --restartint={restartint} \
    --restartmargin={restartmargin} \
    --restartreusetrail={str(restartreusetrail).lower()} \
    --reluctant={reluctant} \
    --reluctantmax={reluctantmax}'

    # Expecting cadical is in the path and you are running this in A2 directory
    command = f'cadical {benchmarks_directory}/{file} {options}'
    command_output = run_command(command=command, shell_output=shell_output).split('\n')[-7:-4]
    return tuple(float(command_output[i].split()[-2]) for i in [0, 2])
        

def forloop(i: int) -> None:
    out = cadical_run(filehash='000a41cdca43be89ed62ea3abf2d0b64', restartmargin=i)[0]
    print(out)
    print('----------')
    return i, out

filehash_out1 = Parallel(n_jobs=-1)(delayed(forloop)(i) for i in range(101))

print('\a')

import matplotlib.pyplot as plt

# Extract x and y coordinates from filehash_out1
x_vals = [point[0] for point in filehash_out1]
y_vals = [point[1] for point in filehash_out1]

plt.plot(x_vals, y_vals, marker='o')
plt.xlabel("X axis")
plt.ylabel("Y axis")
plt.title("Filehash Output Plot")
plt.grid(True)
plt.show()
