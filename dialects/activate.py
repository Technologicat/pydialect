# -*- coding: utf-8 -*-
"""Install the import hook.

Reloading this module refreshes the import hook to the start of ``sys.meta_path``.
"""

from . import importer
import sys

def _find_dialectfinder():
    cls = type(importer.DialectFinder)  # singleton, but id might change if module reloaded
    for j, finder in enumerate(sys.meta_path):
        if isinstance(finder, cls):
            return j
    return -1

j = _find_dialectfinder()
if j > -1:
    sys.meta_path.pop(j)

sys.meta_path.insert(0, importer.DialectFinder)
