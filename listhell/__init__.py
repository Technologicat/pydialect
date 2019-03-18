# -*- coding: utf-8 -*-
"""LisThEll: it's not Lisp, it's not Python, it's not Haskell.

Powered by Pydialect and unpythonic."""

from macropy.core.quotes import macros, q, name

from dialects.util import splice_ast

def ast_transformer(module_body):
    with q as template:
        from unpythonic.syntax import macros, prefix, curry
        # auxiliary syntax elements for the macros
        from unpythonic.syntax import q, u, kw
        from unpythonic import apply
        from unpythonic import composerc as compose  # compose from Right, Currying
        with prefix, curry:
            name["__paste_here__"]
    return splice_ast(module_body, template, "__paste_here__")
