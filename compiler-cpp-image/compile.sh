#!/usr/bin/env bash

export CXXFLAGS="-O2 -std=c++23"
exec parent \
  --cpu-time 30000 \
  --real-time 30000 \
  /usr/bin/make player
