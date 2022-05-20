#!/usr/bin/env bash

# shellcheck source=scripts/common.sh
. "${BASH_SOURCE%/*}/common.sh"

count_query() {
    cat <<EOF
    SELECT COUNT() FROM results__$1
EOF
}

results_query() {
    cat <<EOF
    SELECT * FROM results__$1 FORMAT CSV
EOF
}

if [ $# -ne 2 ]; then
    echo "$0 MEASUREMENT_UUID AGENT_UUID"
    exit 1
fi

measurement_id="${1//-/_}__${2//-/_}"
query=$(traceroutes_query "$measurement_id")
total=$(clickhouse "$(count_query "$measurement_id")")

#url="s3://${AWS_S3_BUCKET}/$1__$2__atlas.jsonl.zst"
#clickhouse "${query}" | pv "${total}" "iris-to-atlas" | iris-to-atlas | zstd | aws s3 cp - "${url}" || aws s3 rm "${url}"
#
#url="s3://${AWS_S3_BUCKET}/$1__$2__warts-trace.warts.zst"
#clickhouse "${query}" | pv "${total}" "iris-to-warts-trace" | iris-to-warts-trace | zstd | aws s3 cp - "${url}" || aws s3 rm "${url}"
