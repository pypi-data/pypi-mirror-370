set -eu

tmpfile=$(mktemp)
trap 'rm -f $tmpfile' INT TERM EXIT

cp README.md "${tmpfile}"
sed -i -e '
/_TOC_/,+1d
s#docs/##
' "${tmpfile}"
cp "${tmpfile}" $@
