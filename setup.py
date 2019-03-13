# -*- coding: utf-8 -*-
#
"""setuptools-based setup.py for Pydialect.

Tested on Python 3.4.

Usage as usual with setuptools:
    python3 setup.py build
    python3 setup.py sdist
    python3 setup.py bdist_wheel --universal
    python3 setup.py install

For details, see
    http://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference
or
    python3 setup.py --help
    python3 setup.py --help-commands
    python3 setup.py --help bdist_wheel  # or any command
"""

#########################################################
# General config
#########################################################

# Name of the top-level package of the library.
#
# This is also the top level of its source tree, relative to the top-level project directory setup.py resides in.
#
libname="pydialect"

# Short description for package list on PyPI
#
SHORTDESC="Build languages on Python."

# Long description for package homepage on PyPI
#
DESC="""Pydialect makes Python into a language platform, à la Racket. It provides the
plumbing that allows to create, in Python, dialects that compile into Python
at import time.

An extension to the Python language doesn't need to make it into the Python core,
*or even be desirable for inclusion* into the Python core, in order to be useful.

Building on functions and syntactic macros, customization of the language itself
is one more tool for the programmer to extract patterns, at a higher level.
Hence, beside language experimentation, such extensions can be used as a
framework that allows shorter and/or more readable programs.

Pydialect places language-creation power in the hands of its users, without the
need to go to extreme lengths to hack CPython itself or implement from scratch
a custom language that compiles to Python AST or bytecode.

Pydialect is geared toward creating languages that extend Python and look
almost like Python, but extend or modify its syntax and/or semantics.
Hence *dialects*.

That said, Pydialect itself is only a lightweight infrastructure hook that makes
it convenient to define and use dialects. To implement the actual semantics
for your dialect (which is where all the interesting things happen), you may
want to look at [MacroPy](https://github.com/azazel75/macropy). Examples can be
found in [unpythonic](https://github.com/Technologicat/unpythonic); see especially
the macros (comprising about one half of ``unpythonic``). On packaging a set of
semantics into a Pydialect definition, look at the example dialects included
in the Pydialect distribution.

Example of a module using a dialect::

    from __lang__ import lispython

    print("hello, my dialect is {}".format(__lang__))

    c = cons(1, 2)
    assert tuple(c) == (1, 2)
    assert car(c) == 1
    assert cdr(c) == 2
    assert ll(1, 2, 3) == llist((1, 2, 3))

    x = let[(a, 21) in 2*a]
    assert x == 42

    x = letseq[((a, 1),
                (a, 2*a),
                (a, 2*a)) in
               a]
    assert x == 4

    a = lambda x: cond[x < 0, "nope",
                       x % 2 == 0, "even",
                       "odd"]
    assert a(-1) == "nope"
    assert a(2) == "even"
    assert a(3) == "odd"

    def fact(n):
        def f(k, acc):
            if k == 1:
                return acc
            f(k - 1, k*acc)  # implicit return in tail position, like in Lisps
        f(n, acc=1)
    assert fact(4) == 24
    fact(5000)  # automatic TCO, no crash

    square = lambda x: x**2
    assert square(3) == 9
    assert square.__name__ == "square"  # lambdas are auto-named
"""

# Set up data files for packaging.
#
# Directories (relative to the top-level directory where setup.py resides) in which to look for data files.
datadirs  = ()

# File extensions to be considered as data files. (Literal, no wildcards.)
dataexts  = (".py", ".ipynb",  ".sh",  ".lyx", ".tex", ".txt", ".pdf")

# Standard documentation to detect (and package if it exists).
#
standard_docs     = ["README", "LICENSE", "TODO", "CHANGELOG", "AUTHORS"]  # just the basename without file extension
standard_doc_exts = [".md", ".rst", ".txt", ""]  # commonly .md for GitHub projects, but other projects may use .rst or .txt (or even blank).

#########################################################
# Init
#########################################################

import os
from setuptools import setup

# Gather user-defined data files
#
# http://stackoverflow.com/questions/13628979/setuptools-how-to-make-package-contain-extra-data-folder-and-all-folders-inside
#
datafiles = []
#getext = lambda filename: os.path.splitext(filename)[1]
#for datadir in datadirs:
#    datafiles.extend( [(root, [os.path.join(root, f) for f in files if getext(f) in dataexts])
#                       for root, dirs, files in os.walk(datadir)] )

# Add standard documentation (README et al.), if any, to data files
#
detected_docs = []
for docname in standard_docs:
    for ext in standard_doc_exts:
        filename = "".join( (docname, ext) )  # relative to the directory in which setup.py resides
        if os.path.isfile(filename):
            detected_docs.append(filename)
datafiles.append( ('.', detected_docs) )

# Extract __version__ from the package __init__.py
# (since it's not a good idea to actually run __init__.py during the build process).
#
# http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
#
import ast
init_py_path = os.path.join('dialects', '__init__.py')
version = '0.0.unknown'
try:
    with open(init_py_path) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            print( "WARNING: Version information not found in '%s', using placeholder '%s'" % (init_py_path, version), file=sys.stderr )
except FileNotFoundError:
    print( "WARNING: Could not find file '%s', using placeholder version information '%s'" % (init_py_path, version), file=sys.stderr )

#########################################################
# Call setup()
#########################################################

setup(
    name = "pydialect",
    version = version,
    author = "Juha Jeronen",
    author_email = "juha.m.jeronen@gmail.com",
    url = "https://github.com/Technologicat/pydialect",

    description = SHORTDESC,
    long_description = DESC,

    license = "BSD",

    # free-form text field; http://stackoverflow.com/questions/34994130/what-platforms-argument-to-setup-in-setup-py-does
    platforms = ["Linux"],

    # See
    #    https://pypi.python.org/pypi?%3Aaction=list_classifiers
    #
    # for the standard classifiers.
    #
    classifiers = [ "Development Status :: 4 - Beta",
                    "Environment :: Console",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: BSD License",
                    "Operating System :: POSIX :: Linux",
                    "Programming Language :: Python",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: 3.4",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules"
                  ],

    # See
    #    http://setuptools.readthedocs.io/en/latest/setuptools.html
    #
    setup_requires = [],
    install_requires = [],
    provides = ["pydialect"],

    # keywords for PyPI (in case you upload your project)
    #
    # e.g. the keywords your project uses as topics on GitHub, minus "python" (if there)
    #
    keywords = ["metaprogramming", "programming-language-development", "dialects"],

    # Declare packages so that  python -m setup build  will copy .py files (especially __init__.py).
    #
    # This **does not** automatically recurse into subpackages, so they must also be declared.
    #
    packages = ["dialects", "lispython"],

    scripts = ["pydialect"],

    zip_safe = False,  # macros are not zip safe, because the zip importer fails to find sources, and MacroPy needs them.

    # Custom data files not inside a Python package
    data_files = datafiles
)

