from clvm.make_eval import EvalError

from .Node import Node
from .reader import read_tokens


BUILT_IN_KEYWORDS = [
    ("if",
        "(list eval (list if_op (first (args)) "
        "(list function (first (rest (args)))) (list function (first (rest (rest (args)))))) (list args))"),
    ("compile",
        "(list compile_op (list quote x0))"),
    ("expand",
        "(list expand_op (list quote x0))"),
    ("prog",
        "(list prog_op (list quote x0))"),
    ("function",
        "(list function_op (list quote x0))"),
    ("map",
        "(list eval (quote (quote (eval x0 (list x0 x1)))) "
        "(list list (list function (list if (quote x1) "
        "(list cons (list eval x0 (list list (list first (quote x1)))) "
        "(list eval (quote x0) (list list (quote x0) (list rest (quote x1))))) ())) x1))"),
]


MACRO_KEYWORDS = {k: read_tokens(v) for k, v in BUILT_IN_KEYWORDS}


def expand_list(sexp, op_expand_sexp):
    """
    Take an sexp that is a list and turn it into a bunch of cons
    operators that build the list.
    """
    if sexp.nullp():
        return sexp.null()
    return sexp.to(["cons", sexp.first(), op_expand_sexp(sexp.to("list").cons(sexp.rest()))])


def make_unexpanded_operator(operator):
    def stop_expanding(sexp, op_expand_sexp):
        return sexp.to(operator).cons(sexp)
    return stop_expanding


UNEXPANDED_OPS = ["quote"]
OPERATOR_LOOKUP = {
    "list": expand_list,
}
OPERATOR_LOOKUP.update({_: make_unexpanded_operator(_) for _ in UNEXPANDED_OPS})


def op_expand_sexp(sexp, operator_lookup=OPERATOR_LOOKUP):
    """
    Expand macros and variables, and quote atoms.
    """
    if sexp.nullp():
        return sexp.to(["quote", sexp])

    if not sexp.listp():
        # expand atoms
        as_atom = sexp.as_atom()
        c = as_atom[0]
        # quoted string
        if c in "\'\"":
            if c == as_atom[-1] and len(as_atom) >= 2:
                return sexp.to(["quote", as_atom])
            raise EvalError("bad string", sexp)

        # variable: x0, x1, ...
        if as_atom.upper().startswith("X"):
            try:
                index = int(as_atom[1:])
                return sexp.to(Node.for_list_index(index))
            except Exception:
                raise EvalError("bad variable", sexp)

        # node by index: n0, n1, ...
        if as_atom.upper().startswith("N"):
            try:
                index = int(as_atom[1:])
                return sexp.to(Node(index))
            except Exception:
                raise EvalError("bad variable", sexp)

        return sexp.to(["quote", sexp])

    operator = sexp.first()
    if not operator.listp():
        as_atom = operator.as_atom()
        if as_atom in MACRO_KEYWORDS:
            operator = MACRO_KEYWORDS[as_atom]

    if operator.listp():
        # this is a macro. Apply it
        macro_sexp = sexp.to(["eval", ["quote", operator], sexp.to(["quote", sexp.rest()])])
        if 0:
            return sexp.to(["eval", macro_sexp, ["args"]])
        else:
            from .cmds import do_eval
            return do_eval(macro_sexp, sexp.null())
    else:
        f = operator_lookup.get(operator.as_atom())
        if f:
            return f(sexp.rest(), op_expand_sexp)
        # expand arguments
        sexp = sexp.to([operator] + [op_expand_sexp(_, operator_lookup) for _ in sexp.rest().as_iter()])

    return sexp


def op_expand_op(sexp):
    if not sexp.nullp() and sexp.rest().nullp():
        return op_expand_sexp(sexp.first())

    raise EvalError("expand_op requires exactly 1 parameter", sexp)


"""
Copyright 2019 Chia Network Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""