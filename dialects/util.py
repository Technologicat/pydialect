# -*- coding: utf-8 -*-

__all__ = ["splice_ast"]

from ast import Expr, Name, If, Num, ImportFrom, Pass, copy_location

try:
    from macropy.core.walkers import Walker
except ImportError:
    Walker = None

def splice_ast(body, template, tag):
    """In an AST transformer, splice module body into template.

    Imports for MacroPy macros are handled specially, gathering them all at the
    front, so that MacroPy sees them. Any macro imports in the template are
    placed first (in the order they appear in the template), followed by any
    macro imports in the user code (in the order they appear in the user code).

    This function is provided as a convenience for modules that define dialects.
    We use MacroPy to perform the splicing, so this function is only available
    when MacroPy is installed (``ImportError`` is raised if not). Installation
    status is checked only once per session, when ``dialects.util`` is first
    imported.

    Parameters:

        ``body``: ``list`` of statements
            Module body of the original user code (input).

        ``template``: ``list`` of statements
            Template for the module body of the new module (output).

            Must contain a marker that indicates where ``body`` is to be
            spliced in. The marker is an ``ast.Name`` node whose ``id``
            attribute matches the value of the ``tag`` string.

        ``tag``: ``str``
            The value of the ``id`` attribute of the marker in ``template``.

    Returns the new module body, i.e. ``template`` with ``body`` spliced in.

    Example::

        marker = q[name["__paste_here__"]]      # MacroPy, or...
        marker = ast.Name(id="__paste_here__")  # ...manually

        ...  # create template, place the marker in it

        dialects.splice_ast(body, template, "__paste_here__")

    """
    if not Walker:  # optional dependency for Pydialect, but mandatory for this util
        raise ImportError("macropy.core.walkers.Walker not found; MacroPy likely not installed")
    if not body:  # ImportError because this occurs during the loading of a module written in a dialect.
        raise ImportError("expected at least one statement or expression in module body")

    def is_paste_here(tree):
        return type(tree) is Expr and type(tree.value) is Name and tree.value.id == tag
    def is_macro_import(tree):
        return type(tree) is ImportFrom and tree.names[0].name == "macros"

    # XXX: MacroPy's debug logger will sometimes crash if a node is missing a source location.
    # In general, dialect templates are fully macro-generated with no source location info to start with.
    # Pretend it's all at the start of the user module.
    locref = body[0]
    @Walker
    def fix_template_srcloc(tree, **kw):
        if not all(hasattr(tree, x) for x in ("lineno", "col_offset")):
            tree = copy_location(tree, locref)
        return tree

    @Walker
    def extract_macro_imports(tree, *, collect, **kw):
        if is_macro_import(tree):
            collect(tree)
            tree = copy_location(Pass(), tree)  # must output a node so replace by a pass stmt
        return tree

    template = fix_template_srcloc.recurse(template)
    template, template_macro_imports = extract_macro_imports.recurse_collect(template)
    body, user_macro_imports = extract_macro_imports.recurse_collect(body)

    @Walker
    def splice_body_into_template(tree, *, stop, **kw):
        if not is_paste_here(tree):
            return tree
        stop()  # prevent infinite recursion in case the user code contains a Name that looks like the marker
        return If(test=Num(n=1),
                  body=body,
                  orelse=[],
                  lineno=tree.lineno, col_offset=tree.col_offset)
    finalbody = splice_body_into_template.recurse(template)
    return template_macro_imports + user_macro_imports + finalbody
