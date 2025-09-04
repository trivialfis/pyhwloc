# Copyright (c) 2025, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import annotations

import ctypes
import os
from ctypes.util import find_library
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, Type, TypeVar


def normpath(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


prefix = os.path.expanduser("~/ws/pyhwloc_dev/hwloc/build/hwloc/.libs")
_LIB = ctypes.CDLL(os.path.join(prefix, "libhwloc.so"), use_errno=True)

hwloc_bitmap_t = ctypes.c_void_p
hwloc_const_bitmap_t = ctypes.c_void_p
bitmap_t = hwloc_bitmap_t
const_bitmap_t = hwloc_const_bitmap_t

hwloc_uint64_t = ctypes.c_uint64
hwloc_pid_t = ctypes.c_int

HWLOC_UNKNOWN_INDEX = ctypes.c_uint(-1).value


_libc = ctypes.CDLL(find_library("c"))
_libc.strerror.restype = ctypes.c_char_p
_libc.strerror.argtypes = [ctypes.c_int]


_file_path = normpath(__file__)
_lib_path = normpath(
    os.path.join(os.path.dirname(_file_path), os.path.pardir, "_lib", "libpyhwloc.so")
)
_pyhwloc_lib = ctypes.cdll.LoadLibrary(_lib_path)


class HwLocError(RuntimeError):
    def __init__(self, status: int, errno: int, msg: bytes) -> None:
        self.status = status
        self.errno = errno
        self.msg = msg.decode("utf-8")

        super().__init__(
            f"status: {self.status}, errno: {self.errno}, error: {self.msg}"
        )


_P = ParamSpec("_P")
_R = TypeVar("_R")


def _cfndoc(fn: Callable[_P, _R]) -> Callable[_P, _R]:
    doc = f"See :cpp:func:`hwloc_{fn.__name__}`"
    fn.__doc__ = doc
    return fn


def _cenumdoc(enum: Type) -> Type:
    doc = f"""See :cpp:enum:`{enum.__name__}`."""
    enum.__doc__ = doc
    return enum


def _free(ptr: Any) -> None:
    _libc.free(ptr)


def _checkc(status: int) -> None:
    if status != 0:
        errno = ctypes.get_errno()
        msg = _libc.strerror(errno)
        raise HwLocError(status, errno, msg)


#############
# API version
#############

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00138.php


_LIB.hwloc_get_api_version.restype = ctypes.c_uint


@_cfndoc
def get_api_version() -> int:
    # major = v >> 16
    # minor = (v >> 8) & 0xFF
    # rev = v & 0xFF
    return _LIB.hwloc_get_api_version()


##################################################
# Object Sets (hwloc_cpuset_t and hwloc_nodeset_t)
##################################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00139.php


hwloc_cpuset_t = bitmap_t
hwloc_nodeset_t = bitmap_t

hwloc_const_cpuset_t = const_bitmap_t
hwloc_const_nodeset_t = const_bitmap_t


##############
# Object Types
##############

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00140.php


@_cenumdoc
class hwloc_obj_type_t(IntEnum):
    HWLOC_OBJ_MACHINE = 0
    HWLOC_OBJ_PACKAGE = 1
    HWLOC_OBJ_DIE = 2
    HWLOC_OBJ_CORE = 3
    HWLOC_OBJ_PU = 4
    HWLOC_OBJ_L1CACHE = 5
    HWLOC_OBJ_L2CACHE = 6
    HWLOC_OBJ_L3CACHE = 7
    HWLOC_OBJ_L4CACHE = 8
    HWLOC_OBJ_L5CACHE = 9
    HWLOC_OBJ_L1ICACHE = 10
    HWLOC_OBJ_L2ICACHE = 11
    HWLOC_OBJ_L3ICACHE = 12
    HWLOC_OBJ_GROUP = 13
    HWLOC_OBJ_NUMANODE = 14
    HWLOC_OBJ_MEMCACHE = 15
    HWLOC_OBJ_BRIDGE = 16
    HWLOC_OBJ_PCI_DEVICE = 17
    HWLOC_OBJ_OS_DEVICE = 18
    HWLOC_OBJ_MISC = 19
    HWLOC_OBJ_TYPE_MAX = 20


@_cenumdoc
class hwloc_obj_cache_type_t(IntEnum):
    HWLOC_OBJ_CACHE_UNIFIED = 0
    HWLOC_OBJ_CACHE_DATA = 1
    HWLOC_OBJ_CACHE_INSTRUCTION = 2


@_cenumdoc
class hwloc_obj_bridge_type_t(IntEnum):
    HWLOC_OBJ_BRIDGE_HOST = 0
    HWLOC_OBJ_BRIDGE_PCI = 1


@_cenumdoc
class hwloc_obj_osdev_type_t(IntEnum):
    HWLOC_OBJ_OSDEV_STORAGE = 1 << 0
    HWLOC_OBJ_OSDEV_MEMORY = 1 << 1
    HWLOC_OBJ_OSDEV_GPU = 1 << 2
    HWLOC_OBJ_OSDEV_COPROC = 1 << 3
    HWLOC_OBJ_OSDEV_NETWORK = 1 << 4
    HWLOC_OBJ_OSDEV_OPENFABRICS = 1 << 5
    HWLOC_OBJ_OSDEV_DMA = 1 << 6


HWLOC_TYPE_UNORDERED = -1

_LIB.hwloc_compare_types.argtypes = [ctypes.c_int, ctypes.c_int]
_LIB.hwloc_compare_types.restype = ctypes.c_int


@_cfndoc
def compare_types(type1: hwloc_obj_type_t, type2: hwloc_obj_type_t) -> int:
    return _LIB.hwloc_compare_types(type1, type2)


#################################
# Object Structure and Attributes
#################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00141.php


class hwloc_info_s(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),  # Info name
        ("value", ctypes.c_char_p),  # Info value
    ]


class hwloc_infos_s(ctypes.Structure):
    _fields_ = [
        ("array", ctypes.POINTER(hwloc_info_s)),
        ("count", ctypes.c_uint),
        ("allocated", ctypes.c_uint),
    ]


if TYPE_CHECKING:
    InfosPtr = ctypes._Pointer[hwloc_infos_s]
else:
    InfosPtr = ctypes._Pointer


class hwloc_memory_page_type_s(ctypes.Structure):
    _fields_ = [
        ("size", hwloc_uint64_t),  # Size of pages
        ("count", hwloc_uint64_t),  # Number of pages of this size
    ]


class hwloc_numanode_attr_s(ctypes.Structure):
    _fields_ = [
        ("local_memory", hwloc_uint64_t),  # Local memory (in bytes)
        ("page_types_len", ctypes.c_uint),  # Size of array page_types
        (
            "page_types",
            ctypes.POINTER(hwloc_memory_page_type_s),
        ),  # Array of local memory page types
    ]


class hwloc_cache_attr_s(ctypes.Structure):
    _fields_ = [
        ("size", hwloc_uint64_t),  # Size of cache in bytes
        ("depth", ctypes.c_uint),  # Depth of cache (e.g., L1, L2, ...etc.)
        ("linesize", ctypes.c_uint),  # Cache-line size in bytes. 0 if unknown
        (
            "associativity",
            ctypes.c_int,
        ),  # Ways of associativity, -1 if fully associative, 0 if unknown
        ("type", ctypes.c_int),  # hwloc_obj_cache_type_t - Cache type
    ]


class hwloc_group_attr_s(ctypes.Structure):
    _fields_ = [
        ("depth", ctypes.c_uint),  # Depth of group object
        ("kind", ctypes.c_uint),  # Internally-used kind of group
        (
            "subkind",
            ctypes.c_uint,
        ),  # Internally-used subkind to distinguish different levels
        (
            "dont_merge",
            ctypes.c_ubyte,
        ),  # Flag preventing groups from being automatically merged
    ]


class hwloc_pcidev_attr_s(ctypes.Structure):
    _fields_ = [
        (
            "domain",
            ctypes.c_uint,
        ),  # Domain number (xxxx in PCI BDF notation xxxx:yy:zz.t)
        ("bus", ctypes.c_ubyte),  # Bus number (yy in PCI BDF notation xxxx:yy:zz.t)
        ("dev", ctypes.c_ubyte),  # Device number (zz in PCI BDF notation xxxx:yy:zz.t)
        (
            "func",
            ctypes.c_ubyte,
        ),  # Function number (t in PCI BDF notation xxxx:yy:zz.t)
        ("prog_if", ctypes.c_ubyte),  # Register-level programming interface number
        (
            "class_id",
            ctypes.c_ushort,
        ),  # The class number (first two bytes, without prog_if)
        ("vendor_id", ctypes.c_ushort),  # Vendor ID (xxxx in [xxxx:yyyy])
        ("device_id", ctypes.c_ushort),  # Device ID (yyyy in [xxxx:yyyy])
        ("subvendor_id", ctypes.c_ushort),  # Sub-Vendor ID
        ("subdevice_id", ctypes.c_ushort),  # Sub-Device ID
        ("revision", ctypes.c_ubyte),  # Revision number
        ("linkspeed", ctypes.c_float),  # Link speed in GB/s
    ]


