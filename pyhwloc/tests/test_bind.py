from pyhwloc.core import get_membind, set_membind, hwloc_membind_flags_t
import ctypes

from .test_core import Topology


def test_membind() -> None:
    topo = Topology()
    flags = hwloc_membind_flags_t.HWLOC_MEMBIND_STRICT
    get_membind(topo.hdl, new_nodeset, ctypes.byref(newpolicy), flags)
