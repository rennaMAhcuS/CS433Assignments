import sys

from z3 import *

# Parsing the argument file
filename = sys.argv[1]
f = parse_smt2_file(sys.argv[1])
f = f[0]


def qad_rec(f, curr, is_not):
    """
        Recursively calculates QAD, converts =>, xor, iff to or, and, not forms.
        f - formula given
        curr - current quantifier type
        is_not - whether the formula is negated
    """

    if is_app_of(f, Z3_OP_NOT):
        return qad_rec(f.arg(0), curr, not is_not)
    if is_app_of(f, Z3_OP_AND) or is_app_of(f, Z3_OP_OR):
        return max(qad_rec(f.arg(0), curr, is_not),
                   qad_rec(f.arg(1), curr, is_not))
    if is_app_of(f, Z3_OP_IMPLIES):
        return max(qad_rec(f.arg(0), curr, not is_not),
                   qad_rec(f.arg(1), curr, is_not))
    if is_app_of(f, Z3_OP_IFF) or is_app_of(f, Z3_OP_XOR):
        return max(qad_rec(f.arg(0), curr, not is_not),
                   qad_rec(f.arg(1), curr, is_not),
                   qad_rec(f.arg(0), curr, is_not),
                   qad_rec(f.arg(1), curr, not is_not))

    if is_var(f) or is_app(f):
        return 0

    # exists == 0, forall == 1
    if f.is_forall():
        body = f.children()[0]
        return (curr == is_not) + qad_rec(body, not is_not, is_not)
    if f.is_exists():
        body = f.children()[0]
        return (curr != is_not and curr != -1) + qad_rec(body, is_not, is_not)

    return 0


# Wrapper function for `qad_rec` with base cases
def qad(f):
    return qad_rec(f, -1, False)


print(qad(f))
