# quay.io/pypa/manylinux_2_28_x86_64

export PATH=/opt/python/cp312-cp312/bin/:$PATH

pip wheel -v . --config-settings=fetch-hwloc=True --wheel-dir dist/

python -c "from pyhwloc import Topology"

python dev/check_plugins.py
