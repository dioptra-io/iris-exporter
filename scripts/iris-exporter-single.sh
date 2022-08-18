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

test_clickhouse
test_s3

measurement_uuid=$1
agent_uuid=$2

query=$(traceroutes_query "${measurement_uuid}" "${agent_uuid}")
total=$(clickhouse "$(count_query "${measurement_uuid}" "${agent_uuid}")")

# TODO: warts -> warts-trace in pantrace
for format in atlas warts; do
  url="s3://${S3_BUCKET}/${measurement_uuid}__${agent_uuid}__${format}.jsonl.zst"
  if aws_does_not_exists "${url}"; then
    clickhouse "${query}" | pv "${total}" | pantrace --from iris --to ${format} | zstd | aws s3 cp - "${url}" || aws s3 rm "${url}"
  fi
done
