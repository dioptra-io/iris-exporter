set -euo pipefail
shopt -s nullglob globstar

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

require aws
require clickhouse
require pv
require zstd
