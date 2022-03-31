FROM python:3.10
WORKDIR /usr/bin

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY iris-exporter-list.py iris-exporter-list.py
COPY iris-exporter-single.sh iris-exporter-single.sh
