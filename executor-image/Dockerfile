FROM docker.io/library/golang:1.21.4-bookworm as build

WORKDIR /work
RUN git clone https://github.com/trojsten/ksp-proboj.git .

WORKDIR /work/runner
RUN go build -o ../output .

FROM docker.io/library/debian:13-slim

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install python3 pipx pypy3 python3-dev build-essential libcap-dev \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home executor && chmod 755 /home/executor
USER executor

RUN PIP_NO_CACHE_DIR=off pipx install parent==25.1

ENV PATH="/home/executor/.local/bin:$PATH"
COPY --from=build /work/output /home/executor/.local/bin/runner

WORKDIR /match
CMD ["runner", "config.json", "games.json"]
