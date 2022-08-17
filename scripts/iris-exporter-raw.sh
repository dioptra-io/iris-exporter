#!/usr/bin/env bash

# shellcheck source=scripts/common.sh
. "${BASH_SOURCE%/*}/common.sh"

if [ $# -ne 2 ]; then
    echo "$0 MEASUREMENT_UUID AGENT_UUID"
    exit 1
fi

test_aws
test_clickhouse

measurement_id="${1//-/_}__${2//-/_}"
url="s3://${AWS_S3_BUCKET}/$1__$2__csv.csv.zst"

query="SELECT * FROM results__${measurement_id} FORMAT CSVWithNames"
total=$(clickhouse "SELECT COUNT() FROM results__${measurement_id}")

if $(aws_does_not_exists "${url}"); then
  clickhouse "${query}" | pv "${total}" | zstd | aws s3 cp - "${url}" || aws s3 rm "${url}"
fi
