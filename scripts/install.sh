#!/bin/sh
set -eu
personalife_language="${1:-en}"
case "$personalife_language" in
  en|de) ;;
  *) printf '%s\n' 'Language must be en or de / Sprache muss en oder de sein' >&2; exit 2 ;;
esac
cd "$(dirname "$0")/.."
fail() {
  if [ "$personalife_language" = de ]; then printf '%s\n' "$2" >&2; else printf '%s\n' "$1" >&2; fi
  exit 1
}
python3 -m venv .venv || fail 'Python environment creation failed' 'Das Erstellen der Python-Umgebung ist fehlgeschlagen'
.venv/bin/python -m pip install . || fail 'PersonaLife installation failed' 'Die Installation von PersonaLife ist fehlgeschlagen'
.venv/bin/python -m unittest discover -s tests -v || fail 'PersonaLife tests failed' 'Die PersonaLife-Tests sind fehlgeschlagen'
if [ "$personalife_language" = de ]; then
  printf '%s\n' 'PersonaLife ist bereit. Starte .venv/bin/personalife --language de persona create'
else
  printf '%s\n' 'PersonaLife ready. Run .venv/bin/personalife --language en persona create'
fi
