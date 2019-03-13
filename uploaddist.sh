#!/bin/bash
VERSION="$1"
twine upload dist/pydialect-${VERSION}.tar.gz dist/pydialect-${VERSION}-py3-none-any.whl