class hwloc_bridge_upstream_u(ctypes.Union):
    _fields_ = [
        (
            "pci",
            hwloc_pcidev_attr_s,
        ),  # PCI attribute of the upstream part as a PCI device
    ]


class hwloc_bridge_downstream_pci_s(ctypes.Structure):
    _fields_ = [
        ("domain", ctypes.c_uint),  # Domain number the downstream PCI buses
        ("secondary_bus", ctypes.c_ubyte),  # First PCI bus number below the bridge
        ("subordinate_bus", ctypes.c_ubyte),  # Highest PCI bus number below the bridge
    ]


class hwloc_bridge_downstream_u(ctypes.Union):
    _fields_ = [
        ("pci", hwloc_bridge_downstream_pci_s),
    ]


class hwloc_bridge_attr_s(ctypes.Structure):
    _fields_ = [
        ("upstream", hwloc_bridge_upstream_u),
        (
            "upstream_type",
            ctypes.c_int,
        ),  # hwloc_obj_bridge_type_t - Upstream Bridge type
        ("downstream", hwloc_bridge_downstream_u),
        (
            "downstream_type",
            ctypes.c_int,
        ),  # hwloc_obj_bridge_type_t - Downstream Bridge type
        ("depth", ctypes.c_uint),
    ]


class hwloc_osdev_attr_s(ctypes.Structure):
    _fields_ = [
        (
            "types",
            ctypes.c_int,
        ),  # hwloc_obj_osdev_types_t - OR'ed set of at least one hwloc_obj_osdev_type_e
    ]


# Main attribute union
class hwloc_obj_attr_u(ctypes.Union):
    _fields_ = [
        ("numanode", hwloc_numanode_attr_s),  # NUMA node-specific Object Attributes
        ("cache", hwloc_cache_attr_s),  # Cache-specific Object Attributes
        ("group", hwloc_group_attr_s),  # Group-specific Object Attributes
        ("pcidev", hwloc_pcidev_attr_s),  # PCI Device specific Object Attributes
        ("bridge", hwloc_bridge_attr_s),  # Bridge specific Object Attributes
        ("osdev", hwloc_osdev_attr_s),  # OS Device specific Object Attributes
    ]


class hwloc_obj(ctypes.Structure):
    pass


hwloc_obj._fields_ = [
    ("type", ctypes.c_int),  # hwloc_obj_type_t
    ("subtype", ctypes.c_char_p),
    ("os_index", ctypes.c_uint),
    ("name", ctypes.c_char_p),
    ("total_memory", hwloc_uint64_t),
    ("attr", ctypes.POINTER(hwloc_obj_attr_u)),
    ("depth", ctypes.c_int),
    ("logical_index", ctypes.c_uint),
    ("next_cousin", ctypes.POINTER(hwloc_obj)),
    ("prev_cousin", ctypes.POINTER(hwloc_obj)),
    ("parent", ctypes.POINTER(hwloc_obj)),
    ("sibling_rank", ctypes.c_uint),
    ("next_sibling", ctypes.POINTER(hwloc_obj)),
    ("prev_sibling", ctypes.POINTER(hwloc_obj)),
    ("arity", ctypes.c_uint),
    ("children", ctypes.POINTER(ctypes.POINTER(hwloc_obj))),
    ("first_child", ctypes.POINTER(hwloc_obj)),
    ("last_child", ctypes.POINTER(hwloc_obj)),
    ("symmetric_subtree", ctypes.c_int),
    ("memory_arity", ctypes.c_uint),
    ("memory_first_child", ctypes.POINTER(hwloc_obj)),
    ("io_arity", ctypes.c_uint),
    ("io_first_child", ctypes.POINTER(hwloc_obj)),
    ("misc_arity", ctypes.c_uint),
    ("misc_first_child", ctypes.POINTER(hwloc_obj)),
    ("cpuset", hwloc_cpuset_t),
    ("complete_cpuset", hwloc_cpuset_t),
    ("nodeset", hwloc_nodeset_t),
    ("complete_nodeset", hwloc_nodeset_t),
    ("infos", hwloc_infos_s),
    ("userdata", ctypes.c_void_p),
    ("gp_index", hwloc_uint64_t),
]


obj_t = ctypes.POINTER(hwloc_obj)

if TYPE_CHECKING:
    ObjType = ctypes._Pointer[hwloc_obj]
else:
    ObjType = ctypes._Pointer


###################################
# Topology Creation and Destruction
###################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00142.php#ga9d1e76ee15a7dee158b786c30b6a6e38

topology_t = ctypes.c_void_p

_LIB.hwloc_topology_init.argtypes = [ctypes.POINTER(topology_t)]
_LIB.hwloc_topology_init.restype = ctypes.c_int


@_cfndoc
def topology_init(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_init(ctypes.byref(topology)))


_LIB.hwloc_topology_load.argtypes = [topology_t]
_LIB.hwloc_topology_load.restype = ctypes.c_int


@_cfndoc
def topology_load(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_load(topology))


_LIB.hwloc_topology_destroy.argtypes = [topology_t]
_LIB.hwloc_topology_destroy.restype = None


@_cfndoc
def topology_destroy(topology: topology_t) -> None:
    _LIB.hwloc_topology_destroy(topology)


_LIB.hwloc_topology_dup.argtypes = [ctypes.POINTER(topology_t), topology_t]
_LIB.hwloc_topology_dup.restype = ctypes.c_int


@_cfndoc
def topology_dup(topology: topology_t) -> topology_t:
    new = topology_t()
    _checkc(_LIB.hwloc_topology_dup(ctypes.byref(new), topology))
    return new


@_cfndoc
def topology_abi_check(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_abi_check(topology))


@_cfndoc
def topology_check(topology: topology_t) -> None:
    _LIB.hwloc_topology_check(topology)


#################################
# Object levels, depths and types
#################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00143.php#gae54d1782ca9b54bea915f5c18a9158fa


@_cenumdoc
class hwloc_get_type_depth_e(IntEnum):
    HWLOC_TYPE_DEPTH_UNKNOWN = -1
    HWLOC_TYPE_DEPTH_MULTIPLE = -2
    HWLOC_TYPE_DEPTH_NUMANODE = -3
    HWLOC_TYPE_DEPTH_BRIDGE = -4
    HWLOC_TYPE_DEPTH_PCI_DEVICE = -5
    HWLOC_TYPE_DEPTH_OS_DEVICE = -6
    HWLOC_TYPE_DEPTH_MISC = -7
    HWLOC_TYPE_DEPTH_MEMCACHE = -8


@_cfndoc
def topology_get_depth(topology: topology_t) -> int:
    return _LIB.hwloc_topology_get_depth(topology)


_LIB.hwloc_get_type_depth.argtypes = [topology_t, ctypes.c_int]
_LIB.hwloc_get_type_depth.restype = ctypes.c_int


@_cfndoc
def get_type_depth(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _LIB.hwloc_get_type_depth(topology, obj_type)


_LIB.hwloc_get_memory_parents_depth.argtypes = [topology_t]
_LIB.hwloc_get_memory_parents_depth.restype = ctypes.c_int


@_cfndoc
def get_memory_parents_depth(topology: topology_t) -> int:
    return _LIB.hwloc_get_memory_parents_depth(topology)


_pyhwloc_lib.pyhwloc_get_type_or_above_depth.argtypes = [topology_t, ctypes.c_int]
_pyhwloc_lib.pyhwloc_get_type_or_above_depth.restype = ctypes.c_int


@_cfndoc
def get_type_or_above_depth(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _pyhwloc_lib.pyhwloc_get_type_or_above_depth(topology, obj_type)


_LIB.hwloc_get_depth_type.argtypes = [topology_t, ctypes.c_int]
_LIB.hwloc_get_depth_type.restype = ctypes.c_int


@_cfndoc
def get_depth_type(topology: topology_t, depth: int) -> hwloc_obj_type_t:
    return hwloc_obj_type_t(_LIB.hwloc_get_depth_type(topology, depth))


_pyhwloc_lib.pyhwloc_get_nbobjs_by_type.argtypes = [topology_t, ctypes.c_int]
_pyhwloc_lib.pyhwloc_get_nbobjs_by_type.restype = ctypes.c_int


@_cfndoc
def get_nbobjs_by_type(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _pyhwloc_lib.pyhwloc_get_nbobjs_by_type(topology, obj_type)


_pyhwloc_lib.pyhwloc_get_root_obj.argtypes = [topology_t]
_pyhwloc_lib.pyhwloc_get_root_obj.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_root_obj(topology: topology_t) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_root_obj(topology)


_pyhwloc_lib.pyhwloc_get_obj_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_get_obj_by_type.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_obj_by_type(
    topology: topology_t, obj_type: hwloc_obj_type_t, idx: int
) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_obj_by_type(topology, obj_type, idx)


_pyhwloc_lib.pyhwloc_get_next_obj_by_depth.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(hwloc_obj),
]
_pyhwloc_lib.pyhwloc_get_next_obj_by_depth.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_obj_by_depth(topology: topology_t, depth: int, prev: ObjType) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_next_obj_by_depth(topology, depth, prev)


_pyhwloc_lib.pyhwloc_get_next_obj_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(hwloc_obj),
]
_pyhwloc_lib.pyhwloc_get_next_obj_by_type.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_obj_by_type(
    topology: topology_t, obj_type: hwloc_obj_type_t, prev: ObjType
) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_next_obj_by_type(topology, obj_type, prev)


@_cfndoc
def get_nbobjs_by_depth(topology: topology_t, depth: int) -> int:
    return _LIB.hwloc_get_nbobjs_by_depth(topology, depth)


_LIB.hwloc_get_obj_by_depth.argtypes = [topology_t, ctypes.c_int, ctypes.c_uint]
_LIB.hwloc_get_obj_by_depth.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_obj_by_depth(topology: topology_t, depth: int, idx: int) -> ObjType:
    return _LIB.hwloc_get_obj_by_depth(topology, depth, idx)


_LIB.hwloc_bitmap_dup.argtypes = [bitmap_t]
_LIB.hwloc_bitmap_dup.restype = bitmap_t

#############################################################
# Converting between Object Types and Attributes, and Strings
#############################################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00144.php#ga6a38b931e5d45e8af4323a169482fe39

_LIB.hwloc_obj_type_string.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_string.restype = ctypes.c_char_p


@_cfndoc
def hwloc_obj_type_string(obj_type: hwloc_obj_type_t) -> bytes:
    return _LIB.hwloc_obj_type_string(obj_type).value


_LIB.hwloc_obj_type_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    obj_t,
    ctypes.c_int,
]
_LIB.hwloc_obj_type_snprintf.restype = ctypes.c_int


