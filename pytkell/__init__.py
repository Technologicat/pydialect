# -*- coding: utf-8 -*-
"""Pytkell: Python with automatic currying and lazy functions.

Powered by Pydialect and unpythonic."""

__version__ = '1.0.0'

from macropy.core.quotes import macros, q, name

from dialects.util import splice_ast

def ast_transformer(module_body):
    with q as template:
        from macropy.quick_lambda import macros, lazy
        from unpythonic.syntax import macros, lazify, lazyrec, curry, \
                                      let, letseq, letrec, do, do0, \
                                      dlet, dletseq, dletrec, \
                                      blet, bletseq, bletrec, \
                                      cond, forall
        # auxiliary syntax elements for the macros
        from unpythonic.syntax import local, delete, where, insist, deny
        # functions that have a haskelly feel to them
        from unpythonic import foldl, foldr, scanl, scanr, \
                               s, m, mg, frozendict, \
                               memoize, fupdate, fup, \
                               gmemoize, imemoize, fimemoize, \
                               islice, take, drop, split_at, first, second, nth, last, \
                               flip, rotate
        from unpythonic import composerc as compose  # compose from Right, Currying (Haskell's . operator)
        # this is a bit lispy, but we're not going out of our way to provide
        # a haskelly surface syntax for these.
        from unpythonic import cons, car, cdr, ll, llist, nil
        with curry, lazify:
            name["__paste_here__"]
    return splice_ast(module_body, template, "__paste_here__")
