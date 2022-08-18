FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.cargo/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        awscli \
        build-essential \
        curl \
        pv \
        python3-pip \
        zstd \
    && rm -rf /var/lib/apt/lists/*

# Install ClickHouse client
COPY --from=clickhouse/clickhouse-server:22 /bin/clickhouse /bin/clickhouse

# Install pantrace
COPY --from=ghcr.io/dioptra-io/pantrace:main /usr/local/bin/pantrace /bin/pantrace

# Install the scripts
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY scripts scripts
