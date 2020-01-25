import io

from . import core_ops, more_ops

from .casts import (
    int_from_bytes, int_to_bytes, bls12_381_from_bytes, bls12_381_to_bytes, bls12_381_generator
)
from .make_eval import make_eval_f, make_eval_cost
from .op_utils import operators_for_module
from .serialize import sexp_to_stream
from .subclass_sexp import subclass_sexp


class mixin:
    @classmethod
    def to_atom(class_, v):
        if isinstance(v, int):
            v = int_to_bytes(v)
        if isinstance(v, bls12_381_generator.__class__):
            v = bls12_381_to_bytes(v)
        return v

    def as_int(self):
        return int_from_bytes(self.as_atom())

    def as_bytes(self):
        return self.as_atom()

    def as_bin(self):
        f = io.BytesIO()
        sexp_to_stream(self, f)
        return f.getvalue()

    def as_bls12_381(self):
        return bls12_381_from_bytes(self.as_atom())


to_sexp_f = subclass_sexp(mixin, (bytes,), false=b'')


KEYWORDS = (
    ". q e a i c f r l x = sha256 + - * . "
    "wrap unwrap point_add pubkey_for_exp uint64 sha256tree >").split()

KEYWORD_FROM_ATOM = {int_to_bytes(k): v for k, v in enumerate(KEYWORDS)}
KEYWORD_TO_ATOM = {v: k for k, v in KEYWORD_FROM_ATOM.items()}

OP_REWRITE = {
    "+": "add",
    "-": "subtract",
    "*": "multiply",
    "/": "divide",
    "i": "if",
    "c": "cons",
    "f": "first",
    "r": "rest",
    "l": "listp",
    "x": "raise",
    "=": "eq",
    ">": "gr",
}


OPERATOR_LOOKUP = operators_for_module(KEYWORD_TO_ATOM, core_ops, OP_REWRITE)
OPERATOR_LOOKUP.update(operators_for_module(KEYWORD_TO_ATOM, more_ops, OP_REWRITE))


eval_f = make_eval_f(
    OPERATOR_LOOKUP, KEYWORD_TO_ATOM["q"], KEYWORD_TO_ATOM["e"], KEYWORD_TO_ATOM["a"])

eval_cost = make_eval_cost(
    OPERATOR_LOOKUP, KEYWORD_TO_ATOM["q"], KEYWORD_TO_ATOM["a"])


def run_program(program, args, max_cost=None, pre_eval_f=None, post_eval_f=None):

    def wrapped_eval(eval_cost, sexp, args, current_cost, max_cost):
        if pre_eval_f:
            new_sexp = pre_eval_f(sexp, args, current_cost, max_cost)
            if new_sexp:
                sexp = new_sexp
        current_cost, r = eval(eval, program, args, max_cost=max_cost)
        if post_eval_f:
            new_r = post_eval_f(sexp, args, current_cost, max_cost, r)
            if new_r:
                r = new_r
        return current_cost, r

    if pre_eval_f or post_eval_f:
        eval = wrapped_eval
    else:
        eval = eval_cost

    return eval(eval, program, args, max_cost=max_cost)
