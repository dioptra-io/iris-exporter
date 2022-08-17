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

# Install pantrace
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup.sh \
    && bash rustup.sh --default-toolchain nightly -y \
    && rm rustup.sh
RUN cargo install pantrace

# Install ClickHouse client
COPY --from=clickhouse/clickhouse-server:22 /bin/clickhouse /bin/clickhouse

# Install the scripts
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY scripts scripts
