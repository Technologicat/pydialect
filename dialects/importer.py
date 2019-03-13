# -*- coding: utf-8 -*-
"""Importer for Python dialects."""

__all__ = ["DialectFinder"]

import ast
import importlib
from importlib.util import spec_from_loader
import logging
import sys
import re

try:
    import macropy.core
except ImportError:
    macropy = None

logger = logging.getLogger(__name__)

# This is essentially a copy of ``macropy.core.import_hooks.MacroLoader``, copied to
# make sure that the implementation won't go out of sync with our ``DialectFinder``.
# The export machinery has been removed as unnecessary for language experimentation;
# but is trivial to add back if needed (see the sources of MacroPy 1.1.0b2).
class DialectLoader:
    def __init__(self, nomacro_spec, code, tree):
        self.nomacro_spec = nomacro_spec
        self.code = code
        self.tree = tree

    def create_module(self, spec):
        pass

    def exec_module(self, module):
        exec(self.code, module.__dict__)

    def get_filename(self, fullname):
        return self.nomacro_spec.loader.get_filename(fullname)

    def is_package(self, fullname):
        return self.nomacro_spec.loader.is_package(fullname)

# barebones unpythonic.misc.call but let's not depend on a library we don't otherwise need
def singleton(cls):
    return cls()

# Like MacroPy's MacroFinder:
#
# - This is a meta_path finder, because we're looking for nonstandard things
#   inside standard-ish Python modules that can be found/loaded using the
#   standard mechanisms.
#
# - Macro expansion is performed already at the finder step, because in order to
#   detect whether to use the macro loader, the input must be scanned for macros.
#   We could dispatch to a custom loader immediately after detecting that the
#   module uses a dialect, but have chosen to just inherit this design.

