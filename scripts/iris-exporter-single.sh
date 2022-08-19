#!/usr/bin/env bash

# shellcheck source=scripts/common.sh
. "${BASH_SOURCE%/*}/common.sh"

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
    WHERE NOT destination_host_reply
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

measurement_uuid=$1
agent_uuid=$2

query=$(traceroutes_query "${measurement_uuid}" "${agent_uuid}")
total=$(clickhouse "$(count_query "${measurement_uuid}" "${agent_uuid}")")

url="s3://${S3_BUCKET}/${measurement_uuid}__${agent_uuid}__jsonl.jsonl.zst"
if $(s3_does_not_exists "${url}"); then
  echo "Exporting: ${url}"
  clickhouse "${query}" | pv "${total}" | zstd | s3 cp - "${url}" || s3 rm "${url}"
else
  echo "Already existing: ${url}"
fi
