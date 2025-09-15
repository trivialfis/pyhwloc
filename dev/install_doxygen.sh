#!/usr/bin/env bash

echo "sh: CONDA_ENV ${CONDA_PREFIX}"

cd /ws/doxygen
mkdir build
cd build
cmake -GNinja -Duse_libclang=ON -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX ..
time ninja
ninja install
cd /ws
rm -rf doxygen
