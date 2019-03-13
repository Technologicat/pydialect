## Pytkell: Python with automatic currying and lazy functions

Powered by [Pydialect](https://github.com/Technologicat/pydialect) and
[unpythonic](https://github.com/Technologicat/unpythonic).

### Features

In terms of ``unpythonic.syntax``, we implicitly enable ``curry`` and ``lazify``
for the whole module.

We also import some macros and functions to serve as dialect builtins:

  - All ``let[]`` and ``do[]`` constructs from ``unpythonic.syntax``
  - ``lazy[]`` and ``lazyrec[]`` for manual lazification of atoms and
    data structure literals, respectively
  - If-elseif-else expression ``cond[]``
  - Nondeterministic evaluation ``forall[]`` (do-notation in the List monad)
  - Function composition, ``compose`` (like Haskell's ``.`` operator),
    aliased to unpythonic's currying right-compose ``composerc``
  - Linked list utilities ``cons``, ``car``, ``cdr``, ``ll``, ``llist``, ``nil``
  - Folds and scans ``foldl``, ``foldr``, ``scanl``, ``scanr``
  - Memoization ``memoize``, ``gmemoize``, ``imemoize``, ``fimemoize``
  - Functional updates ``fup`` and ``fupdate``
  - Immutable dict ``frozendict``
  - Mathematical sequences ``s``, ``m``, ``mg``
  - Iterable utilities ``islice`` (unpythonic's version), ``take``, ``drop``,
    ``split_at``, ``first``, ``second``, ``nth``, ``last``
  - Function arglist reordering utilities ``flip``, ``rotate``

For detailed documentation of the language features, see
[unpythonic](https://github.com/Technologicat/unpythonic) and
[``unpythonic.syntax``](https://github.com/Technologicat/unpythonic/tree/master/macro_extras).

The builtin ``let[]`` constructs are ``let``, ``letseq``, ``letrec``, the
decorator versions ``dlet``, ``dletseq``, ``dletrec``, the block
versions (decorator, call immediately, replace def'd name with result)
``blet``, ``bletseq``, ``bletrec``. Bindings may be made using any syntax
variant supported by ``unpythonic.syntax``.

The builtin ``do[]`` constructs are ``do`` and ``do0``.

For more, import from [``unpythonic``](https://github.com/Technologicat/unpythonic), the standard library of Pytkell
(on top of what Python itself already provides).

The lazifier uses MacroPy ``lazy[]`` promises from ``macropy.quick_lambda``.


### What Pytkell is

Pytkell is a dialect of Python implemented in MacroPy. It makes Python feel
slightly more haskelly.

This dialect is mainly intended as an example of what is possible, and for
system testing the dialect machinery and ``unpythonic``.

This module is the dialect definition, invoked by ``dialects.DialectFinder``
when it detects a lang-import that matches our module name.


### Comboability

Not comboable with most of the block macros in ``unpythonic.syntax``, because
``curry`` and ``lazify`` appear in the dialect template, hence at the lexically
outermost position.

Only first-pass macros (outside-in) that should expand after ``lazify`` has
recorded its userlambdas (currently unpythonic provides no such macros) and
second-pass (inside-out) macros that should expand before ``curry`` (there are
two, namely ``tco`` and ``continuations``) can be used in programs written
in the Pytkell dialect.


### Why "Pytkell"?

The other obvious contraction *Pyskell* sounds like a serious programming
language, whereas *Pytkell* is obviously something quickly thrown together
for system testing.


### CAUTION

No instrumentation exists (or is even planned) for the Pytkell layer; you'll
have to use regular Python tooling to profile, debug, and such.

This layer is not quite as thin as Lispython's, but the Pytkell dialect is not
intended for serious production use, either.
