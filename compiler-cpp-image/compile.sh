#!/usr/bin/env bash

export CXXFLAGS="-O2 -std=c++20"
exec parent \
  --cpu-time 30000 \
  --real-time 30000 \
  /usr/bin/make player
