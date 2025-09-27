#!/usr/bin/env bash

cd /ws/hwloc/doc
HWLOC_DOXYGEN_GENERATE_XML=YES doxygen ./doxygen.cfg
cp -r doxygen-doc/xml /ws/xml
cd ..                           # hwloc