@_cfndoc
def obj_type_snprintf(
    string: ctypes.c_char_p | ctypes.Array, size: int, obj: ObjType, verbose: int
) -> int:
    return _LIB.hwloc_obj_type_snprintf(string, size, obj, verbose)


_LIB.hwloc_obj_attr_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    obj_t,
    ctypes.c_char_p,
    ctypes.c_int,
]
_LIB.hwloc_obj_attr_snprintf.restype = ctypes.c_int


@_cfndoc
def obj_attr_snprintf(
    string: ctypes.c_char_p | ctypes.Array,
    size: int,
    obj: ObjType,
    separator: ctypes.c_char_p | bytes,
    verbose: int,
) -> int:
    return _LIB.hwloc_obj_attr_snprintf(string, size, obj, separator, verbose)


_LIB.hwloc_type_sscanf.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(hwloc_obj_attr_u),
    ctypes.c_size_t,
]
_LIB.hwloc_type_sscanf.restype = ctypes.c_int


@_cfndoc
def type_sscanf(string: str) -> tuple[hwloc_obj_type_t, hwloc_obj_attr_u | None]:
    string_bytes = string.encode("utf-8")
    typep = ctypes.c_int()

    attrp = hwloc_obj_attr_u()
    result = _LIB.hwloc_type_sscanf(
        string_bytes, ctypes.byref(typep), ctypes.byref(attrp), ctypes.sizeof(attrp)
    )
    _checkc(result)
    return hwloc_obj_type_t(typep.value), attrp


_LIB.hwloc_type_sscanf_as_depth.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_int),
    topology_t,
    ctypes.POINTER(ctypes.c_int),
]
_LIB.hwloc_type_sscanf_as_depth.restype = ctypes.c_int


@_cfndoc
def type_sscanf_as_depth(
    string: str, topology: topology_t
) -> tuple[hwloc_obj_type_t, int]:
    string_bytes = string.encode("utf-8")
    typep = ctypes.c_int()
    depthp = ctypes.c_int()

    _checkc(
        _LIB.hwloc_type_sscanf_as_depth(
            string_bytes, ctypes.byref(typep), topology, ctypes.byref(depthp)
        )
    )

    return hwloc_obj_type_t(typep.value), depthp.value


#######################################
# Consulting and Adding Info Attributes
#######################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00145.php


_pyhwloc_lib.pyhwloc_get_info_by_name.argtypes = [
    ctypes.POINTER(hwloc_infos_s),
    ctypes.c_char_p,
]
_pyhwloc_lib.pyhwloc_get_info_by_name.restype = ctypes.c_char_p


@_cfndoc
def obj_get_info_by_name(obj: ObjType, name: str) -> str | None:
    name_bytes = name.encode("utf-8")
    result = _pyhwloc_lib.pyhwloc_get_info_by_name(
        ctypes.byref(obj.contents.infos), name_bytes
    )
    if result:
        return result.decode("utf-8")
    return None


_pyhwloc_lib.pyhwloc_obj_add_info.argtypes = [obj_t, ctypes.c_char_p, ctypes.c_char_p]
_pyhwloc_lib.pyhwloc_obj_add_info.restype = ctypes.c_int


@_cfndoc
def obj_add_info(obj: ObjType, name: str, value: str) -> None:
    if not name or not value:
        raise ValueError("name and value must be non-empty strings")

    name_bytes = name.encode("utf-8")
    value_bytes = value.encode("utf-8")
    _checkc(_pyhwloc_lib.pyhwloc_obj_add_info(obj, name_bytes, value_bytes))


_LIB.hwloc_obj_set_subtype.argtypes = [topology_t, obj_t, ctypes.c_char_p]
_LIB.hwloc_obj_set_subtype.restype = ctypes.c_int


@_cfndoc
def obj_set_subtype(topology: topology_t, obj: ObjType, subtype: str) -> None:
    subtype_bytes = subtype.encode("utf-8")
    _checkc(_LIB.hwloc_obj_set_subtype(topology, obj, subtype_bytes))


##########################
# Looking at Cache Objects
##########################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00155.php


_pyhwloc_lib.pyhwloc_get_cache_type_depth.argtypes = [
    topology_t,
    ctypes.c_uint,
    ctypes.c_int,
]
_pyhwloc_lib.pyhwloc_get_cache_type_depth.restype = ctypes.c_int


@_cfndoc
def get_cache_type_depth(
    topology: topology_t, cachelevel: int, cachetype: hwloc_obj_cache_type_t
) -> int:
    # This can return HWLOC_TYPE_DEPTH_UNKNOWN (-1) and HWLOC_TYPE_DEPTH_MULTIPLE (-2)
    return _pyhwloc_lib.pyhwloc_get_cache_type_depth(topology, cachelevel, cachetype)


_pyhwloc_lib.pyhwloc_get_cache_covering_cpuset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
]
_pyhwloc_lib.pyhwloc_get_cache_covering_cpuset.restype = obj_t


@_cfndoc
def get_cache_covering_cpuset(
    topology: topology_t, cpuset: hwloc_const_cpuset_t
) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_cache_covering_cpuset(topology, cpuset)


_pyhwloc_lib.pyhwloc_get_shared_cache_covering_obj.argtypes = [topology_t, obj_t]
_pyhwloc_lib.pyhwloc_get_shared_cache_covering_obj.restype = obj_t


@_cfndoc
def get_shared_cache_covering_obj(topology: topology_t, obj: ObjType) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_shared_cache_covering_obj(topology, obj)


#####################
# Finding I/O objects
#####################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00160.php


_pyhwloc_lib.pyhwloc_get_non_io_ancestor_obj.argtypes = [
    topology_t,
    ctypes.POINTER(hwloc_obj),
]
_pyhwloc_lib.pyhwloc_get_non_io_ancestor_obj.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_non_io_ancestor_obj(topology: topology_t, ioobj: ObjType) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_non_io_ancestor_obj(topology, ioobj)


_pyhwloc_lib.pyhwloc_get_next_pcidev.argtypes = [topology_t, ctypes.POINTER(hwloc_obj)]
_pyhwloc_lib.pyhwloc_get_next_pcidev.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_pcidev(topology: topology_t, prev: ObjType) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_next_pcidev(topology, prev)


