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

aws() {
  command aws --endpoint-url="${S3_ENDPOINT_URL}" "$@"
}

aws_does_not_exists() {
  aws s3 ls "$1" >/dev/null && exit 1 || exit 0
}

clickhouse() {
  command clickhouse client \
    --optimize_aggregation_in_order 1 \
    --max_memory_usage "${CLICKHOUSE_MAX_MEMORY_USAGE}" \
    --max_threads 1 \
    --database "${CLICKHOUSE_DATABASE}" \
    --host "${CLICKHOUSE_HOST}" \
    --user "${CLICKHOUSE_USERNAME}" \
    --password "${CLICKHOUSE_PASSWORD}" \
    --query "${1}"
}

pv() {
  command pv --line-mode --size="$1" --name="$2"
}

require() {
  hash "$@" || exit 127
}

zstd() {
  command zstd -1
}

test_clickhouse() {
  clickhouse "SELECT 'ClickHouse: OK'"
}

test_s3() {
  aws s3 ls "${S3_BUCKET}" >/dev/null && echo "S3: OK"
}

require aws
require clickhouse
require pv
require zstd
