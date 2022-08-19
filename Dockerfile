FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
        awscli \
        curl \
        pv \
        python3-pip \
        zstd \
    && rm -rf /var/lib/apt/lists/*

# Install ClickHouse client
COPY --from=clickhouse/clickhouse-server:22 /bin/clickhouse /bin/clickhouse

# Install the scripts
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY scripts scripts
