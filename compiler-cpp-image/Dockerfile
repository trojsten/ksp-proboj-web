FROM docker.io/library/debian:13-slim

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install build-essential python3 pipx python3-dev build-essential libcap-dev \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home compiler
USER compiler

RUN PIP_NO_CACHE_DIR=off pipx install  parent==25.1
ENV PATH="/home/compiler/.local/bin/:$PATH"
COPY compile.sh /home/compiler/.local/bin/compile

WORKDIR /data
CMD ["compile"]
