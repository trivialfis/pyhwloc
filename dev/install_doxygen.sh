#!/usr/bin/env bash

cd /ws/doxygen
mkdir build
cd build \
cmake -GNinja -Duse_libclang=ON -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX ..
time ninja
ninja install
