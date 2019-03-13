## Pydialect: build languages on Python

Pydialect makes Python into a language platform, à la [Racket](https://racket-lang.org/).
It provides the plumbing that allows to create, in Python, dialects that compile into Python
at import time. Pydialect is geared toward creating languages that extend Python
and look almost like Python, but extend or modify its syntax and/or semantics.
Hence *dialects*.

Pydialect itself is only a lightweight infrastructure hook that makes
it convenient to define and use dialects. To implement the actual semantics
for your dialect (which is where all the interesting things happen), you may
want to look at [MacroPy](https://github.com/azazel75/macropy). Examples can be
found in [unpythonic](https://github.com/Technologicat/unpythonic); see especially
the macros (comprising about one half of the library).

On packaging a set of semantics into a dialect, look at the example dialects
included in the Pydialect distribution:

  - [Lispython: the love child of Python and Scheme](lispython/)
  - [Pytkell: Python with automatic currying and lazy functions](pytkell/)
  - [LisThEll: it's not Lisp, it's not Python, it's not Haskell](listhell/)


### Why dialects?

An extension to the Python language doesn't need to make it into the Python core,
*or even be desirable for inclusion* into the Python core, in order to be useful.

Building on functions and syntactic macros, customization of the language itself
is one more tool for the programmer to extract patterns, at a higher level.
Hence, beside language experimentation, such extensions can be used as a
framework that allows shorter and/or more readable programs.

Pydialect places language-creation power in the hands of its users, without the
need to go to extreme lengths to hack CPython itself or implement from scratch
a custom language that compiles to Python AST or bytecode.

Pydialect dialects compile to Python and are implemented in Python, allowing
the rest of the user program to benefit from new versions of Python, mostly
orthogonally to the development of any dialect.

At its simplest, a custom dialect can alleviate the need to spam a combination
of block macros in every module of a project that uses a macro-based language
extension, such as ``unpythonic.syntax``. Being named as a dialect, a particular
combination of macros becomes instantly recognizable,
and [DRY](https://en.wikipedia.org/wiki/Don't_repeat_yourself):
the dialect definition becomes the only place in the codebase that defines
the macro combination to be used by each module in the project.

The same argument applies to custom builtins: any functions or macros that
feel like they "should be" part of the language layer, so that they won't
have to be explicitly imported in each module where they are used.


### Using dialects

Place a **lang-import** at the start of your module that uses a dialect:

    from __lang__ import piethon

Run your program (in this example written in the ``piethon`` dialect)
through the ``pydialect`` bootstrapper instead of ``python3`` directly,
so that the main program gets imported instead of run directly, to trigger
the import hook that performs the dialect processing. (Installing Pydialect
will install the bootstrapper.)

Any imported module that has a *lang-import* will be detected, and the appropriate
dialect module (if and when found) will be invoked. The result is then sent to
the macro expander (if MacroPy is installed and the code uses macros at that
point), after which the final result is imported normally.

The lang-import must appear as the first statement of the module; only the
module docstring is allowed to appear before it. This is to make it explicit
that **a dialect applies to the whole module**. (Local changes to semantics
are better represented as a block macro.)

At import time, the dialect importer replaces the lang-import with an
assignment that sets the module's ``__lang__`` attribute to the dialect name,
for introspection. If a module does not have a ``__lang__`` attribute at
run time, then it was not compiled by Pydialect. Note that just like with
MacroPy, at run time the code is pure Python.

The lang-import is a construct specific to Pydialect. This ensures that the
module will immediately fail if run under standard Python, because there is
no actual module named ``__lang__``.

If you use MacroPy, the Pydialect import hook must be installed at index ``0``
in ``sys.meta_path``, so that the dialect importer triggers before MacroPy's
standard macro expander. The ``pydialect`` bootstrapper takes care of this.
If you need to enable Pydialect manually for some reason, the incantation
to install the hook is ``import dialects.activate``.

The lang-import syntax was chosen as a close pythonic equivalent to Racket's
``#lang foo``.


### Defining a dialect

In Pydialect, a dialect is any module that provides one or both of the following
callables:

   - ``source_transformer``: source text -> source text

        The **full source code** of the module being imported (*including*
        the lang-import) is sent to the the source transformer. The data type
        is whatever the loader's ``get_source`` returns, usually ``str``.

        Source transformers are useful e.g. for defining custom infix
        operators. For example, the monadic bind syntax ``a >>= b``
        could be made to transform into the syntax ``a.__mbind__(b)``.

        Although the input is text, in practice a token-based approach is
        recommended; see stdlib's ``tokenize`` module as a base to work from.
        (Be sure to untokenize when done, because the next stage expects text.)

        **After the source transformer**, the source text must be valid
        surface syntax for **standard Python**, i.e. valid input for
        ``ast.parse``.

   - ``ast_transformer``: ``list`` of AST nodes -> ``list`` of AST nodes

        After the source transformer, but before macro expansion, the full AST
        of the module being imported (*minus* the module docstring and the
        lang-import) is sent to this whole-module AST transformer.

        This allows injecting implicit imports to create builtins for the
        dialect, as well as e.g. lifting the whole module (except the docstring
        and the code to set ``__lang__``) into a ``with`` block to apply
        some MacroPy block macro(s) to the whole module.

        **After the AST transformer**, the module is sent to MacroPy for
        macro expansion (if MacroPy is installed, and the module has macros
        at that point), and after that, the result is finally imported normally.

The AST transformer can use MacroPy if it wants, but doesn't have to; this
decision is left up to each developer implementing a dialect.

If you make an AST transformer, and have MacroPy, then see ``dialects.util``,
which can help with the boilerplate task of pasting in the code from the
user module (while handling macro-imports correctly in both the dialect
template and in the user module).

**The name** of a dialect is simply the name of the module or package that
implements the dialect. In other words, it's the name that needs to be imported
to find the transformer functions.

Note that a dotted name in place of the ``xxx`` in ``from __lang__ import xxx``
is not valid Python syntax, so (currently) **a dialect should be defined in a
top-level module** (no dots in the name). Strictly, the dialect finder doesn't
need to care about this (though it currently does), but IDEs and tools in
general are much happier with code that does not contain syntax errors.
(This allows using standard Python tools with dialects that do not introduce
any new surface syntax.)

A dialect can be implemented using another dialect, as long as there are no
dependency loops. *Whenever* a lang-import is detected, the dialect importer
is invoked (especially, also during the import of a module that defines a
new dialect). This allows creating a tower of languages.


### Combining existing dialects

*Dangerous things should be difficult to do _by accident_.* --[John Shutt](http://fexpr.blogspot.com/2011/05/dangerous-things-should-be-difficult-to.html)

Due to the potentially unlimited complexity of interactions between language
features defined by different dialects, there is *by design* no automation for
combining dialects. In the general case, this is something that requires human
intervention.

If you know (or at least suspect) that two or more dialects are compatible,
you can define a new dialect whose ``source_transformer`` and ``ast_transformer``
simply chain those of the existing dialects (in the desired order; consider how
the macros expand), and then use that dialect.


### When to make a dialect

Often explicit is better than implicit. There is however a tipping point with
regard to complexity, and/or simply length, after which implicit becomes
better.

This already applies to functions and macros; code in a ``with continuations``
block (see macros in [unpythonic](https://github.com/Technologicat/unpythonic))
is much more readable and maintainable than code manually converted to
continuation-passing style (CPS). There's obviously a tradeoff; as PG reminds
in [On Lisp](http://paulgraham.com/onlisp.html), each abstraction is another
entity for the reader to learn and remember, so it must save several times
its own length to become an overall win.

So, when to make a dialect depends on how much it will save (in a project or
across several), and on the other hand on how important it is to have a shared
central definition that specifies a "language-level" common ground for a set of
user modules.


### Dialect implementation considerations

A dialect can do anything from simply adding some surface syntax (such as a
monadic bind operator), to completely changing Python's semantics, e.g. by adding
automatic tail-call optimization, continuations, and/or lazy functions. The only
limitation is that the desired functionality must be (macro-)expressible in Python.

The core of a dialect is defined as a set of functions and macros, which typically
live inside a library. The role of the dialect module is to package that core
functionality into a whole that can be concisely loaded with a single lang-import.

Typically a dialect implicitly imports its core functions and macros, to make
them appear as builtins (in the sense of *defined by default*) to modules that
use the dialect.

A dialect may also define non-core functions and macros that live in the same
library; those essentially comprise *the standard library* of the dialect.

For example, the ``lispython`` dialect itself is defined by a subset of
``unpythonic`` and ``unpythonic.syntax``; the rest of the library is available
to be imported manually; it makes up the standard library of ``lispython``.

For macros, Pydialect supports MacroPy. Technically, macros are optional,
so Pydialect's dependency on MacroPy is strictly speaking optional.
Pydialect already defines a hook for a full-module AST transform;
if that (and/or a source transform) is all you need, there's no need
to have your dialect depend on MacroPy.

However, where MacroPy shines is its infrastructure. It provides a uniform
syntax to direct AST transformations to apply to particular expressions or
blocks in the user code, and it provides a hygienic quasiquote system, which
is absolutely essential for avoiding inadvertent name conflicts (identifier
capture, free variable injection). It's also good at fixing missing source
location info for macro-generated AST nodes, which is extremely useful, since
in Python the source location info is compulsory for every AST node.

Since you're reading this, you probably already know, but be aware that, unlike
how it was envisioned during the *extensible languages* movement in the 1960s-70s,
language extension is hardly an exercise requiring only *modest amounts of labor
by unsophisticated users* [[1]](http://fexpr.blogspot.com/2013/12/abstractive-power.html).
Especially the interaction between different macros needs a lot of thought,
and as the number of language features grows, the complexity skyrockets.
(For an example, look at what hoops other parts of ``unpythonic`` must jump
through to make ``lazify`` happy.) Seams between parts of the user program
that use or do not use some particular feature (or a combination of features)
also require special attention.

Python is a notoriously irregular language, not to mention a far cry from
homoiconic, so it is likely harder to extend than a Lisp. Be prepared for some
head-scratching, especially when dealing with function call arguments,
assignments and the two different kinds of function definitions (``def`` and
``lambda``, one of which supports the full Python language while the other is
limited to the expression sublanguage).
[Green Tree Snakes - the missing Python AST docs](https://greentreesnakes.readthedocs.io/en/latest/index.html)
is a highly useful resource here.

Be sure to understand the role of ``ast.Expr`` (the *expression statement*) and
its implications when working with MacroPy. (E.g. ``ast_literal[tree]`` by itself
in a block-quasiquote is an ``Expr``, where the value is the ``Subscript``
``ast_literal[tree]``. This may not be what you want, if you're aiming to
splice in a block of statements, but it's unavoidable given Python's AST
representation.

Dialects implemented via macros will mainly require maintenance when Python's
AST representation changes (if incompatible changes or interesting new features
hit a relevant part). Large parts of the AST representation have remained
stable over several of the latest minor releases, or even all of Python 3.
Perhaps most notably, the handling of function call arguments changed in an
incompatible way in 3.5, along with introducing MatMult and the async
machinery. The other changes between 3.4 (2014) and 3.7 (2018) are just
a couple of new node types.

Long live [language-oriented programming](https://en.wikipedia.org/wiki/Language-oriented_programming),
and have fun!


### Notes

``dialects/importer.py`` is based on ``core/import_hooks.py`` in MacroPy 1.1.0b2,
and was then heavily customized.

In the Lisp community, surface syntax transformations are known as *reader macros*
(although technically it's something done at the parsing step, unrelated to
syntactic macros).

**Further reading**:

   - [Hacking Python without hacking Python](http://stupidpythonideas.blogspot.com/2015/06/hacking-python-without-hacking-python.html)
   - [Operator sectioning for Python](http://stupidpythonideas.blogspot.com/2015/05/operator-sectioning-for-python.html)
   - [How to use loader and finder objects in Python](http://www.robots.ox.ac.uk/~bradley/blog/2017/12/loader-finder-python.html)

**Ground-up extension efforts** that replace Python's syntax:

   - [Dogelang](https://pyos.github.io/dg/), Python with Haskell-like syntax,
     compiles to Python bytecode.
   - [Hy](http://docs.hylang.org/en/stable/), a Lisp-2 that compiles to Python AST.
