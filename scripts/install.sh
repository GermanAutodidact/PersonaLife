#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m unittest discover -s tests -v
printf '%s\n' 'PersonaLife ready. Run .venv/bin/personalife persona create'
