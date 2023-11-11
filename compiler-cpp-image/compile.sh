#!/usr/bin/env bash

export CXXFLAGS="-O2 -std=c++20"
exec parent \
  --cpu-time 5000 \
  --real-time 5000 \
  --exitcode \
  /usr/bin/make player
