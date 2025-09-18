#!/usr/bin/env bash

cd hwloc
echo "Run autogen"
./autogen.sh
./configure --prefix=$CONDA_PREFIX --disable-nvml --enable-doxygen
time make -j$(nproc) install

cd doc
HWLOC_DOXYGEN_GENERATE_XML=YES doxygen ./doxygen.cfg
cp -r doxygen-doc/xml /ws/xml
cd ..				# hwloc
git clean -xdf
