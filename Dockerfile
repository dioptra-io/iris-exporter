FROM docker.io/library/ubuntu:22.04
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

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup.sh \
    && bash rustup.sh --default-toolchain nightly -y \
    && rm rustup.sh

RUN curl -L https://github.com/dioptra-io/clickhouse-builds/releases/download/20211210/clickhouse.$(arch).zst | zstd > /usr/bin/clickhouse \
     && chmod +x /usr/bin/clickhouse

RUN cargo install pantrace

WORKDIR /usr/bin

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY scripts/iris-exporter-list.py iris-exporter-list.py
COPY scripts/iris-exporter-single.sh iris-exporter-single.sh