@singleton
class DialectFinder:
    """Importer that matches any module that has a 'from __lang__ import xxx'."""

    def _find_spec_nomacro(self, fullname, path, target=None):
        """Try to find the original, non macro-expanded module using all the
        remaining meta_path finders (except MacroPy's, to avoid handling
        macros twice).
        """
        spec = None
        for finder in sys.meta_path:
            # when testing with pytest, it installs a finder that for
            # some yet unknown reasons makes macros expansion
            # fail. For now it will just avoid using it and pass to
            # the next one
            if finder is self or (macropy and finder is macropy.core.import_hooks.MacroFinder) or \
               'pytest' in finder.__module__:
                continue
            if hasattr(finder, 'find_spec'):
                spec = finder.find_spec(fullname, path, target=target)
            elif hasattr(finder, 'load_module'):
                spec = spec_from_loader(fullname, finder)
            if spec is not None:
                break
        return spec

    def expand_macros(self, source_code, filename, fullname, spec, lang_module):
        """Parse, apply AST transforms, and compile.

        Parses the source_code, applies the ast_transformer of the dialect,
        and macro-expands the resulting AST if it has macros. Then compiles
        the final AST.

        Returns both the compiled new AST, and the raw new AST.
        """
        logger.info('Parse in file {} (module {})'.format(filename, fullname))
        tree = ast.parse(source_code)

        if not (isinstance(tree, ast.Module) and tree.body):
            msg = "Expected a Module node with at least one statement or expression in file {} (module {})".format(filename, fullname)
            logger.error(msg)
            raise SyntaxError(msg)

        # The 'from __lang__ import xxx' has done its job, replace it with
        # '__lang__ = "xxx"' for run-time introspection.
        def isimportdialect(tree):
            return type(tree) is ast.ImportFrom and tree.module == "__lang__"
        # q[] would be much easier but we want to keep MacroPy optional.
        # We need to be careful to insert a location to each AST node
        # in case we're not invoking MacroPy (which fixes missing locations).
        def make_langname_setter(tree):
            s = ast.Str(s=tree.names[0].name)
            s = ast.copy_location(s, tree)
            n = ast.Name(id="__lang__", ctx=ast.Store())
            n = ast.copy_location(n, tree)
            a = ast.Assign(targets=[n], value=s)
            a = ast.copy_location(a, tree)
            return a

        if isimportdialect(tree.body[0]):
            preamble = [make_langname_setter(tree.body[0])]
            thebody = tree.body[1:]
        # variant with module docstring
        elif len(tree.body) > 1 and isinstance(tree.body[0], ast.Expr) and \
             isimportdialect(tree.body[1]):
            preamble = [tree.body[0], make_langname_setter(tree.body[1])]
            thebody = tree.body[2:]
        else:  # we know the lang-import is there; it's in some other position
            msg = "Misplaced lang-import in file {} (module {})".format(filename, fullname)
            logger.error(msg)
            raise SyntaxError(msg)

        if hasattr(lang_module, "ast_transformer"):
            logger.info('Dialect AST transform in file {} (module {})'.format(filename, fullname))
            thebody = lang_module.ast_transformer(thebody)
        tree.body = preamble + thebody

        # detect macros **after** any dialect-level whole-module transform
        new_tree = tree
        if macropy:
            logger.info('Detect macros in file {} (module {})'.format(filename, fullname))
            bindings = macropy.core.macros.detect_macros(tree, spec.name,
                                                         spec.parent,
                                                         spec.name)
            if bindings:  # expand macros
                logger.info('Expand macros in file {} (module {})'.format(filename, fullname))
                modules = []
                for mod, bind in bindings:
                    modules.append((importlib.import_module(mod), bind))
                new_tree = macropy.core.macros.ModuleExpansionContext(
                    tree, source_code, modules).expand_macros()

        try:
            # MacroPy uses the old tree here as input to compile(), but it doesn't matter,
            # since ``ModuleExpansionContext.expand_macros`` mutates the tree in-place.
            logger.info('Compile file {} (module {})'.format(filename, fullname))
            return compile(new_tree, filename, "exec"), new_tree
        except Exception:
            logger.error("Error while compiling file {} (module {})".format(filename, fullname))
            raise

    def find_spec(self, fullname, path, target=None):
        spec = self._find_spec_nomacro(fullname, path, target)
        if spec is None or not (hasattr(spec.loader, 'get_source') and
                                callable(spec.loader.get_source)):  # noqa: E128
            if fullname != 'org':
                # stdlib pickle.py at line 94 contains a ``from
                # org.python.core for Jython which is always failing,
                # of course
                logger.debug('Failed finding spec for {}'.format(fullname))
            return
        origin = spec.origin
        if origin == 'builtin':
            return
        try:
            source = spec.loader.get_source(fullname)
        except ImportError:
            logger.debug('Loader for {} was unable to find the sources'.format(fullname))
            return
        except Exception:
            logger.error('Loader for {} raised an error'.format(fullname))
            return
        if not source:  # some loaders may return None for the sources, without raising an exception
            logger.debug('Loader returned empty sources for {}'.format(fullname))
            return

        lang_import = "from __lang__ import"
        if lang_import not in source:
            return  # this module does not use a dialect

        # Detect the dialect... ugh!
        #   - At this point, the input is text.
        #   - It's not parseable by ast.parse, because a dialect may introduce
        #     new surface syntax.
        #   - Similarly, it's not tokenizable by stdlib's tokenizer, because
        #     a dialect may customize what constitutes a token.
        #   - So we can only rely on the literal text "from __lang__ import xxx".
        #   - This is rather similar to how Racket heavily constrains what may
        #     appear on the #lang line.
        matches = re.findall(r"from __lang__ import\s+([0-9a-zA-Z_]+)\s*$", source, re.MULTILINE)
        if len(matches) != 1:
            msg = "Expected exactly one lang-import with one dialect name"
            logger.error(msg)
            raise SyntaxError(msg)
        dialect_name = matches[0]

        try:
            logger.info("Detected dialect '{}' in module '{}', loading dialect".format(dialect_name, fullname))
            lang_module = importlib.import_module(dialect_name)
        except ImportError as err:
            msg = "Could not import dialect module '{}'".format(dialect_name)
            logger.error(msg)
            raise ImportError(msg) from err
        if not any(hasattr(lang_module, x) for x in ("source_transformer", "ast_transformer")):
            msg = "Module '{}' has no dialect transformers".format(dialect_name)
            logger.error(msg)
            raise ImportError(msg)

        if hasattr(lang_module, "source_transformer"):
            logger.info('Dialect source transform in {}'.format(fullname))
            source = lang_module.source_transformer(source)
            if not source:
                msg = "Empty source text after dialect source transform in {}".format(fullname)
                logger.error(msg)
                raise SyntaxError(msg)
            if lang_import not in source:  # preserve invariant
                msg = 'Dialect source transform for {} should not delete the lang-import'.format(fullname)
                logger.error(msg)
                raise RuntimeError(msg)

        code, tree = self.expand_macros(source, origin, fullname, spec, lang_module)

        # Unlike macropy.core.import_hooks.MacroLoader, which exits at this point if there
        # were no macros, we always process the module (because it was explicitly tagged
        # as a dialect, and pure source-transform dialects are also allowed).

        loader = DialectLoader(spec, code, tree)
        return spec_from_loader(fullname, loader)
