# quay.io/pypa/manylinux_2_28_x86_64

alias python=/opt/python/cp312-cp312/bin/python

pip wheel -v . --config-settings=fetch-hwloc=True --wheel-dir dist/

python -c "from pyhwloc import Topology"

python dev/check_plugins.py
