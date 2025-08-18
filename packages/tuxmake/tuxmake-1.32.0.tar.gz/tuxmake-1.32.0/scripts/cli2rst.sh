#!/bin/sh

set -eu

tmpfile=$(mktemp)
trap 'rm -f $tmpfile' INT TERM EXIT
python3 -m tuxmake --help > "${tmpfile}"
sed -i -e '/^Build input options:/,$ !d; /^  -/{x;p;x}' "${tmpfile}"
cp "${tmpfile}" "$1"
