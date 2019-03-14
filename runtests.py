#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess

import dialects.activate

# https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters
# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
CHEAD = "\033[32m"  # dark green
CPASS = "\033[92m"  # light green
CFAIL = "\033[91m"  # light red
CEND = "\033[39m"   # reset FG color to default

_blacklist = ["build", "dist"]
def findtestpaths(root):
    toplevel_subdirs = sorted([fn for fn in os.listdir(root) if os.path.isdir(os.path.join(root, fn)) and 
                                                                fn not in _blacklist and
                                                                not fn.endswith(".egg-info") and
                                                                not fn.startswith(".")])
    out = []
    def doit(path):
        subdirs = [fn for fn in os.listdir(path) if os.path.isdir(os.path.join(path, fn)) and not fn.startswith(".")]
        if "test" in subdirs:
            out.append(os.path.join(path, "test"))
        for x in subdirs:
            doit(os.path.join(path, x))
    for x in toplevel_subdirs:
        doit(os.path.join(root, x))
    return out

def listtestmodules(path):
    testfiles = listtestfiles(path)
    testmodules = [modname(path, fn) for fn in testfiles]
    return list(sorted(testmodules))

def listtestfiles(path, prefix="test_", suffix=".py"):
    return [fn for fn in os.listdir(path) if fn.startswith(prefix) and fn.endswith(suffix)]

def modname(path, filename):  # some/dir/mod.py --> some.dir.mod
    t = '.{}'.format(os.path.sep)
    if path.startswith(t):  # remove './' at the start
        path = path[len(t):]
    modpath = re.sub(os.path.sep, r".", path)
    themod = re.sub(r"\.py$", r"", filename)
    return ".".join([modpath, themod])

def runtests(testsetname, modules, command_prefix):
    print(CHEAD + "*** Testing {} ***".format(testsetname) + CEND)
    fails = 0
    for mod in modules:
        print(CHEAD + "*** Running {} ***".format(mod) + CEND)
        # TODO: migrate to subprocess.run (Python 3.5+)
        ret = subprocess.call(command_prefix + [mod])
        if ret == 0:
            print(CPASS + "*** PASS ***" + CEND)
        else:
            fails += 1
            print(CFAIL + "*** FAIL ***" + CEND)
    if not fails:
        print(CPASS + "*** ALL OK in {} ***".format(testsetname) + CEND)
    else:
        print(CFAIL + "*** AT LEAST ONE FAIL in {} ***".format(testsetname))
    return fails

def main():
    thepaths = findtestpaths(".")
    thetestmodules = [module for path in thepaths for module in listtestmodules(path)]

    totalfails = 0
    totalfails += runtests("dialects",
                           thetestmodules,
                           [os.path.join(".", "pydialect"), "-m"])

    if not totalfails:
        print(CPASS + "*** ALL OK ***" + CEND)
    else:
        print(CFAIL + "*** AT LEAST ONE FAIL ***" + CEND)

if __name__ == '__main__':
    main()
