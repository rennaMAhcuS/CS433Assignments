import sys

from z3 import *

filename = sys.argv[1]
f = parse_smt2_file(sys.argv[1])
f = f[0]

u = DeclareSort("U")
x = Const("x", u)
q = Function("q", u, BoolSort())

connectives = ["and", "or", "not", "=>", "xor", "iff"]
quantifiers = ["forall", "exists"]


def qd(f):
    if is_var(f) or is_app(f):
        return 0
    if f.is_forall() or f.is_exists():
        return qd(f.children()[0]) + 1
    if f.decl().name() in connectives:
        return max(qd(f.arg(0)), qd(f.arg(1)))
    return 0


# helper function for qad
def qad_rec(f, curr):

    # if f is a connective, return the maximum of the quantifier depth of its children
    if (is_app_of(f, Z3_OP_AND) or is_app_of(f, Z3_OP_OR)
            or is_app_of(f, Z3_OP_IFF) or is_app_of(f, Z3_OP_XOR)
            or is_app_of(f, Z3_OP_IMPLIES)):
        return max(qad_rec(f.arg(0), curr), qad_rec(f.arg(1), curr))
    if is_app_of(f, Z3_OP_NOT):
        return qad_rec(f.arg(0), curr)

    # constants are function applications with 0 arguments
    # if f is a variable or a function application, return 0
    # these would be atoms
    if is_var(f) or is_app(f):
        return 0

    # exists == 0, forall == 1
    if f.is_forall():
        if curr == -1:
            return qad_rec(f.children()[0], 1)
        if curr == 0:
            return 1 + qad_rec(f.children()[0], 1 - curr)
        return qad_rec(f.children()[0], curr)
    if f.is_exists():
        if curr == -1:
            return qad_rec(f.children()[0], 0)
        if curr == 1:
            return 1 + qad_rec(f.children()[0], 1 - curr)
        return qad_rec(f.children()[0], curr)
    return 0


# This function assumes that f is in prenex normal form
def qad(f):
    return qad_rec(f, -1)


# help_simplify()
print(qad(f))
