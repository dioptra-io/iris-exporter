set -euo pipefail
shopt -s nullglob globstar

: "${CLICKHOUSE_HOST:=clickhouse.docker.localhost}"
: "${CLICKHOUSE_DATABASE:=iris}"
: "${CLICKHOUSE_USERNAME:=iris}"
: "${CLICKHOUSE_PASSWORD:=iris}"
: "${CLICKHOUSE_MAX_MEMORY_USAGE:=16Gi}"
: "${S3_ACCESS_KEY_ID:=minioadmin}"
: "${S3_SECRET_ACCESS_KEY:=minioadmin}"
: "${S3_BUCKET:=public-exports}"
: "${S3_ENDPOINT_URL:=http://minio.docker.localhost}"

# We expose environment variables with the same name as Iris settings.
# Here we remap some variables to match the names expected by the AWS CLI.
export AWS_ACCESS_KEY_ID=${S3_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=${S3_SECRET_ACCESS_KEY}

require() {
  hash "$@" || exit 127
}

# Check that the required programs are installed.
# This must be performed before defining functions with the same name.
require aws
require clickhouse
require pantrace
require pv
require zstd

clickhouse() {
  command clickhouse client \
    --database "${CLICKHOUSE_DATABASE}" \
    --host "${CLICKHOUSE_HOST}" \
    --user "${CLICKHOUSE_USERNAME}" \
    --password "${CLICKHOUSE_PASSWORD}" \
    --max_memory_usage "${CLICKHOUSE_MAX_MEMORY_USAGE}" \
    --max_threads 1 \
    --optimize_aggregation_in_order 1 \
    --query "${1}"
}

pv() {
  command pv --line-mode --size="$1"
}

s3() {
  aws --endpoint-url="${S3_ENDPOINT_URL}" s3 "$@"
}

s3_does_not_exists() {
  s3 ls "$1" >/dev/null && exit 1 || exit 0
}

zstd() {
  command zstd -1
}

# Perform some basic tests
clickhouse "SELECT 'ClickHouse: OK'"
s3 ls "${S3_BUCKET}" >/dev/null && echo "S3: OK"
