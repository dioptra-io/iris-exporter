#!/usr/bin/env bash

# shellcheck source=scripts/common.sh
. "${BASH_SOURCE%/*}/common.sh"

if [ $# -ne 1 ]; then
    echo "$0 LISTFILE"
    exit 1
fi

test_clickhouse
test_s3

parallel \
  --arg-file="$1" \
  --colsep=' ' \
  --jobs=8 \
  --memfree=1G \
  --progress \
  --retries=1 \
  scripts/iris-exporter-single.sh "{1}" "{2}"