_pyhwloc_lib.pyhwloc_get_pcidev_by_busid.argtypes = [
    topology_t,
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_get_pcidev_by_busid.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_pcidev_by_busid(
    topology: topology_t, domain: int, bus: int, dev: int, func: int
) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_pcidev_by_busid(topology, domain, bus, dev, func)


_pyhwloc_lib.pyhwloc_get_pcidev_by_busidstring.argtypes = [topology_t, ctypes.c_char_p]
_pyhwloc_lib.pyhwloc_get_pcidev_by_busidstring.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_pcidev_by_busidstring(topology: topology_t, busid: str) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_pcidev_by_busidstring(
        topology, busid.encode("utf-8")
    )


_pyhwloc_lib.pyhwloc_get_next_osdev.argtypes = [topology_t, ctypes.POINTER(hwloc_obj)]
_pyhwloc_lib.pyhwloc_get_next_osdev.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_osdev(topology: topology_t, prev: ObjType) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_next_osdev(topology, prev)


_pyhwloc_lib.pyhwloc_get_next_bridge.argtypes = [topology_t, ctypes.POINTER(hwloc_obj)]
_pyhwloc_lib.pyhwloc_get_next_bridge.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_bridge(topology: topology_t, prev: ObjType | None) -> ObjType:
    return _pyhwloc_lib.pyhwloc_get_next_bridge(topology, prev)


_pyhwloc_lib.pyhwloc_bridge_covers_pcibus.argtypes = [
    ctypes.POINTER(hwloc_obj),
    ctypes.c_uint,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_bridge_covers_pcibus.restype = ctypes.c_int


@_cfndoc
def bridge_covers_pcibus(bridge: ObjType, domain: int, bus: int) -> int:
    return _pyhwloc_lib.pyhwloc_bridge_covers_pcibus(bridge, domain, bus)


################
# The bitmap API
################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00161.php#gae679434c1a5f41d3560a8a7e2c1b0dee

_pyhwloc_lib.pyhwloc_bitmap_alloc.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
_pyhwloc_lib.pyhwloc_bitmap_alloc.restype = int


@_cfndoc
def bitmap_alloc() -> hwloc_bitmap_t:
    ptr = ctypes.c_void_p()
    _checkc(_pyhwloc_lib.pyhwloc_bitmap_alloc(ctypes.byref(ptr)))
    return ptr


_pyhwloc_lib.pyhwloc_bitmap_alloc_full.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
_pyhwloc_lib.pyhwloc_bitmap_alloc_full.restype = int


@_cfndoc
def bitmap_alloc_full() -> hwloc_bitmap_t:
    ptr = ctypes.c_void_p()
    _checkc(_pyhwloc_lib.pyhwloc_bitmap_alloc_full(ctypes.byref(ptr)))
    return ptr


_LIB.hwloc_bitmap_free.argtypes = [hwloc_bitmap_t]


@_cfndoc
def bitmap_free(bitmap: hwloc_bitmap_t) -> None:
    _LIB.hwloc_bitmap_free(bitmap)


_LIB.hwloc_bitmap_dup.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_dup.restype = hwloc_bitmap_t


@_cfndoc
def bitmap_dup(bitmap: hwloc_const_bitmap_t) -> hwloc_bitmap_t:
    return _LIB.hwloc_bitmap_dup(bitmap)


_LIB.hwloc_bitmap_copy.argtypes = [hwloc_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_copy.restype = ctypes.c_int


@_cfndoc
def bitmap_copy(dst: hwloc_bitmap_t, src: hwloc_const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_copy(dst, src))


# Bitmap/String Conversion
_LIB.hwloc_bitmap_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_snprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_snprintf(
    buf: ctypes.c_char_p | ctypes.Array, buflen: int, bitmap: hwloc_const_bitmap_t
) -> int:
    n_written = _LIB.hwloc_bitmap_snprintf(buf, buflen, bitmap)
    if n_written == -1:
        _checkc(n_written)
    return n_written


_LIB.hwloc_bitmap_asprintf.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_asprintf.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_char_p)
@_cfndoc
def bitmap_asprintf(strp: ctypes._Pointer, bitmap: hwloc_const_bitmap_t) -> int:
    result = _LIB.hwloc_bitmap_asprintf(strp, bitmap)
    if result == -1:
        errno = ctypes.get_errno()
        msg = _libc.strerror(errno)
        raise HwLocError(-1, errno, msg)
    return result


_LIB.hwloc_bitmap_sscanf.argtypes = [hwloc_bitmap_t, ctypes.c_char_p]
_LIB.hwloc_bitmap_sscanf.restype = ctypes.c_int


@_cfndoc
def bitmap_sscanf(bitmap: hwloc_bitmap_t, string: str) -> None:
    string_bytes = string.encode("utf-8")
    _checkc(_LIB.hwloc_bitmap_sscanf(bitmap, string_bytes))


_LIB.hwloc_bitmap_list_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_list_snprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_list_snprintf(
    buf: ctypes.c_char_p, buflen: int, bitmap: hwloc_const_bitmap_t
) -> int:
    return _LIB.hwloc_bitmap_list_snprintf(buf, buflen, bitmap)


_LIB.hwloc_bitmap_list_asprintf.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_list_asprintf.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_char_p)
@_cfndoc
def bitmap_list_asprintf(strp: ctypes._Pointer, bitmap: hwloc_const_bitmap_t) -> int:
    result = _LIB.hwloc_bitmap_list_asprintf(strp, bitmap)
    if result == -1:
        errno = ctypes.get_errno()
        msg = _libc.strerror(errno)
        raise HwLocError(-1, errno, msg)
    return result


_LIB.hwloc_bitmap_list_sscanf.argtypes = [hwloc_bitmap_t, ctypes.c_char_p]
_LIB.hwloc_bitmap_list_sscanf.restype = ctypes.c_int


@_cfndoc
def bitmap_list_sscanf(bitmap: hwloc_bitmap_t, string: str) -> None:
    string_bytes = string.encode("utf-8")
    _checkc(_LIB.hwloc_bitmap_list_sscanf(bitmap, string_bytes))


_LIB.hwloc_bitmap_taskset_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_taskset_snprintf.restype = ctypes.c_int


@_cfndoc
def bitmap_taskset_snprintf(
    buf: ctypes.c_char_p, buflen: int, bitmap: hwloc_const_bitmap_t
) -> int:
    return _LIB.hwloc_bitmap_taskset_snprintf(buf, buflen, bitmap)


_LIB.hwloc_bitmap_taskset_asprintf.argtypes = [
    ctypes.POINTER(ctypes.c_char_p),
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_taskset_asprintf.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_char_p)
@_cfndoc
def bitmap_taskset_asprintf(strp: ctypes._Pointer, bitmap: hwloc_const_bitmap_t) -> int:
    result = _LIB.hwloc_bitmap_taskset_asprintf(strp, bitmap)
    if result == -1:
        errno = ctypes.get_errno()
        msg = _libc.strerror(errno)
        raise HwLocError(-1, errno, msg)
    return result


_LIB.hwloc_bitmap_taskset_sscanf.argtypes = [hwloc_bitmap_t, ctypes.c_char_p]
_LIB.hwloc_bitmap_taskset_sscanf.restype = ctypes.c_int


@_cfndoc
def bitmap_taskset_sscanf(bitmap: hwloc_bitmap_t, string: str) -> None:
    string_bytes = string.encode("utf-8")
    _checkc(_LIB.hwloc_bitmap_taskset_sscanf(bitmap, string_bytes))


_LIB.hwloc_bitmap_singlify.argtypes = [bitmap_t]

# Building bitmaps
_LIB.hwloc_bitmap_zero.argtypes = [hwloc_bitmap_t]


@_cfndoc
def bitmap_zero(bitmap: hwloc_bitmap_t) -> None:
    _LIB.hwloc_bitmap_zero(bitmap)


_LIB.hwloc_bitmap_fill.argtypes = [hwloc_bitmap_t]


@_cfndoc
def bitmap_fill(bitmap: hwloc_bitmap_t) -> None:
    _LIB.hwloc_bitmap_fill(bitmap)


_LIB.hwloc_bitmap_only.argtypes = [hwloc_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_only.restype = ctypes.c_int


@_cfndoc
def bitmap_only(bitmap: hwloc_bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_only(bitmap, id))


_LIB.hwloc_bitmap_allbut.argtypes = [hwloc_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_allbut.restype = ctypes.c_int


@_cfndoc
def bitmap_allbut(bitmap: hwloc_bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_allbut(bitmap, id))


_LIB.hwloc_bitmap_from_ulong.argtypes = [hwloc_bitmap_t, ctypes.c_ulong]
_LIB.hwloc_bitmap_from_ulong.restype = ctypes.c_int


@_cfndoc
def bitmap_from_ulong(bitmap: hwloc_bitmap_t, mask: int) -> None:
    _checkc(_LIB.hwloc_bitmap_from_ulong(bitmap, mask))


_LIB.hwloc_bitmap_from_ith_ulong.argtypes = [
    hwloc_bitmap_t,
    ctypes.c_uint,
    ctypes.c_ulong,
]
_LIB.hwloc_bitmap_from_ith_ulong.restype = ctypes.c_int


@_cfndoc
def bitmap_from_ith_ulong(bitmap: hwloc_bitmap_t, i: int, mask: int) -> None:
    _checkc(_LIB.hwloc_bitmap_from_ith_ulong(bitmap, i, mask))


_LIB.hwloc_bitmap_from_ulongs.argtypes = [
    hwloc_bitmap_t,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ulong),
]
_LIB.hwloc_bitmap_from_ulongs.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_ulong)
@_cfndoc
def bitmap_from_ulongs(bitmap: hwloc_bitmap_t, nr: int, masks: ctypes._Pointer) -> None:
    _checkc(_LIB.hwloc_bitmap_from_ulongs(bitmap, nr, masks))


# Modifying bitmaps
_LIB.hwloc_bitmap_set.argtypes = [hwloc_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_set.restype = ctypes.c_int


@_cfndoc
def bitmap_set(bitmap: hwloc_bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_set(bitmap, id))


_LIB.hwloc_bitmap_set_range.argtypes = [hwloc_bitmap_t, ctypes.c_uint, ctypes.c_int]
_LIB.hwloc_bitmap_set_range.restype = ctypes.c_int


@_cfndoc
def bitmap_set_range(bitmap: hwloc_bitmap_t, begin: int, end: int) -> None:
    _checkc(_LIB.hwloc_bitmap_set_range(bitmap, begin, end))


_LIB.hwloc_bitmap_set_ith_ulong.argtypes = [
    hwloc_bitmap_t,
    ctypes.c_uint,
    ctypes.c_ulong,
]
_LIB.hwloc_bitmap_set_ith_ulong.restype = ctypes.c_int


@_cfndoc
def bitmap_set_ith_ulong(bitmap: hwloc_bitmap_t, i: int, mask: int) -> None:
    _checkc(_LIB.hwloc_bitmap_set_ith_ulong(bitmap, i, mask))


_LIB.hwloc_bitmap_clr.argtypes = [hwloc_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_clr.restype = ctypes.c_int


@_cfndoc
def bitmap_clr(bitmap: hwloc_bitmap_t, id: int) -> None:
    _checkc(_LIB.hwloc_bitmap_clr(bitmap, id))


_LIB.hwloc_bitmap_clr_range.argtypes = [hwloc_bitmap_t, ctypes.c_uint, ctypes.c_int]
_LIB.hwloc_bitmap_clr_range.restype = ctypes.c_int


@_cfndoc
def bitmap_clr_range(bitmap: hwloc_bitmap_t, begin: int, end: int) -> None:
    _checkc(_LIB.hwloc_bitmap_clr_range(bitmap, begin, end))


_LIB.hwloc_bitmap_singlify.argtypes = [hwloc_bitmap_t]
_LIB.hwloc_bitmap_singlify.restype = ctypes.c_int


@_cfndoc
def bitmap_singlify(bitmap: hwloc_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_singlify(bitmap))


# Consulting bitmaps
_LIB.hwloc_bitmap_to_ulong.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_to_ulong.restype = ctypes.c_ulong


@_cfndoc
def bitmap_to_ulong(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_to_ulong(bitmap)


_LIB.hwloc_bitmap_to_ith_ulong.argtypes = [hwloc_const_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_to_ith_ulong.restype = ctypes.c_ulong


@_cfndoc
def bitmap_to_ith_ulong(bitmap: hwloc_const_bitmap_t, i: int) -> int:
    return _LIB.hwloc_bitmap_to_ith_ulong(bitmap, i)


_LIB.hwloc_bitmap_to_ulongs.argtypes = [
    hwloc_const_bitmap_t,
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ulong),
]
_LIB.hwloc_bitmap_to_ulongs.restype = ctypes.c_int


# ctypes.POINTER(ctypes.c_ulong)
@_cfndoc
def bitmap_to_ulongs(
    bitmap: hwloc_const_bitmap_t, nr: int, masks: ctypes._Pointer
) -> None:
    _checkc(_LIB.hwloc_bitmap_to_ulongs(bitmap, nr, masks))


_LIB.hwloc_bitmap_nr_ulongs.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_nr_ulongs.restype = ctypes.c_int


@_cfndoc
def bitmap_nr_ulongs(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_nr_ulongs(bitmap)


_LIB.hwloc_bitmap_isset.argtypes = [hwloc_const_bitmap_t, ctypes.c_uint]
_LIB.hwloc_bitmap_isset.restype = ctypes.c_int


@_cfndoc
def bitmap_isset(bitmap: hwloc_const_bitmap_t, i: int) -> bool:
    return bool(_LIB.hwloc_bitmap_isset(bitmap, i))


_LIB.hwloc_bitmap_iszero.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_iszero.restype = ctypes.c_int


@_cfndoc
def bitmap_iszero(bitmap: hwloc_const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_iszero(bitmap))


_LIB.hwloc_bitmap_isfull.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_isfull.restype = ctypes.c_int


@_cfndoc
def bitmap_isfull(bitmap: hwloc_const_bitmap_t) -> bool:
    return bool(_LIB.hwloc_bitmap_isfull(bitmap))


_LIB.hwloc_bitmap_first.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_first.restype = ctypes.c_int


@_cfndoc
def bitmap_first(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_first(bitmap)


_LIB.hwloc_bitmap_next.argtypes = [hwloc_const_bitmap_t, ctypes.c_int]
_LIB.hwloc_bitmap_next.restype = ctypes.c_int


@_cfndoc
def bitmap_next(bitmap: hwloc_const_bitmap_t, prev: int) -> int:
    return _LIB.hwloc_bitmap_next(bitmap, prev)


_LIB.hwloc_bitmap_last.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_last.restype = ctypes.c_int


@_cfndoc
def bitmap_last(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_last(bitmap)


_LIB.hwloc_bitmap_weight.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_weight.restype = ctypes.c_int


@_cfndoc
def bitmap_weight(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_weight(bitmap)


_LIB.hwloc_bitmap_first_unset.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_first_unset.restype = ctypes.c_int


@_cfndoc
def bitmap_first_unset(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_first_unset(bitmap)


_LIB.hwloc_bitmap_next_unset.argtypes = [hwloc_const_bitmap_t, ctypes.c_int]
_LIB.hwloc_bitmap_next_unset.restype = ctypes.c_int


@_cfndoc
def bitmap_next_unset(bitmap: hwloc_const_bitmap_t, prev: int) -> int:
    return _LIB.hwloc_bitmap_next_unset(bitmap, prev)


_LIB.hwloc_bitmap_last_unset.argtypes = [hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_last_unset.restype = ctypes.c_int


@_cfndoc
def bitmap_last_unset(bitmap: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_last_unset(bitmap)


# Combining bitmaps
_LIB.hwloc_bitmap_or.argtypes = [
    hwloc_bitmap_t,
    hwloc_const_bitmap_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_or.restype = ctypes.c_int


@_cfndoc
def bitmap_or(
    res: hwloc_bitmap_t, bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> None:
    _checkc(_LIB.hwloc_bitmap_or(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_and.argtypes = [
    hwloc_bitmap_t,
    hwloc_const_bitmap_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_and.restype = ctypes.c_int


@_cfndoc
def bitmap_and(
    res: hwloc_bitmap_t, bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> None:
    _checkc(_LIB.hwloc_bitmap_and(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_andnot.argtypes = [
    hwloc_bitmap_t,
    hwloc_const_bitmap_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_andnot.restype = ctypes.c_int


@_cfndoc
def bitmap_andnot(
    res: hwloc_bitmap_t, bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> None:
    _checkc(_LIB.hwloc_bitmap_andnot(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_xor.argtypes = [
    hwloc_bitmap_t,
    hwloc_const_bitmap_t,
    hwloc_const_bitmap_t,
]
_LIB.hwloc_bitmap_xor.restype = ctypes.c_int


@_cfndoc
def bitmap_xor(
    res: hwloc_bitmap_t, bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> None:
    _checkc(_LIB.hwloc_bitmap_xor(res, bitmap1, bitmap2))


_LIB.hwloc_bitmap_not.argtypes = [hwloc_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_not.restype = ctypes.c_int


def bitmap_not(res: hwloc_bitmap_t, bitmap: hwloc_const_bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_not(res, bitmap))


# Comparing bitmaps
_LIB.hwloc_bitmap_intersects.argtypes = [hwloc_const_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_intersects.restype = ctypes.c_int


@_cfndoc
def bitmap_intersects(
    bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> bool:
    return bool(_LIB.hwloc_bitmap_intersects(bitmap1, bitmap2))


_LIB.hwloc_bitmap_isincluded.argtypes = [hwloc_const_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_isincluded.restype = ctypes.c_int


@_cfndoc
def bitmap_isincluded(
    sub_bitmap: hwloc_const_bitmap_t, super_bitmap: hwloc_const_bitmap_t
) -> bool:
    return bool(_LIB.hwloc_bitmap_isincluded(sub_bitmap, super_bitmap))


_LIB.hwloc_bitmap_isequal.argtypes = [hwloc_const_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_isequal.restype = ctypes.c_int


@_cfndoc
def bitmap_isequal(
    bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> bool:
    return bool(_LIB.hwloc_bitmap_isequal(bitmap1, bitmap2))


_LIB.hwloc_bitmap_compare_first.argtypes = [hwloc_const_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_compare_first.restype = ctypes.c_int


@_cfndoc
def bitmap_compare_first(
    bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t
) -> int:
    return _LIB.hwloc_bitmap_compare_first(bitmap1, bitmap2)


_LIB.hwloc_bitmap_compare.argtypes = [hwloc_const_bitmap_t, hwloc_const_bitmap_t]
_LIB.hwloc_bitmap_compare.restype = ctypes.c_int


@_cfndoc
def bitmap_compare(bitmap1: hwloc_const_bitmap_t, bitmap2: hwloc_const_bitmap_t) -> int:
    return _LIB.hwloc_bitmap_compare(bitmap1, bitmap2)


#############################
# Exporting Topologies to XML
#############################


@_cenumdoc
class hwloc_topology_export_xml_flags_e(IntEnum):
    HWLOC_TOPOLOGY_EXPORT_XML_FLAG_V2 = 1 << 1


_LIB.hwloc_topology_export_xml.argtypes = [topology_t, ctypes.c_char_p, ctypes.c_ulong]
_LIB.hwloc_topology_export_xml.restype = ctypes.c_int


@_cfndoc
def topology_export_xml(topology: topology_t, xmlpath: str, flags: int) -> None:
    _checkc(_LIB.hwloc_topology_export_xml(topology, xmlpath.encode("utf-8"), flags))


_LIB.hwloc_topology_export_xmlbuffer.argtypes = [
    topology_t,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_ulong,
]
_LIB.hwloc_topology_export_xmlbuffer.restype = ctypes.c_int


@_cfndoc
def topology_export_xmlbuffer(topology: topology_t, flags: int) -> str:
    xmlbuffer = ctypes.c_char_p()
    buflen = ctypes.c_int()
    _checkc(
        _LIB.hwloc_topology_export_xmlbuffer(
            topology, ctypes.byref(xmlbuffer), ctypes.byref(buflen), flags
        )
    )
    result = xmlbuffer.value.decode("utf-8") if xmlbuffer.value else ""
    _LIB.hwloc_free_xmlbuffer(topology, xmlbuffer)
    return result


_LIB.hwloc_free_xmlbuffer.argtypes = [topology_t, ctypes.c_char_p]
_LIB.hwloc_free_xmlbuffer.restype = None


@_cfndoc
def free_xmlbuffer(topology: topology_t, xmlbuffer: ctypes.c_char_p) -> None:
    _LIB.hwloc_free_xmlbuffer(topology, xmlbuffer)


export_callback_t = ctypes.CFUNCTYPE(
    None, ctypes.c_void_p, topology_t, ctypes.POINTER(hwloc_obj)
)

_LIB.hwloc_topology_set_userdata_export_callback.argtypes = [
    topology_t,
    export_callback_t,
]
_LIB.hwloc_topology_set_userdata_export_callback.restype = None


@_cfndoc
def topology_set_userdata_export_callback(
    topology: topology_t, export_cb: Callable
) -> None:
    _LIB.hwloc_topology_set_userdata_export_callback(topology, export_cb)


_LIB.hwloc_export_obj_userdata.argtypes = [
    ctypes.c_void_p,
    topology_t,
    ctypes.POINTER(hwloc_obj),
    ctypes.c_char_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
_LIB.hwloc_export_obj_userdata.restype = ctypes.c_int


@_cfndoc
def export_obj_userdata(
    reserved: ctypes.c_void_p,
    topology: topology_t,
    obj: ObjType,
    name: str,
    buf: ctypes.c_void_p,
    length: int,
) -> None:
    _checkc(
        _LIB.hwloc_export_obj_userdata(
            reserved, topology, obj, name.encode("utf-8"), buf, length
        )
    )


_LIB.hwloc_export_obj_userdata_base64.argtypes = [
    ctypes.c_void_p,
    topology_t,
    ctypes.POINTER(hwloc_obj),
    ctypes.c_char_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
_LIB.hwloc_export_obj_userdata_base64.restype = ctypes.c_int


@_cfndoc
def export_obj_userdata_base64(
    reserved: ctypes.c_void_p,
    topology: topology_t,
    obj: ObjType,
    name: str,
    buffer: ctypes.c_void_p,
    length: int,
) -> None:
    _checkc(
        _LIB.hwloc_export_obj_userdata_base64(
            reserved, topology, obj, name.encode("utf-8"), buffer, length
        )
    )


import_callback_t = ctypes.CFUNCTYPE(
    None,
    topology_t,
    ctypes.POINTER(hwloc_obj),
    ctypes.c_char_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
)

_LIB.hwloc_topology_set_userdata_import_callback.argtypes = [
    topology_t,
    import_callback_t,
]
_LIB.hwloc_topology_set_userdata_import_callback.restype = None


@_cfndoc
def topology_set_userdata_import_callback(
    topology: topology_t, import_cb: Callable
) -> None:
    _LIB.hwloc_topology_set_userdata_import_callback(topology, import_cb)


###################################
# Exporting Topologies to Synthetic
###################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00163.php


@_cenumdoc
class hwloc_topology_export_synthetic_flags_e(IntEnum):
    HWLOC_TOPOLOGY_EXPORT_SYNTHETIC_FLAG_NO_EXTENDED_TYPES = 1 << 0
    HWLOC_TOPOLOGY_EXPORT_SYNTHETIC_FLAG_NO_ATTRS = 1 << 1
    HWLOC_TOPOLOGY_EXPORT_SYNTHETIC_FLAG_V1 = 1 << 2
    HWLOC_TOPOLOGY_EXPORT_SYNTHETIC_FLAG_IGNORE_MEMORY = 1 << 3


_LIB.hwloc_topology_export_synthetic.argtypes = [
    topology_t,
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.c_ulong,
]
_LIB.hwloc_topology_export_synthetic.restype = ctypes.c_int


@_cfndoc
def topology_export_synthetic(
    topology: topology_t,
    buf: ctypes.c_char_p | ctypes.Array,
    buflen: int,
    flags: int,
) -> int:
    # A 1024-byte buffer should be large enough for exporting topologies in the vast
    # majority of cases.
    n_written = _LIB.hwloc_topology_export_synthetic(topology, buf, buflen, flags)
    if n_written == -1:
        errno = ctypes.get_errno()
        msg = _libc.strerror(errno)
        raise HwLocError(-1, errno, msg)
    return n_written


############################################
# Topology Detection Configuration and Query
############################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00149.php


class hwloc_topology_discovery_support(ctypes.Structure):
    _fields_ = [
        ("pu", ctypes.c_ubyte),
        ("numa", ctypes.c_ubyte),
        ("numa_memory", ctypes.c_ubyte),
        ("disallowed_pu", ctypes.c_ubyte),
        ("disallowed_numa", ctypes.c_ubyte),
        ("cpukind_efficiency", ctypes.c_ubyte),
    ]


class hwloc_topology_cpubind_support(ctypes.Structure):
    _fields_ = [
        ("set_thisproc_cpubind", ctypes.c_ubyte),
        ("get_thisproc_cpubind", ctypes.c_ubyte),
        ("set_proc_cpubind", ctypes.c_ubyte),
        ("get_proc_cpubind", ctypes.c_ubyte),
        ("set_thisthread_cpubind", ctypes.c_ubyte),
        ("get_thisthread_cpubind", ctypes.c_ubyte),
        ("set_thread_cpubind", ctypes.c_ubyte),
        ("get_thread_cpubind", ctypes.c_ubyte),
        ("get_thisproc_last_cpu_location", ctypes.c_ubyte),
        ("get_proc_last_cpu_location", ctypes.c_ubyte),
        ("get_thisthread_last_cpu_location", ctypes.c_ubyte),
    ]


class hwloc_topology_membind_support(ctypes.Structure):
    _fields_ = [
        ("set_thisproc_membind", ctypes.c_ubyte),
        ("get_thisproc_membind", ctypes.c_ubyte),
        ("set_proc_membind", ctypes.c_ubyte),
        ("get_proc_membind", ctypes.c_ubyte),
        ("set_thisthread_membind", ctypes.c_ubyte),
        ("get_thisthread_membind", ctypes.c_ubyte),
        ("alloc_membind", ctypes.c_ubyte),
        ("set_area_membind", ctypes.c_ubyte),
        ("get_area_membind", ctypes.c_ubyte),
        ("get_area_memlocation", ctypes.c_ubyte),
        ("firsttouch_membind", ctypes.c_ubyte),
        ("bind_membind", ctypes.c_ubyte),
        ("interleave_membind", ctypes.c_ubyte),
        ("weighted_interleave_membind", ctypes.c_ubyte),
        ("nexttouch_membind", ctypes.c_ubyte),
        ("migrate_membind", ctypes.c_ubyte),
    ]


class hwloc_topology_misc_support(ctypes.Structure):
    _fields_ = [
        ("imported_support", ctypes.c_ubyte),
    ]


class hwloc_topology_support(ctypes.Structure):
    _fields_ = [
        ("discovery", ctypes.POINTER(hwloc_topology_discovery_support)),
        ("cpubind", ctypes.POINTER(hwloc_topology_cpubind_support)),
        ("membind", ctypes.POINTER(hwloc_topology_membind_support)),
        ("misc", ctypes.POINTER(hwloc_topology_misc_support)),
    ]


@_cenumdoc
class hwloc_topology_flags_e(IntEnum):
    HWLOC_TOPOLOGY_FLAG_INCLUDE_DISALLOWED = 1 << 0
    HWLOC_TOPOLOGY_FLAG_IS_THISSYSTEM = 1 << 1
    HWLOC_TOPOLOGY_FLAG_THISSYSTEM_ALLOWED_RESOURCES = 1 << 2
    HWLOC_TOPOLOGY_FLAG_IMPORT_SUPPORT = 1 << 3
    HWLOC_TOPOLOGY_FLAG_RESTRICT_TO_CPUBINDING = 1 << 4
    HWLOC_TOPOLOGY_FLAG_RESTRICT_TO_MEMBINDING = 1 << 5
    HWLOC_TOPOLOGY_FLAG_DONT_CHANGE_BINDING = 1 << 6
    HWLOC_TOPOLOGY_FLAG_NO_DISTANCES = 1 << 7
    HWLOC_TOPOLOGY_FLAG_NO_MEMATTRS = 1 << 8
    HWLOC_TOPOLOGY_FLAG_NO_CPUKINDS = 1 << 9


@_cenumdoc
class hwloc_type_filter_e(IntEnum):
    HWLOC_TYPE_FILTER_KEEP_ALL = 0
    HWLOC_TYPE_FILTER_KEEP_NONE = 1
    HWLOC_TYPE_FILTER_KEEP_STRUCTURE = 2
    HWLOC_TYPE_FILTER_KEEP_IMPORTANT = 3


_LIB.hwloc_topology_set_flags.argtypes = [topology_t, ctypes.c_ulong]
_LIB.hwloc_topology_set_flags.restype = ctypes.c_int


@_cfndoc
def topology_set_flags(topology: topology_t, flags: int) -> None:
    _checkc(_LIB.hwloc_topology_set_flags(topology, flags))


_LIB.hwloc_topology_get_flags.argtypes = [topology_t]
_LIB.hwloc_topology_get_flags.restype = ctypes.c_ulong


@_cfndoc
def topology_get_flags(topology: topology_t) -> int:
    return _LIB.hwloc_topology_get_flags(topology)


_LIB.hwloc_topology_is_thissystem.argtypes = [topology_t]
_LIB.hwloc_topology_is_thissystem.restype = ctypes.c_int


@_cfndoc
def topology_is_thissystem(topology: topology_t) -> bool:
    return bool(_LIB.hwloc_topology_is_thissystem(topology))


_LIB.hwloc_topology_get_support.argtypes = [topology_t]
_LIB.hwloc_topology_get_support.restype = ctypes.POINTER(hwloc_topology_support)


if TYPE_CHECKING:
    SupportType = ctypes._Pointer[hwloc_topology_support]
else:
    SupportType = ctypes._Pointer


@_cfndoc
def topology_get_support(topology: topology_t) -> SupportType:
    return _LIB.hwloc_topology_get_support(topology)


_LIB.hwloc_topology_set_type_filter.argtypes = [topology_t, ctypes.c_int, ctypes.c_int]
_LIB.hwloc_topology_set_type_filter.restype = ctypes.c_int


@_cfndoc
def topology_set_type_filter(
    topology: topology_t, obj_type: hwloc_obj_type_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_type_filter(topology, obj_type, filter))


_LIB.hwloc_topology_get_type_filter.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
]
_LIB.hwloc_topology_get_type_filter.restype = ctypes.c_int


@_cfndoc
def topology_get_type_filter(
    topology: topology_t, obj_type: hwloc_obj_type_t
) -> hwloc_type_filter_e:
    filter = ctypes.c_int()
    _checkc(
        _LIB.hwloc_topology_get_type_filter(topology, obj_type, ctypes.byref(filter))
    )
    return hwloc_type_filter_e(filter.value)


@_cfndoc
def topology_set_all_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_all_types_filter(topology, filter))


@_cfndoc
def topology_set_cache_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_cache_types_filter(topology, filter))


@_cfndoc
def topology_set_icache_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_icache_types_filter(topology, filter))


@_cfndoc
def topology_set_io_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_io_types_filter(topology, filter))


# void 	hwloc_topology_set_userdata (hwloc_topology_t topology, const void *userdata)

# void * 	hwloc_topology_get_userdata (hwloc_topology_t topology)

#############
# CPU binding
#############

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00146.php


@_cenumdoc
class hwloc_cpubind_flags_t(IntEnum):
    HWLOC_CPUBIND_PROCESS = 1 << 0
    HWLOC_CPUBIND_THREAD = 1 << 1
    HWLOC_CPUBIND_STRICT = 1 << 2
    HWLOC_CPUBIND_NOMEMBIND = 1 << 3


_LIB.hwloc_set_cpubind.argtypes = [topology_t, hwloc_const_cpuset_t, ctypes.c_int]
_LIB.hwloc_set_cpubind.restype = ctypes.c_int


@_cfndoc
def set_cpubind(topology: topology_t, cpuset: hwloc_const_cpuset_t, flags: int) -> None:
    _checkc(_LIB.hwloc_set_cpubind(topology, cpuset, flags))


_LIB.hwloc_get_cpubind.argtypes = [topology_t, hwloc_cpuset_t, ctypes.c_int]
_LIB.hwloc_get_cpubind.restype = ctypes.c_int


@_cfndoc
def get_cpubind(topology: topology_t, cpuset: hwloc_cpuset_t, flags: int) -> None:
    _checkc(_LIB.hwloc_get_cpubind(topology, cpuset, flags))


_LIB.hwloc_set_proc_cpubind.argtypes = [
    topology_t,
    hwloc_pid_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
]
_LIB.hwloc_set_proc_cpubind.restype = ctypes.c_int


@_cfndoc
def set_proc_cpubind(
    topology: topology_t, pid: hwloc_pid_t, cpuset: hwloc_const_cpuset_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_set_proc_cpubind(topology, pid, cpuset, flags))


_LIB.hwloc_get_proc_cpubind.argtypes = [
    topology_t,
    hwloc_pid_t,
    hwloc_cpuset_t,
    ctypes.c_int,
]
_LIB.hwloc_get_proc_cpubind.restype = ctypes.c_int


@_cfndoc
def get_proc_cpubind(
    topology: topology_t, pid: hwloc_pid_t, cpuset: hwloc_cpuset_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_get_proc_cpubind(topology, pid, cpuset, flags))


hwloc_thread_t = ctypes.c_ulong

_LIB.hwloc_set_thread_cpubind.argtypes = [
    topology_t,
    hwloc_thread_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
]
_LIB.hwloc_set_thread_cpubind.restype = ctypes.c_int


@_cfndoc
def set_thread_cpubind(
    topology: topology_t,
    thread: hwloc_thread_t,
    cpuset: hwloc_const_cpuset_t,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_set_thread_cpubind(topology, thread, cpuset, flags))


_LIB.hwloc_get_thread_cpubind.argtypes = [
    topology_t,
    hwloc_thread_t,
    hwloc_cpuset_t,
    ctypes.c_int,
]
_LIB.hwloc_get_thread_cpubind.restype = ctypes.c_int


@_cfndoc
def get_thread_cpubind(
    topology: topology_t, thread: hwloc_thread_t, cpuset: hwloc_cpuset_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_get_thread_cpubind(topology, thread, cpuset, flags))


_LIB.hwloc_get_last_cpu_location.argtypes = [topology_t, hwloc_cpuset_t, ctypes.c_int]
_LIB.hwloc_get_last_cpu_location.restype = ctypes.c_int


@_cfndoc
def get_last_cpu_location(
    topology: topology_t, cpuset: hwloc_cpuset_t, flags: int
) -> None:

    _checkc(_LIB.hwloc_get_last_cpu_location(topology, cpuset, flags))


_LIB.hwloc_get_proc_last_cpu_location.argtypes = [
    topology_t,
    hwloc_pid_t,
    hwloc_cpuset_t,
    ctypes.c_int,
]
_LIB.hwloc_get_proc_last_cpu_location.restype = ctypes.c_int


@_cfndoc
def get_proc_last_cpu_location(
    topology: topology_t, pid: hwloc_pid_t, cpuset: hwloc_cpuset_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_get_proc_last_cpu_location(topology, pid, cpuset, flags))


################
# Memory binding
################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00147.php#gadf87089ef533db40460ccc24b5bc0d65


@_cenumdoc
class hwloc_membind_policy_t(IntEnum):
    HWLOC_MEMBIND_DEFAULT = 0
    HWLOC_MEMBIND_FIRSTTOUCH = 1
    HWLOC_MEMBIND_BIND = 2
    HWLOC_MEMBIND_INTERLEAVE = 3
    HWLOC_MEMBIND_WEIGHTED_INTERLEAVE = 5
    HWLOC_MEMBIND_NEXTTOUCH = 4
    HWLOC_MEMBIND_MIXED = -1


@_cenumdoc
class hwloc_membind_flags_t(IntEnum):
    HWLOC_MEMBIND_PROCESS = 1 << 0
    HWLOC_MEMBIND_THREAD = 1 << 1
    HWLOC_MEMBIND_STRICT = 1 << 2
    HWLOC_MEMBIND_MIGRATE = 1 << 3
    HWLOC_MEMBIND_NOCPUBIND = 1 << 4
    HWLOC_MEMBIND_BYNODESET = 1 << 5


_LIB.hwloc_set_membind.argtypes = [
    topology_t,
    const_bitmap_t,
    ctypes.c_int,
    ctypes.c_int,
]
_LIB.hwloc_set_membind.restype = ctypes.c_int


@_cfndoc
def set_membind(
    topology: topology_t,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_set_membind(topology, set, policy, flags))


_LIB.hwloc_get_membind.argtypes = [
    topology_t,
    bitmap_t,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
]
_LIB.hwloc_get_membind.restype = ctypes.c_int


@_cfndoc
def get_membind(
    topology: topology_t, set: bitmap_t, flags: int
) -> hwloc_membind_policy_t:
    policy = ctypes.c_int()
    _checkc(_LIB.hwloc_get_membind(topology, set, ctypes.byref(policy), flags))
    return hwloc_membind_policy_t(policy.value)


_LIB.hwloc_set_proc_membind.argtypes = [
    topology_t,
    hwloc_pid_t,
    const_bitmap_t,
    ctypes.c_int,
    ctypes.c_int,
]
_LIB.hwloc_set_proc_membind.restype = ctypes.c_int


@_cfndoc
def set_proc_membind(
    topology: topology_t,
    pid: hwloc_pid_t,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_set_proc_membind(topology, pid, set, policy, flags))


_LIB.hwloc_get_proc_membind.argtypes = [
    topology_t,
    hwloc_pid_t,
    bitmap_t,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
]
_LIB.hwloc_get_proc_membind.restype = ctypes.c_int


@_cfndoc
def get_proc_membind(
    topology: topology_t, pid: hwloc_pid_t, set: bitmap_t, flags: int
) -> hwloc_membind_policy_t:
    policy = ctypes.c_int()
    _checkc(
        _LIB.hwloc_get_proc_membind(topology, pid, set, ctypes.byref(policy), flags)
    )
    return hwloc_membind_policy_t(policy.value)


_LIB.hwloc_set_area_membind.argtypes = [
    topology_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
    const_bitmap_t,
    ctypes.c_int,
    ctypes.c_int,
]
_LIB.hwloc_set_area_membind.restype = ctypes.c_int


@_cfndoc
def set_area_membind(
    topology: topology_t,
    addr: ctypes.c_void_p,
    length: int,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_set_area_membind(topology, addr, length, set, policy, flags))


_LIB.hwloc_get_area_membind.argtypes = [
    topology_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
    bitmap_t,
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
]
_LIB.hwloc_get_area_membind.restype = ctypes.c_int


@_cfndoc
def get_area_membind(
    topology: topology_t, addr: ctypes.c_void_p, length: int, set: bitmap_t, flags: int
) -> hwloc_membind_policy_t:
    policy = ctypes.c_int()
    _checkc(
        _LIB.hwloc_get_area_membind(
            topology, addr, length, set, ctypes.byref(policy), flags
        )
    )
    return hwloc_membind_policy_t(policy.value)


_LIB.hwloc_get_area_memlocation.argtypes = [
    topology_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
    bitmap_t,
    ctypes.c_int,
]
_LIB.hwloc_get_area_memlocation.restype = ctypes.c_int


@_cfndoc
def get_area_memlocation(
    topology: topology_t, addr: ctypes.c_void_p, length: int, set: bitmap_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_get_area_memlocation(topology, addr, length, set, flags))


_LIB.hwloc_alloc.argtypes = [topology_t, ctypes.c_size_t]
_LIB.hwloc_alloc.restype = ctypes.c_void_p


@_cfndoc
def alloc(topology: topology_t, length: int) -> ctypes.c_void_p:
    result = _LIB.hwloc_alloc(topology, length)
    if not result:
        raise HwLocError(-1, 0, b"hwloc_alloc failed")
    return result


_LIB.hwloc_alloc_membind.argtypes = [
    topology_t,
    ctypes.c_size_t,
    const_bitmap_t,
    ctypes.c_int,
    ctypes.c_int,
]
_LIB.hwloc_alloc_membind.restype = ctypes.c_void_p


@_cfndoc
def alloc_membind(
    topology: topology_t,
    length: int,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> ctypes.c_void_p:
    result = _LIB.hwloc_alloc_membind(topology, length, set, policy, flags)
    if not result:
        raise HwLocError(-1, 0, b"hwloc_alloc_membind failed")
    return result


_pyhwloc_lib.pyhwloc_alloc_membind_policy.argtypes = [
    topology_t,
    ctypes.c_size_t,
    const_bitmap_t,
    ctypes.c_int,
    ctypes.c_int,
]
_pyhwloc_lib.pyhwloc_alloc_membind_policy.restype = ctypes.c_void_p


@_cfndoc
def alloc_membind_policy(
    topology: topology_t,
    length: int,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> ctypes.c_void_p:
    result = _pyhwloc_lib.pyhwloc_alloc_membind_policy(
        topology, length, set, policy, flags
    )
    if not result:
        raise HwLocError(-1, 0, b"hwloc_alloc_membind_policy failed")
    return result


_LIB.hwloc_free.argtypes = [topology_t, ctypes.c_void_p, ctypes.c_size_t]
_LIB.hwloc_free.restype = ctypes.c_int


@_cfndoc
def free(topology: topology_t, addr: ctypes.c_void_p, length: int) -> None:
    _checkc(_LIB.hwloc_free(topology, addr, length))


######################
# Kinds of object Type
######################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00151.php


_LIB.hwloc_obj_type_is_normal.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_is_normal.restype = ctypes.c_int


@_cfndoc
def obj_type_is_normal(obj_type: hwloc_obj_type_t) -> bool:
    # For the definition of normal:
    # https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00343.php
    return bool(_LIB.hwloc_obj_type_is_normal(int(obj_type)))


_LIB.hwloc_obj_type_is_io.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_is_io.restype = ctypes.c_int


@_cfndoc
def obj_type_is_io(obj_type: hwloc_obj_type_t) -> bool:
    return bool(_LIB.hwloc_obj_type_is_io(obj_type))


_LIB.hwloc_obj_type_is_memory.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_is_memory.restype = ctypes.c_int


@_cfndoc
def obj_type_is_memory(obj_type: hwloc_obj_type_t) -> bool:
    return bool(_LIB.hwloc_obj_type_is_memory(obj_type))


_LIB.hwloc_obj_type_is_cache.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_is_cache.restype = ctypes.c_int


@_cfndoc
def obj_type_is_cache(obj_type: hwloc_obj_type_t) -> bool:
    return bool(_LIB.hwloc_obj_type_is_cache(obj_type))


_LIB.hwloc_obj_type_is_dcache.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_is_dcache.restype = ctypes.c_int


@_cfndoc
def obj_type_is_dcache(obj_type: hwloc_obj_type_t) -> bool:
    return bool(_LIB.hwloc_obj_type_is_dcache(obj_type))


_LIB.hwloc_obj_type_is_icache.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_is_icache.restype = ctypes.c_int


@_cfndoc
def obj_type_is_icache(obj_type: hwloc_obj_type_t) -> bool:
    return bool(_LIB.hwloc_obj_type_is_icache(obj_type))


####################
# Kinds of CPU cores
####################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00170.php

_LIB.hwloc_cpukinds_get_nr.argtypes = [topology_t, ctypes.c_ulong]
_LIB.hwloc_cpukinds_get_nr.restype = ctypes.c_int


@_cfndoc
def cpukinds_get_nr(topology: topology_t, flags: int) -> int:
    result = _LIB.hwloc_cpukinds_get_nr(topology, flags)
    if result < 0:
        _checkc(result)
    return result


_LIB.hwloc_cpukinds_get_by_cpuset.argtypes = [
    topology_t,
    hwloc_const_bitmap_t,
    ctypes.c_ulong,
]
_LIB.hwloc_cpukinds_get_by_cpuset.restype = ctypes.c_int


@_cfndoc
def cpukinds_get_by_cpuset(
    topology: topology_t, cpuset: hwloc_const_bitmap_t, flags: int
) -> int:
    result = _LIB.hwloc_cpukinds_get_by_cpuset(topology, cpuset, flags)
    if result < 0:
        _checkc(result)
    return result


_LIB.hwloc_cpukinds_get_info.argtypes = [
    topology_t,
    ctypes.c_uint,
    hwloc_bitmap_t,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.POINTER(hwloc_infos_s)),
    ctypes.c_ulong,
]
_LIB.hwloc_cpukinds_get_info.restype = ctypes.c_int


@_cfndoc
def cpukinds_get_info(
    topology: topology_t, kind_index: int, flags: int
) -> tuple[hwloc_bitmap_t, int, InfosPtr]:
    cpuset = bitmap_alloc()
    efficiency = ctypes.c_int()
    infos_ptr = ctypes.POINTER(hwloc_infos_s)()
    # flags must be 0 for now.
    _checkc(
        _LIB.hwloc_cpukinds_get_info(
            topology,
            kind_index,
            cpuset,
            ctypes.byref(efficiency),
            ctypes.byref(infos_ptr),
            flags,
        )
    )

    return cpuset, efficiency.value, infos_ptr


_LIB.hwloc_cpukinds_register.argtypes = [
    topology_t,
    hwloc_bitmap_t,
    ctypes.c_int,
    ctypes.POINTER(hwloc_infos_s),
    ctypes.c_ulong,
]
_LIB.hwloc_cpukinds_register.restype = ctypes.c_int


@_cfndoc
def cpukinds_register(
    topology: topology_t,
    cpuset: hwloc_bitmap_t,
    forced_efficiency: int,
    infos: hwloc_infos_s | None,
) -> None:
    pinfos = ctypes.byref(infos) if infos is not None else None
    # The parameter flags must be 0 for now.
    _checkc(
        _LIB.hwloc_cpukinds_register(topology, cpuset, forced_efficiency, pinfos, 0)
    )


######
# misc
######


@_cfndoc
def get_type_or_below_depth(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _pyhwloc_lib.pyhwloc_get_type_or_below_depth(topology, obj_type)


_LIB.hwloc_topology_get_infos.argtypes = [topology_t]
_LIB.hwloc_topology_get_infos.restype = ctypes.POINTER(hwloc_infos_s)


@_cfndoc
def topology_get_infos(topology: topology_t) -> InfosPtr:
    infos = _LIB.hwloc_topology_get_infos(topology)
    return infos
