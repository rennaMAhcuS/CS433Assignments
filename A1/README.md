# CS433: Automated Reasoning
# Assignment 1: Quantifier Alternation Depth
## Deadline: Friday, 7th February 2025, 11:59 PM

For this assignment you have to use the Python API of `z3` to calculate the
quantifier alternation depth of a given formula. The quantifier alternation
depth of a formula is the maximum number of quantifier type switches on any
path from the root of the parse tree to an atom.

## Task

Write python code that takes a `smt2` file as input via command line arguments
and calculates the quantifier alternation depth of the formula in the file.
Print the quantifier alternation depth to `stdout`. 

The python file should be named `<roll_number_0>_a1.py` or
`<roll_number_0>_<roll_number_1>_a1.py` or
`<roll_number_0>_<roll_number_1>_<roll_number_2>_a1.py` depending on the number
of members in your group. Only 1 group member should submit the file on Moodle.

Expected usage of the code is as follows:

```sh
python 22b0967_a1.py input.smt2
```

## Input Format

The input file will be in `smt2` format. It is guaranteed that the input file
will contain a single first-order-logic formula. 

Sample input files are provided in the `inputs/` directory.

## Output Format

The output to `stdout` should be a single integer, the quantifier alternation
depth of the formula in the given input file. 

Correct outputs to the sample inputs are provided in the `outputs/` directory.
