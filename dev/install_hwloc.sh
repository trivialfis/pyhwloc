#!/usr/bin/env bash

cd hwloc
echo "Run autogen"
./autogen.sh
./configure --prefix=$CONDA_PREFIX
time make -j$(nproc) install
