# -*- coding: utf-8 -*-
"""Lispython: the love child of Python and Scheme.

Powered by Pydialect and unpythonic."""

from macropy.core.quotes import macros, q, name

# The dialect finder imports us, so do not from-import to avoid dependency loop.
import dialects.util

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
        from unpythonic.syntax import local, where, block, expr, f, _
        from unpythonic import cons, car, cdr, ll, llist, nil, prod, dyn
        with namedlambda:  # MacroPy #21 (nontrivial two-pass macro; seems I didn't get the fix right)
            with autoreturn, quicklambda, multilambda, tco:
                name["__paste_here__"]
    return dialects.util.splice_ast(module_body, template, "__paste_here__")

def rejoice():
    """**Schemers rejoice!**::

    Multiple musings mix in a lambda,
    Lament no longer the lack of let.
    Languish no longer labelless, lambda,
    Linked lists cons and fold.
    Tail-call into recursion divine,
    The final value always provide."""
    return rejoice.__doc__
