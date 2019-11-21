## LisThEll: it's not Lisp, it's not Python, it's not Haskell

Powered by [Pydialect](https://github.com/Technologicat/pydialect) and
[unpythonic](https://github.com/Technologicat/unpythonic).

```python
from __lang__ import listhell

from unpythonic import foldr, cons, nil, ll

(print, "hello from LisThEll")

my_map = lambda f: (foldr, (compose, cons, f), nil)
assert (my_map, double, (q, 1, 2, 3)) == (ll, 2, 4, 6)
```

### Features

In terms of ``unpythonic.syntax``, we implicitly enable ``prefix`` and ``curry``
for the whole module.

The following are dialect builtins:

  - ``apply``, aliased to ``unpythonic.fun.apply``
  - ``compose``, aliased to unpythonic's currying right-compose ``composerc``
  - ``q``, ``u``, ``kw`` for the prefix syntax (note these are not MacroPy's
    ``q`` and ``u``, but unpythonic's, specifically for ``prefix``)

For detailed documentation of the language features, see
[unpythonic](https://github.com/Technologicat/unpythonic) and
[``unpythonic.syntax``](https://github.com/Technologicat/unpythonic/tree/master/doc/macros.md).


### What LisThEll is

Essentially a demonstration of how Python could look, if it had Lisp's prefix syntax
for function calls and Haskell's automatic currying.

It's also a minimal example of how to make a dialect based on an ``ast_transformer``.


### Comboability

Only first-pass macros (outside-in) that should expand after ``curry``
(currently unpythonic provides no such macros) and second-pass (inside-out)
macros that should expand before ``curry`` (there are two, namely ``tco`` and
``continuations``) can be used in programs written in the LisThEll dialect.


### Notes

If you like the idea and want autocurry for a Lisp, try
[spicy](https://github.com/Technologicat/spicy) for [Racket](https://racket-lang.org/).

### CAUTION

Not intended for serious use.
