#!/usr/bin/env bash

# shellcheck source=scripts/common.sh
. "${BASH_SOURCE%/*}/common.sh"

test_clickhouse
test_s3
