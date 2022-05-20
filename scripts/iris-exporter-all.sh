#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob globstar

if [ $# -ne 1 ]; then
    echo "$0 LISTFILE"
    exit 1
fi

parallel \
  --arg-file="$1" \
  --colsep=' ' \
  --jobs=1 \
  --memfree=1G \
  --retries=1 \
  --verbose \
  scripts/iris-exporter-single.sh "{1}" "{2}"
