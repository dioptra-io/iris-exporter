set -euo pipefail
shopt -s nullglob globstar

aws() {
  command aws --endpoint-url="${AWS_S3_ENDPOINT_URL}" "$@"
}

aws_does_not_exists() {
  aws s3 ls "$1" >/dev/null && exit 1 || exit 0
}

clickhouse() {
  command clickhouse client \
    --optimize_aggregation_in_order 1 \
    --max_memory_usage "${CLICKHOUSE_MAX_MEMORY_USAGE:-16Gi}" \
    --max_threads 1 \
    --database "${CLICKHOUSE_DATABASE:-default}" \
    --host "${CLICKHOUSE_HOST:-localhost}" \
    --user "${CLICKHOUSE_USERNAME:-default}" \
    --password "${CLICKHOUSE_PASSWORD:-}" \
    --query "${1}"
}

pv() {
  command pv --line-mode --size="$1"
}

require() {
  hash "$@" || exit 127
}

zstd() {
  command zstd -1
}

test_aws() {
  aws s3 ls "${AWS_S3_BUCKET}" >/dev/null && echo "S3: OK"
}

test_clickhouse()  {
   clickhouse "SELECT 'ClickHouse: OK'"
}

require aws
require clickhouse
require pv
require zstd
