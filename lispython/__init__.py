# -*- coding: utf-8 -*-
"""Lispython: the love child of Python and Scheme.

Powered by Pydialect and unpythonic."""

__version__ = '1.0.0'

from macropy.core.quotes import macros, q, name

from dialects.util import splice_ast

def ast_transformer(module_body):
    with q as template:
        from unpythonic.syntax import macros, tco, autoreturn, \
                                      multilambda, quicklambda, namedlambda, \
                                      let, letseq, letrec, do, do0, \
                                      dlet, dletseq, dletrec, \
                                      blet, bletseq, bletrec, \
                                      let_syntax, abbrev, \
                                      cond
        # auxiliary syntax elements for the macros
        from unpythonic.syntax import local, delete, where, block, expr, f, _
        from unpythonic import cons, car, cdr, ll, llist, nil, prod, dyn
        with namedlambda:  # MacroPy #21 (nontrivial two-pass macro; seems I didn't get the fix right)
            with autoreturn, quicklambda, multilambda, tco:
                name["__paste_here__"]
    return splice_ast(module_body, template, "__paste_here__")

def rejoice():
    """**Schemers rejoice!**::

    Multiple musings mix in a lambda,
    Lament no longer the lack of let.
    Languish no longer labelless, lambda,
    Linked lists cons and fold.
    Tail-call into recursion divine,
    The final value always provide."""
    return rejoice.__doc__
