FROM golang:1.21.4-bookworm as build

WORKDIR /work
RUN git clone https://github.com/trojsten/ksp-proboj.git .

WORKDIR /work/runner
RUN go build -o ../output .

FROM debian:12-slim

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install python3 pypy3 \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home executor
USER executor

ENV PATH="/home/executor/.local/bin/:$PATH"
COPY --from=build /work/output /home/executor/.local/bin/runner

WORKDIR /match
CMD ["runner", "config.json", "games.json"]
