#!/usr/bin/env bash

# shellcheck source=scripts/common.sh
. "${BASH_SOURCE%/*}/common.sh"

aws() {
    command aws --endpoint-url="${AWS_S3_ENDPOINT_URL}" "$@"
}

clickhouse() {
    command clickhouse client \
        --optimize_aggregation_in_order 1 \
        --max_memory_usage "${CLICKHOUSE_MAX_MEMORY_USAGE:-16Gi}" \
        --database "${CLICKHOUSE_DATABASE:-default}" \
        --host "${CLICKHOUSE_HOST:-localhost}" \
        --user "${CLICKHOUSE_USERNAME:-default}" \
        --password "${CLICKHOUSE_PASSWORD:-}" \
        --query "${1}"
}

pv() {
    command pv --line-mode --size="$1" --name="$2"
}

require() {
    hash "$@" || exit 127;
}

count_query() {
    local measurement_id="${1//-/_}__${2//-/_}"
    cat <<EOF
    SELECT uniqExact((
        probe_protocol,
        probe_src_addr,
        probe_dst_addr,
        probe_src_port,
        probe_dst_port,
    ))
    FROM results__${measurement_id}
    WHERE round = 1
EOF
}

traceroutes_query() {
    local measurement_id="${1//-/_}__${2//-/_}"
    cat <<EOF
    SELECT
        probe_protocol,
        probe_src_addr,
        probe_dst_addr,
        probe_src_port,
        probe_dst_port,
        groupArray((
            formatDateTime(capture_timestamp, '%Y-%m-%dT%H:%M:%SZ'),
            probe_ttl,
            reply_ttl,
            reply_size,
            reply_mpls_labels,
            reply_src_addr,
            rtt
        )) AS replies
    FROM results__${measurement_id}
    -- WHERE {self.filters(subset)}
    WHERE round = 1
        AND NOT destination_host_reply
        AND NOT destination_prefix_reply
        AND NOT private_probe_dst_prefix
        AND NOT private_reply_src_addr
        AND time_exceeded_reply
        AND valid_probe_protocol
    GROUP BY (
        probe_protocol,
        probe_src_addr,
        probe_dst_addr,
        probe_src_port,
        probe_dst_port,
    )
    FORMAT JSONEachRow
EOF
}

if [ $# -ne 2 ]; then
    echo "$0 MEASUREMENT_UUID AGENT_UUID"
    exit 1
fi

query=$(traceroutes_query "$1" "$2")
total=$(clickhouse "$(count_query "$1" "$2")")

url="s3://${AWS_S3_BUCKET}/$1__$2__atlas.jsonl.zst"
clickhouse "${query}" | pv "${total}" "iris-to-atlas" | iris-to-atlas | zstd | aws s3 cp - "${url}" || aws s3 rm "${url}"

url="s3://${AWS_S3_BUCKET}/$1__$2__warts-trace.warts.zst"
clickhouse "${query}" | pv "${total}" "iris-to-warts-trace" | iris-to-warts-trace | zstd | aws s3 cp - "${url}" || aws s3 rm "${url}"
