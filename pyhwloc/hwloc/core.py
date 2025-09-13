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
"""
Core API
========
"""
from __future__ import annotations

import ctypes
import sys
from enum import IntEnum
from typing import TYPE_CHECKING, Callable

from .bitmap import bitmap_alloc, bitmap_t, const_bitmap_t
from .lib import (
    _LIB,
    _cenumdoc,
    _cfndoc,
    _checkc,
    _cstructdoc,
    _cuniondoc,
    _hwloc_error,
    _pyhwloc_lib,
)

hwloc_uint64_t = ctypes.c_uint64
hwloc_pid_t = ctypes.c_int

HWLOC_UNKNOWN_INDEX = ctypes.c_uint(-1).value


#############
# API version
#############

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00138.php


_LIB.hwloc_get_api_version.restype = ctypes.c_uint


@_cfndoc
def get_api_version() -> int:
    return int(_LIB.hwloc_get_api_version())


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
class hwloc_obj_cache_type_e(IntEnum):
    HWLOC_OBJ_CACHE_UNIFIED = 0
    HWLOC_OBJ_CACHE_DATA = 1
    HWLOC_OBJ_CACHE_INSTRUCTION = 2


# typedef in hwloc.h
hwloc_obj_cache_type_t = hwloc_obj_cache_type_e


@_cenumdoc
class hwloc_obj_bridge_type_e(IntEnum):
    HWLOC_OBJ_BRIDGE_HOST = 0
    HWLOC_OBJ_BRIDGE_PCI = 1


# typedef in hwloc.h
hwloc_obj_bridge_type_t = hwloc_obj_bridge_type_e


@_cenumdoc
class hwloc_obj_osdev_type_e(IntEnum):
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


@_cstructdoc()
class hwloc_info_s(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),  # Info name
        ("value", ctypes.c_char_p),  # Info value
    ]


@_cstructdoc()
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


@_cstructdoc(parent="hwloc_obj_attr_u")
class hwloc_memory_page_type_s(ctypes.Structure):
    _fields_ = [
        ("size", hwloc_uint64_t),  # Size of pages
        ("count", hwloc_uint64_t),  # Number of pages of this size
    ]


@_cstructdoc(parent="hwloc_obj_attr_u")
class hwloc_numanode_attr_s(ctypes.Structure):
    """See :c:struct:`hwloc_obj_attr_u.hwloc_numanode_attr_s`"""

    _fields_ = [
        ("local_memory", hwloc_uint64_t),  # Local memory (in bytes)
        ("page_types_len", ctypes.c_uint),  # Size of array page_types
        (
            "page_types",
            ctypes.POINTER(hwloc_memory_page_type_s),
        ),  # Array of local memory page types
    ]


@_cstructdoc("hwloc_obj_attr_u")
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


@_cstructdoc("hwloc_obj_attr_u")
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


@_cstructdoc("hwloc_obj_attr_u")
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


@_cuniondoc("hwloc_obj_attr_u.hwloc_bridge_attr_s")
class hwloc_bridge_upstream_u(ctypes.Union):
    _fields_ = [
        (
            "pci",
            hwloc_pcidev_attr_s,
        ),  # PCI attribute of the upstream part as a PCI device
    ]


@_cstructdoc("hwloc_obj_attr_u.hwloc_bridge_downstream_u")
class hwloc_bridge_downstream_pci_s(ctypes.Structure):
    _fields_ = [
        ("domain", ctypes.c_uint),  # Domain number the downstream PCI buses
        ("secondary_bus", ctypes.c_ubyte),  # First PCI bus number below the bridge
        ("subordinate_bus", ctypes.c_ubyte),  # Highest PCI bus number below the bridge
    ]


@_cuniondoc("hwloc_obj_attr_u")
class hwloc_bridge_downstream_u(ctypes.Union):
    _fields_ = [
        ("pci", hwloc_bridge_downstream_pci_s),
    ]


@_cstructdoc("hwloc_obj_attr_u")
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


# OR'ed set of ::hwloc_obj_osdev_type_e.
hwloc_obj_osdev_types_t = ctypes.c_ulong


@_cstructdoc("hwloc_obj_attr_u")
class hwloc_osdev_attr_s(ctypes.Structure):
    _fields_ = [
        (
            "types",
            hwloc_obj_osdev_types_t,
        ),  # hwloc_obj_osdev_types_t - OR'ed set of at least one hwloc_obj_osdev_type_e
    ]


# Main attribute union
@_cuniondoc()
class hwloc_obj_attr_u(ctypes.Union):
    _fields_ = [
        ("numanode", hwloc_numanode_attr_s),  # NUMA node-specific Object Attributes
        ("cache", hwloc_cache_attr_s),  # Cache-specific Object Attributes
        ("group", hwloc_group_attr_s),  # Group-specific Object Attributes
        ("pcidev", hwloc_pcidev_attr_s),  # PCI Device specific Object Attributes
        ("bridge", hwloc_bridge_attr_s),  # Bridge specific Object Attributes
        ("osdev", hwloc_osdev_attr_s),  # OS Device specific Object Attributes
    ]


@_cstructdoc()
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
    ObjPtr = ctypes._Pointer[hwloc_obj]
else:
    ObjPtr = ctypes._Pointer


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


_LIB.hwloc_topology_get_depth.argtypes = [topology_t]
_LIB.hwloc_topology_get_depth.restype = ctypes.c_int


@_cfndoc
def topology_get_depth(topology: topology_t) -> int:
    return _LIB.hwloc_topology_get_depth(topology)


_LIB.hwloc_get_type_depth.argtypes = [topology_t, ctypes.c_int]
_LIB.hwloc_get_type_depth.restype = ctypes.c_int


@_cfndoc
def get_type_depth(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _LIB.hwloc_get_type_depth(topology, obj_type)


_LIB.hwloc_get_type_depth_with_attr.argtypes = [
    topology_t,
    ctypes.c_int,  # hwloc_obj_type_t
    ctypes.POINTER(hwloc_obj_attr_u),
    ctypes.c_size_t,
]
_LIB.hwloc_get_type_depth_with_attr.restype = ctypes.c_int


@_cfndoc
def get_type_depth_with_attr(
    topology: topology_t,
    obj_type: hwloc_obj_type_t,
    attr: ctypes._Pointer,  # [hwloc_obj_attr_u]
    attrsize: int,
) -> int:
    return _LIB.hwloc_get_type_depth_with_attr(topology, obj_type, attr, attrsize)


_LIB.hwloc_get_memory_parents_depth.argtypes = [topology_t]
_LIB.hwloc_get_memory_parents_depth.restype = ctypes.c_int


@_cfndoc
def get_memory_parents_depth(topology: topology_t) -> int:
    return _LIB.hwloc_get_memory_parents_depth(topology)


_pyhwloc_lib.pyhwloc_get_type_or_above_depth.argtypes = [topology_t, ctypes.c_int]
_pyhwloc_lib.pyhwloc_get_type_or_above_depth.restype = ctypes.c_int


@_cfndoc
def get_type_or_below_depth(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _pyhwloc_lib.pyhwloc_get_type_or_below_depth(topology, obj_type)


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
def get_root_obj(topology: topology_t) -> ObjPtr:
    # This function cannot return NULL.
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
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_obj_by_type(topology, obj_type, idx)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_obj_by_depth.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(hwloc_obj),
]
_pyhwloc_lib.pyhwloc_get_next_obj_by_depth.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_obj_by_depth(
    topology: topology_t, depth: int, prev: ObjPtr | None
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_obj_by_depth(topology, depth, prev)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_obj_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(hwloc_obj),
]
_pyhwloc_lib.pyhwloc_get_next_obj_by_type.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_obj_by_type(
    topology: topology_t, obj_type: hwloc_obj_type_t, prev: ObjPtr | None
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_obj_by_type(topology, obj_type, prev)
    if not obj:
        return None
    return obj


@_cfndoc
def get_nbobjs_by_depth(topology: topology_t, depth: int) -> int:
    return _LIB.hwloc_get_nbobjs_by_depth(topology, depth)


_LIB.hwloc_get_obj_by_depth.argtypes = [topology_t, ctypes.c_int, ctypes.c_uint]
_LIB.hwloc_get_obj_by_depth.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_obj_by_depth(topology: topology_t, depth: int, idx: int) -> ObjPtr | None:
    obj = _LIB.hwloc_get_obj_by_depth(topology, depth, idx)
    if not obj:
        return None
    return obj


#############################################################
# Converting between Object Types and Attributes, and Strings
#############################################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00144.php

_LIB.hwloc_obj_type_string.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_string.restype = ctypes.c_char_p


@_cfndoc
def hwloc_obj_type_string(obj_type: hwloc_obj_type_t) -> bytes:
    return _LIB.hwloc_obj_type_string(obj_type).value


class hwloc_obj_snprintf_flag_e(IntEnum):
    HWLOC_OBJ_SNPRINTF_FLAG_OLD_VERBOSE = 1 << 0
    HWLOC_OBJ_SNPRINTF_FLAG_LONG_NAMES = 1 << 1
    HWLOC_OBJ_SNPRINTF_FLAG_SHORT_NAMES = 1 << 2
    HWLOC_OBJ_SNPRINTF_FLAG_MORE_ATTRS = 1 << 3
    HWLOC_OBJ_SNPRINTF_FLAG_NO_UNITS = 1 << 4
    HWLOC_OBJ_SNPRINTF_FLAG_UNITS_1000 = 1 << 5


_LIB.hwloc_obj_type_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    obj_t,
    ctypes.c_ulong,
]
_LIB.hwloc_obj_type_snprintf.restype = ctypes.c_int


@_cfndoc
def obj_type_snprintf(
    string: ctypes.c_char_p | ctypes.Array, size: int, obj: ObjPtr, flags: int
) -> int:
    # flags are hwloc_obj_snprintf_flag_e
    return _LIB.hwloc_obj_type_snprintf(string, size, obj, int(flags))


_LIB.hwloc_obj_attr_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    obj_t,
    ctypes.c_char_p,
    ctypes.c_ulong,
]
_LIB.hwloc_obj_attr_snprintf.restype = ctypes.c_int


@_cfndoc
def obj_attr_snprintf(
    string: ctypes.c_char_p | ctypes.Array,
    size: int,
    obj: ObjPtr,
    separator: ctypes.c_char_p | bytes,
    flags: int,
) -> int:
    # flags are hwloc_obj_snprintf_flag_e
    return _LIB.hwloc_obj_attr_snprintf(string, size, obj, separator, int(flags))


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
def obj_get_info_by_name(obj: ObjPtr, name: str) -> str | None:
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
def obj_add_info(obj: ObjPtr, name: str, value: str) -> None:
    if not name or not value:
        raise ValueError("name and value must be non-empty strings")

    name_bytes = name.encode("utf-8")
    value_bytes = value.encode("utf-8")
    _checkc(_pyhwloc_lib.pyhwloc_obj_add_info(obj, name_bytes, value_bytes))


_LIB.hwloc_obj_set_subtype.argtypes = [topology_t, obj_t, ctypes.c_char_p]
_LIB.hwloc_obj_set_subtype.restype = ctypes.c_int


@_cfndoc
def obj_set_subtype(topology: topology_t, obj: ObjPtr, subtype: str) -> None:
    subtype_bytes = subtype.encode("utf-8")
    _checkc(_LIB.hwloc_obj_set_subtype(topology, obj, subtype_bytes))


_LIB.hwloc_topology_get_infos.argtypes = [topology_t]
_LIB.hwloc_topology_get_infos.restype = ctypes.POINTER(hwloc_infos_s)


@_cfndoc
def topology_get_infos(topology: topology_t) -> InfosPtr:
    infos = _LIB.hwloc_topology_get_infos(topology)
    return infos


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


if sys.platform == "win32":
    hwloc_thread_t = ctypes.c_void_p

    ctypes.windll.kernel32.OpenThread.restype = hwloc_thread_t
    ctypes.windll.kernel32.OpenThread.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]

    def _open_thread_handle(thread_id: int, read_only: bool = True) -> hwloc_thread_t:
        THREAD_SET_INFORMATION = 0x0020
        THREAD_QUERY_INFORMATION = 0x0040
        if read_only:
            access = THREAD_QUERY_INFORMATION
        else:
            access = THREAD_QUERY_INFORMATION | THREAD_SET_INFORMATION
        hdl = ctypes.windll.kernel32.OpenThread(access, 0, thread_id)
        if not hdl:
            raise ctypes.WinError()
        return hdl

    ctypes.windll.kernel32.CloseHandle.argtypes = [hwloc_thread_t]
    ctypes.windll.kernel32.CloseHandle.restype = ctypes.c_int

    def _close_thread_handle(thread_hdl: hwloc_thread_t) -> None:
        status = ctypes.windll.kernel32.CloseHandle(thread_hdl)
        if status == 0:
            raise ctypes.WinError()

else:
    hwloc_thread_t = ctypes.c_ulong

    def _open_thread_handle(thread_id: int, read_only: bool = True) -> hwloc_thread_t:
        return hwloc_thread_t(thread_id)

    def _close_thread_handle(thread_hdl: hwloc_thread_t) -> None:
        pass


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
    pid: int,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_set_proc_membind(topology, hwloc_pid_t(pid), set, policy, flags))


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
    topology: topology_t, pid: int, set: bitmap_t, flags: int
) -> hwloc_membind_policy_t:
    # Note that it does not make sense to pass ::HWLOC_MEMBIND_THREAD to this function.
    policy = ctypes.c_int()
    _checkc(
        _LIB.hwloc_get_proc_membind(
            topology, hwloc_pid_t(pid), set, ctypes.byref(policy), flags
        )
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
        raise _hwloc_error("hwloc_alloc")
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
        raise _hwloc_error("hwloc_alloc_membind")
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
        raise _hwloc_error("hwloc_alloc_membind_policy")
    return result


_LIB.hwloc_free.argtypes = [topology_t, ctypes.c_void_p, ctypes.c_size_t]
_LIB.hwloc_free.restype = ctypes.c_int


@_cfndoc
def free(topology: topology_t, addr: ctypes.c_void_p, length: int) -> None:
    _checkc(_LIB.hwloc_free(topology, addr, length))


###########################################
# Changing the Source of Topology Discovery
###########################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00148.php


class hwloc_topology_components_flag_e(IntEnum):
    HWLOC_TOPOLOGY_COMPONENTS_FLAG_BLACKLIST = 1 << 0


_LIB.hwloc_topology_set_pid.argtypes = [topology_t, hwloc_pid_t]
_LIB.hwloc_topology_set_pid.restype = ctypes.c_int


@_cfndoc
def topology_set_pid(topology: topology_t, pid: int) -> None:
    _checkc(_LIB.hwloc_topology_set_pid(topology, hwloc_pid_t(pid)))


_LIB.hwloc_topology_set_synthetic.argtypes = [topology_t, ctypes.c_char_p]
_LIB.hwloc_topology_set_synthetic.restype = ctypes.c_int


@_cfndoc
def topology_set_synthetic(topology: topology_t, description: str) -> None:
    description_bytes = description.encode("utf-8")
    _checkc(_LIB.hwloc_topology_set_synthetic(topology, description_bytes))


_LIB.hwloc_topology_set_xml.argtypes = [topology_t, ctypes.c_char_p]
_LIB.hwloc_topology_set_xml.restype = ctypes.c_int


@_cfndoc
def topology_set_xml(topology: topology_t, xmlpath: str) -> None:
    xmlpath_bytes = xmlpath.encode("utf-8")
    _checkc(_LIB.hwloc_topology_set_xml(topology, xmlpath_bytes))


_LIB.hwloc_topology_set_xmlbuffer.argtypes = [topology_t, ctypes.c_char_p, ctypes.c_int]
_LIB.hwloc_topology_set_xmlbuffer.restype = ctypes.c_int


@_cfndoc
def topology_set_xmlbuffer(topology: topology_t, buf: str) -> None:
    buffer_bytes = buf.encode("utf-8")
    _checkc(
        _LIB.hwloc_topology_set_xmlbuffer(topology, buffer_bytes, len(buffer_bytes))
    )


_LIB.hwloc_topology_set_components.argtypes = [
    topology_t,
    ctypes.c_ulong,
    ctypes.c_char_p,
]
_LIB.hwloc_topology_set_components.restype = ctypes.c_int


@_cfndoc
def topology_set_components(topology: topology_t, flags: int, name: str) -> None:
    name_bytes = name.encode("utf-8")
    _checkc(_LIB.hwloc_topology_set_components(topology, flags, name_bytes))


############################################
# Topology Detection Configuration and Query
############################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00149.php


@_cstructdoc()
class hwloc_topology_discovery_support(ctypes.Structure):
    _fields_ = [
        ("pu", ctypes.c_ubyte),
        ("numa", ctypes.c_ubyte),
        ("numa_memory", ctypes.c_ubyte),
        ("disallowed_pu", ctypes.c_ubyte),
        ("disallowed_numa", ctypes.c_ubyte),
        ("cpukind_efficiency", ctypes.c_ubyte),
    ]


@_cstructdoc()
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


@_cstructdoc()
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


@_cstructdoc()
class hwloc_topology_misc_support(ctypes.Structure):
    _fields_ = [
        ("imported_support", ctypes.c_ubyte),
    ]


@_cstructdoc()
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
    topology: topology_t, obj_type: hwloc_obj_type_t, f: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_type_filter(topology, obj_type, f))


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
    f = ctypes.c_int()
    _checkc(_LIB.hwloc_topology_get_type_filter(topology, obj_type, ctypes.byref(f)))
    return hwloc_type_filter_e(f.value)


@_cfndoc
def topology_set_all_types_filter(topology: topology_t, f: hwloc_type_filter_e) -> None:
    _checkc(_LIB.hwloc_topology_set_all_types_filter(topology, f))


@_cfndoc
def topology_set_cache_types_filter(
    topology: topology_t, f: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_cache_types_filter(topology, f))


@_cfndoc
def topology_set_icache_types_filter(
    topology: topology_t, f: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_icache_types_filter(topology, f))


@_cfndoc
def topology_set_io_types_filter(topology: topology_t, f: hwloc_type_filter_e) -> None:
    _checkc(_LIB.hwloc_topology_set_io_types_filter(topology, f))


_LIB.hwloc_topology_set_userdata.argtypes = [topology_t, ctypes.c_void_p]
_LIB.hwloc_topology_set_userdata.restype = None


@_cfndoc
def topology_set_userdata(topology: topology_t, userdata: int) -> None:
    _LIB.hwloc_topology_set_userdata(topology, userdata)


_LIB.hwloc_topology_get_userdata.argtypes = [topology_t]
_LIB.hwloc_topology_get_userdata.restype = ctypes.c_void_p


@_cfndoc
def topology_get_userdata(topology: topology_t) -> int:
    return _LIB.hwloc_topology_get_userdata(topology)


#############################
# Modifying a loaded Topology
#############################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00150.php


@_cenumdoc
class hwloc_restrict_flags_e(IntEnum):
    HWLOC_RESTRICT_FLAG_REMOVE_CPULESS = 1 << 0
    HWLOC_RESTRICT_FLAG_ADAPT_MISC = 1 << 1
    HWLOC_RESTRICT_FLAG_ADAPT_IO = 1 << 2
    HWLOC_RESTRICT_FLAG_BYNODESET = 1 << 3
    HWLOC_RESTRICT_FLAG_REMOVE_MEMLESS = 1 << 4


@_cenumdoc
class hwloc_allow_flags_e(IntEnum):
    HWLOC_ALLOW_FLAG_ALL = 1 << 0
    HWLOC_ALLOW_FLAG_LOCAL_RESTRICTIONS = 1 << 1
    HWLOC_ALLOW_FLAG_CUSTOM = 1 << 2


_LIB.hwloc_topology_restrict.argtypes = [
    topology_t,
    const_bitmap_t,
    ctypes.c_ulong,
]
_LIB.hwloc_topology_restrict.restype = ctypes.c_int


@_cfndoc
def topology_restrict(topology: topology_t, cpuset: const_bitmap_t, flags: int) -> None:
    _checkc(_LIB.hwloc_topology_restrict(topology, cpuset, flags))


_LIB.hwloc_topology_allow.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    hwloc_const_nodeset_t,
    ctypes.c_ulong,
]
_LIB.hwloc_topology_allow.restype = ctypes.c_int


@_cfndoc
def topology_allow(
    topology: topology_t,
    cpuset: hwloc_const_cpuset_t,
    nodeset: hwloc_const_nodeset_t,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_topology_allow(topology, cpuset, nodeset, flags))


_LIB.hwloc_topology_insert_misc_object.argtypes = [topology_t, obj_t, ctypes.c_char_p]
_LIB.hwloc_topology_insert_misc_object.restype = obj_t


@_cfndoc
def topology_insert_misc_object(
    topology: topology_t, parent: ObjPtr, name: str
) -> ObjPtr | None:
    name_bytes = name.encode("utf-8")
    obj = _LIB.hwloc_topology_insert_misc_object(topology, parent, name_bytes)
    # fixme: null return can be caused by error and filter, how do we know which one is
    # the case?
    if not obj:
        return None
    return obj


_LIB.hwloc_topology_alloc_group_object.argtypes = [topology_t]
_LIB.hwloc_topology_alloc_group_object.restype = obj_t


@_cfndoc
def topology_alloc_group_object(topology: topology_t) -> ObjPtr:
    obj = _LIB.hwloc_topology_alloc_group_object(topology)
    if not obj:
        raise _hwloc_error("hwloc_topology_alloc_group_object")
    return obj


_LIB.hwloc_topology_free_group_object.argtypes = [topology_t, obj_t]
_LIB.hwloc_topology_free_group_object.restype = ctypes.c_int


@_cfndoc
def topology_free_group_object(topology: topology_t, group: ObjPtr) -> None:
    _checkc(_LIB.hwloc_topology_free_group_object(topology, group))


_LIB.hwloc_topology_insert_group_object.argtypes = [topology_t, obj_t]
_LIB.hwloc_topology_insert_group_object.restype = obj_t


@_cfndoc
def topology_insert_group_object(topology: topology_t, group: ObjPtr) -> ObjPtr | None:
    # fixme: null return can be caused by error and filter, how do we know which one is
    # the case?
    obj = _LIB.hwloc_topology_insert_group_object(topology, group)
    if not obj:
        return None
    return obj


_LIB.hwloc_obj_add_other_obj_sets.argtypes = [obj_t, obj_t]
_LIB.hwloc_obj_add_other_obj_sets.restype = ctypes.c_int


@_cfndoc
def obj_add_other_obj_sets(dst: ObjPtr, src: ObjPtr) -> None:
    _checkc(_LIB.hwloc_obj_add_other_obj_sets(dst, src))


_LIB.hwloc_topology_refresh.argtypes = [topology_t]
_LIB.hwloc_topology_refresh.restype = ctypes.c_int


@_cfndoc
def topology_refresh(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_refresh(topology))


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


##################################
# Finding Objects inside a CPU set
##################################

_pyhwloc_lib.pyhwloc_get_first_largest_obj_inside_cpuset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
]
_pyhwloc_lib.pyhwloc_get_first_largest_obj_inside_cpuset.restype = obj_t


@_cfndoc
def get_first_largest_obj_inside_cpuset(
    topology: topology_t, cpuset: hwloc_const_cpuset_t
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_first_largest_obj_inside_cpuset(topology, cpuset)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_largest_objs_inside_cpuset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.POINTER(obj_t),
    ctypes.c_int,
]
_pyhwloc_lib.pyhwloc_get_largest_objs_inside_cpuset.restype = ctypes.c_int


@_cfndoc
def get_largest_objs_inside_cpuset(
    topology: topology_t,
    cpuset: hwloc_const_cpuset_t,
    objs: ctypes.Array,
    max_objs: int,
) -> int:
    return _pyhwloc_lib.pyhwloc_get_largest_objs_inside_cpuset(
        topology, cpuset, objs, max_objs
    )


_pyhwloc_lib.pyhwloc_get_next_obj_inside_cpuset_by_depth.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_next_obj_inside_cpuset_by_depth.restype = obj_t


@_cfndoc
def get_next_obj_inside_cpuset_by_depth(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, depth: int, prev: ObjPtr
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_obj_inside_cpuset_by_depth(
        topology, cpuset, depth, prev
    )
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_obj_inside_cpuset_by_type.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_next_obj_inside_cpuset_by_type.restype = obj_t


@_cfndoc
def get_next_obj_inside_cpuset_by_type(
    topology: topology_t,
    cpuset: hwloc_const_cpuset_t,
    obj_type: hwloc_obj_type_t,
    prev: ObjPtr,
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_obj_inside_cpuset_by_type(
        topology, cpuset, obj_type, prev
    )
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_obj_inside_cpuset_by_depth.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_get_obj_inside_cpuset_by_depth.restype = obj_t


@_cfndoc
def get_obj_inside_cpuset_by_depth(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, depth: int, idx: int
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_obj_inside_cpuset_by_depth(
        topology, cpuset, depth, idx
    )
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_obj_inside_cpuset_by_type.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_get_obj_inside_cpuset_by_type.restype = obj_t


@_cfndoc
def get_obj_inside_cpuset_by_type(
    topology: topology_t,
    cpuset: hwloc_const_cpuset_t,
    obj_type: hwloc_obj_type_t,
    idx: int,
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_obj_inside_cpuset_by_type(
        topology, cpuset, obj_type, idx
    )
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_nbobjs_inside_cpuset_by_depth.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
]
_pyhwloc_lib.pyhwloc_get_nbobjs_inside_cpuset_by_depth.restype = ctypes.c_uint


@_cfndoc
def get_nbobjs_inside_cpuset_by_depth(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, depth: int
) -> int:
    return _pyhwloc_lib.pyhwloc_get_nbobjs_inside_cpuset_by_depth(
        topology, cpuset, depth
    )


_pyhwloc_lib.pyhwloc_get_nbobjs_inside_cpuset_by_type.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
]
_pyhwloc_lib.pyhwloc_get_nbobjs_inside_cpuset_by_type.restype = ctypes.c_int


@_cfndoc
def get_nbobjs_inside_cpuset_by_type(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, obj_type: hwloc_obj_type_t
) -> int:
    return _pyhwloc_lib.pyhwloc_get_nbobjs_inside_cpuset_by_type(
        topology, cpuset, obj_type
    )


_pyhwloc_lib.pyhwloc_get_obj_index_inside_cpuset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_obj_index_inside_cpuset.restype = ctypes.c_int


@_cfndoc
def get_obj_index_inside_cpuset(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, obj: ObjPtr
) -> int:
    return _pyhwloc_lib.pyhwloc_get_obj_index_inside_cpuset(topology, cpuset, obj)


###########################################
# Finding Objects covering at least CPU set
###########################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00153.php


_pyhwloc_lib.pyhwloc_get_child_covering_cpuset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_child_covering_cpuset.restype = obj_t


@_cfndoc
def get_child_covering_cpuset(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, parent: ObjPtr
) -> ObjPtr | None:
    child_obj = _pyhwloc_lib.pyhwloc_get_child_covering_cpuset(topology, cpuset, parent)
    if not child_obj:
        return None
    return child_obj


_pyhwloc_lib.pyhwloc_get_obj_covering_cpuset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
]
_pyhwloc_lib.pyhwloc_get_obj_covering_cpuset.restype = obj_t


@_cfndoc
def get_obj_covering_cpuset(
    topology: topology_t, cpuset: hwloc_const_cpuset_t
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_obj_covering_cpuset(topology, cpuset)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_obj_covering_cpuset_by_depth.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_next_obj_covering_cpuset_by_depth.restype = obj_t


@_cfndoc
def get_next_obj_covering_cpuset_by_depth(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, depth: int, prev: ObjPtr
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_obj_covering_cpuset_by_depth(
        topology, cpuset, depth, prev
    )
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_obj_covering_cpuset_by_type.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    ctypes.c_int,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_next_obj_covering_cpuset_by_type.restype = obj_t


@_cfndoc
def get_next_obj_covering_cpuset_by_type(
    topology: topology_t,
    cpuset: hwloc_const_cpuset_t,
    obj_type: hwloc_obj_type_t,
    prev: ObjPtr,
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_obj_covering_cpuset_by_type(
        topology, cpuset, obj_type, prev
    )
    if not obj:
        return None
    return obj


#######################################
# Looking at Ancestor and Child Objects
#######################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00154.php


_pyhwloc_lib.pyhwloc_get_ancestor_obj_by_depth.argtypes = [
    topology_t,
    ctypes.c_int,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_ancestor_obj_by_depth.restype = obj_t


@_cfndoc
def get_ancestor_obj_by_depth(
    topology: topology_t, depth: int, obj: ObjPtr
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_ancestor_obj_by_depth(topology, depth, obj)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_ancestor_obj_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_ancestor_obj_by_type.restype = obj_t


@_cfndoc
def get_ancestor_obj_by_type(
    topology: topology_t, obj_type: hwloc_obj_type_t, obj: ObjPtr
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_ancestor_obj_by_type(topology, obj_type, obj)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_common_ancestor_obj.argtypes = [
    topology_t,
    obj_t,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_common_ancestor_obj.restype = obj_t


@_cfndoc
def get_common_ancestor_obj(topology: topology_t, obj1: ObjPtr, obj2: ObjPtr) -> ObjPtr:
    # This function cannot return NULL.
    return _pyhwloc_lib.pyhwloc_get_common_ancestor_obj(topology, obj1, obj2)


_pyhwloc_lib.pyhwloc_obj_is_in_subtree.argtypes = [
    topology_t,
    obj_t,
    obj_t,
]
_pyhwloc_lib.pyhwloc_obj_is_in_subtree.restype = ctypes.c_int


@_cfndoc
def obj_is_in_subtree(topology: topology_t, obj: ObjPtr, subtree_root: ObjPtr) -> bool:
    result = _pyhwloc_lib.pyhwloc_obj_is_in_subtree(topology, obj, subtree_root)
    return bool(result)


_pyhwloc_lib.pyhwloc_get_next_child.argtypes = [
    topology_t,
    obj_t,
    obj_t,
]
_pyhwloc_lib.pyhwloc_get_next_child.restype = obj_t


@_cfndoc
def get_next_child(
    topology: topology_t, parent: ObjPtr, prev: ObjPtr | None
) -> ObjPtr | None:
    child_obj = _pyhwloc_lib.pyhwloc_get_next_child(topology, parent, prev)
    if not child_obj:
        return None
    return child_obj


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
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_cache_covering_cpuset(topology, cpuset)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_shared_cache_covering_obj.argtypes = [topology_t, obj_t]
_pyhwloc_lib.pyhwloc_get_shared_cache_covering_obj.restype = obj_t


@_cfndoc
def get_shared_cache_covering_obj(topology: topology_t, obj: ObjPtr) -> ObjPtr | None:
    robj = _pyhwloc_lib.pyhwloc_get_shared_cache_covering_obj(topology, obj)
    if not robj:
        return None
    return robj


########################################
# Finding objects, miscellaneous helpers
########################################


# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00156.php


_pyhwloc_lib.pyhwloc_bitmap_singlify_per_core.argtypes = [
    topology_t,
    bitmap_t,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_bitmap_singlify_per_core.restype = ctypes.c_int


@_cfndoc
def bitmap_singlify_per_core(
    topology: topology_t, cpuset: bitmap_t, which: int
) -> None:
    _checkc(_pyhwloc_lib.pyhwloc_bitmap_singlify_per_core(topology, cpuset, which))


_pyhwloc_lib.pyhwloc_get_pu_obj_by_os_index.argtypes = [topology_t, ctypes.c_uint]
_pyhwloc_lib.pyhwloc_get_pu_obj_by_os_index.restype = obj_t


@_cfndoc
def get_pu_obj_by_os_index(topology: topology_t, os_index: int) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_pu_obj_by_os_index(topology, os_index)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_numanode_obj_by_os_index.argtypes = [topology_t, ctypes.c_uint]
_pyhwloc_lib.pyhwloc_get_numanode_obj_by_os_index.restype = obj_t


@_cfndoc
def get_numanode_obj_by_os_index(topology: topology_t, os_index: int) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_numanode_obj_by_os_index(topology, os_index)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_closest_objs.argtypes = [
    topology_t,
    obj_t,
    ctypes.POINTER(obj_t),
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_get_closest_objs.restype = ctypes.c_uint


@_cfndoc
def get_closest_objs(
    topology: topology_t, src: ObjPtr, objs: ctypes.Array, max_objs: int
) -> int:
    return _pyhwloc_lib.pyhwloc_get_closest_objs(topology, src, objs, max_objs)


_pyhwloc_lib.pyhwloc_get_obj_below_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.c_uint,
    ctypes.c_int,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_get_obj_below_by_type.restype = obj_t


@_cfndoc
def get_obj_below_by_type(
    topology: topology_t,
    type1: hwloc_obj_type_t,
    idx1: int,
    type2: hwloc_obj_type_t,
    idx2: int,
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_obj_below_by_type(topology, type1, idx1, type2, idx2)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_obj_below_array_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_uint),
]
_pyhwloc_lib.pyhwloc_get_obj_below_array_by_type.restype = obj_t


@_cfndoc
def get_obj_below_array_by_type(
    topology: topology_t,
    nr: int,
    typev: ctypes.Array,
    idxv: ctypes.Array,
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_obj_below_array_by_type(topology, nr, typev, idxv)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_obj_with_same_locality.argtypes = [
    topology_t,
    obj_t,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_ulong,
]
_pyhwloc_lib.pyhwloc_get_obj_with_same_locality.restype = obj_t


@_cfndoc
def get_obj_with_same_locality(
    topology: topology_t,
    src: ObjPtr,
    obj_type: hwloc_obj_type_t,
    subtype: str | None,
    nameprefix: str | None,
    flags: int,
) -> ObjPtr | None:
    subtype_bytes = subtype.encode("utf-8") if subtype else None
    nameprefix_bytes = nameprefix.encode("utf-8") if nameprefix else None
    obj = _pyhwloc_lib.pyhwloc_get_obj_with_same_locality(
        topology, src, obj_type, subtype_bytes, nameprefix_bytes, flags
    )
    if not obj:
        return None
    return obj


####################################
# Distributing items over a topology
####################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00157.php


@_cenumdoc
class hwloc_distrib_flags_e(IntEnum):
    HWLOC_DISTRIB_FLAG_REVERSE = 1 << 0


_pyhwloc_lib.pyhwloc_distrib.argtypes = [
    topology_t,
    ctypes.POINTER(obj_t),
    ctypes.c_uint,
    ctypes.POINTER(hwloc_cpuset_t),
    ctypes.c_uint,
    ctypes.c_int,
    ctypes.c_ulong,
]
_pyhwloc_lib.pyhwloc_distrib.restype = ctypes.c_int


@_cfndoc
def distrib(
    topology: topology_t,
    roots: ctypes._Pointer,  # Pointer[obj_t]
    n_roots: int,
    cpuset: ctypes._Pointer,  # Pointer[hwloc_cpuset_t]
    n: int,
    until: int,
    flags: int,
) -> None:
    _checkc(
        _pyhwloc_lib.pyhwloc_distrib(topology, roots, n_roots, cpuset, n, until, flags)
    )


########################################
# CPU and node sets of entire topologies
########################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00158.php

_LIB.hwloc_topology_get_complete_cpuset.argtypes = [topology_t]
_LIB.hwloc_topology_get_complete_cpuset.restype = hwloc_const_cpuset_t


@_cfndoc
def topology_get_complete_cpuset(topology: topology_t) -> hwloc_const_cpuset_t:
    # No need for free.
    return _LIB.hwloc_topology_get_complete_cpuset(topology)


_LIB.hwloc_topology_get_topology_cpuset.argtypes = [topology_t]
_LIB.hwloc_topology_get_topology_cpuset.restype = hwloc_const_cpuset_t


@_cfndoc
def topology_get_topology_cpuset(topology: topology_t) -> hwloc_const_cpuset_t:
    return _LIB.hwloc_topology_get_topology_cpuset(topology)


_LIB.hwloc_topology_get_allowed_cpuset.argtypes = [topology_t]
_LIB.hwloc_topology_get_allowed_cpuset.restype = hwloc_const_cpuset_t


@_cfndoc
def topology_get_allowed_cpuset(topology: topology_t) -> hwloc_const_cpuset_t:
    return _LIB.hwloc_topology_get_allowed_cpuset(topology)


_LIB.hwloc_topology_get_complete_nodeset.argtypes = [topology_t]
_LIB.hwloc_topology_get_complete_nodeset.restype = hwloc_const_nodeset_t


@_cfndoc
def topology_get_complete_nodeset(topology: topology_t) -> hwloc_const_nodeset_t:
    return _LIB.hwloc_topology_get_complete_nodeset(topology)


_LIB.hwloc_topology_get_topology_nodeset.argtypes = [topology_t]
_LIB.hwloc_topology_get_topology_nodeset.restype = hwloc_const_nodeset_t


@_cfndoc
def topology_get_topology_nodeset(topology: topology_t) -> hwloc_const_nodeset_t:
    return _LIB.hwloc_topology_get_topology_nodeset(topology)


_LIB.hwloc_topology_get_allowed_nodeset.argtypes = [topology_t]
_LIB.hwloc_topology_get_allowed_nodeset.restype = hwloc_const_nodeset_t


@_cfndoc
def topology_get_allowed_nodeset(topology: topology_t) -> hwloc_const_nodeset_t:
    return _LIB.hwloc_topology_get_allowed_nodeset(topology)


###########################################
# Converting between CPU sets and node sets
###########################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00159.php


_pyhwloc_lib.pyhwloc_cpuset_to_nodeset.argtypes = [
    topology_t,
    hwloc_const_cpuset_t,
    hwloc_nodeset_t,
]
_pyhwloc_lib.pyhwloc_cpuset_to_nodeset.restype = ctypes.c_int


@_cfndoc
def cpuset_to_nodeset(
    topology: topology_t, cpuset: hwloc_const_cpuset_t, nodeset: hwloc_nodeset_t
) -> None:
    _checkc(_pyhwloc_lib.pyhwloc_cpuset_to_nodeset(topology, cpuset, nodeset))


_pyhwloc_lib.pyhwloc_cpuset_from_nodeset.argtypes = [
    topology_t,
    hwloc_cpuset_t,
    hwloc_const_nodeset_t,
]
_pyhwloc_lib.pyhwloc_cpuset_from_nodeset.restype = ctypes.c_int


@_cfndoc
def cpuset_from_nodeset(
    topology: topology_t, cpuset: hwloc_cpuset_t, nodeset: hwloc_const_nodeset_t
) -> None:
    _checkc(_pyhwloc_lib.pyhwloc_cpuset_from_nodeset(topology, cpuset, nodeset))


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
def get_non_io_ancestor_obj(topology: topology_t, ioobj: ObjPtr) -> ObjPtr:
    # This function cannot return NULL.
    return _pyhwloc_lib.pyhwloc_get_non_io_ancestor_obj(topology, ioobj)


_pyhwloc_lib.pyhwloc_get_next_pcidev.argtypes = [topology_t, ctypes.POINTER(hwloc_obj)]
_pyhwloc_lib.pyhwloc_get_next_pcidev.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_pcidev(topology: topology_t, prev: ObjPtr) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_pcidev(topology, prev)
    if not obj:
        return None
    return obj


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
) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_pcidev_by_busid(topology, domain, bus, dev, func)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_pcidev_by_busidstring.argtypes = [topology_t, ctypes.c_char_p]
_pyhwloc_lib.pyhwloc_get_pcidev_by_busidstring.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_pcidev_by_busidstring(topology: topology_t, busid: str) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_pcidev_by_busidstring(
        topology, busid.encode("utf-8")
    )
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_osdev.argtypes = [topology_t, ctypes.POINTER(hwloc_obj)]
_pyhwloc_lib.pyhwloc_get_next_osdev.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_osdev(topology: topology_t, prev: ObjPtr) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_osdev(topology, prev)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_get_next_bridge.argtypes = [topology_t, ctypes.POINTER(hwloc_obj)]
_pyhwloc_lib.pyhwloc_get_next_bridge.restype = ctypes.POINTER(hwloc_obj)


@_cfndoc
def get_next_bridge(topology: topology_t, prev: ObjPtr | None) -> ObjPtr | None:
    obj = _pyhwloc_lib.pyhwloc_get_next_bridge(topology, prev)
    if not obj:
        return None
    return obj


_pyhwloc_lib.pyhwloc_bridge_covers_pcibus.argtypes = [
    ctypes.POINTER(hwloc_obj),
    ctypes.c_uint,
    ctypes.c_uint,
]
_pyhwloc_lib.pyhwloc_bridge_covers_pcibus.restype = ctypes.c_int


@_cfndoc
def bridge_covers_pcibus(bridge: ObjPtr, domain: int, bus: int) -> int:
    return _pyhwloc_lib.pyhwloc_bridge_covers_pcibus(bridge, domain, bus)


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
    _free_xmlbuffer(topology, xmlbuffer)
    return result


_LIB.hwloc_free_xmlbuffer.argtypes = [topology_t, ctypes.c_char_p]
_LIB.hwloc_free_xmlbuffer.restype = None


# This function is only used internally since we return python strings.
def _free_xmlbuffer(topology: topology_t, xmlbuffer: ctypes.c_char_p) -> None:
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
    obj: ObjPtr,
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
    obj: ObjPtr,
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
        raise _hwloc_error("hwloc_topology_export_synthetic")
    return n_written


####################################
# Retrieve distances between objects
####################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00164.php


@_cenumdoc
class hwloc_distances_kind_e(IntEnum):
    HWLOC_DISTANCES_KIND_FROM_OS = 1 << 0
    HWLOC_DISTANCES_KIND_FROM_USER = 1 << 1
    HWLOC_DISTANCES_KIND_VALUE_LATENCY = 1 << 2
    HWLOC_DISTANCES_KIND_VALUE_BANDWIDTH = 1 << 3
    HWLOC_DISTANCES_KIND_HETEROGENEOUS_TYPES = 1 << 4
    HWLOC_DISTANCES_KIND_VALUE_HOPS = 1 << 5


@_cenumdoc
class hwloc_distances_transform_e(IntEnum):
    HWLOC_DISTANCES_TRANSFORM_REMOVE_NULL = 0
    HWLOC_DISTANCES_TRANSFORM_LINKS = 1
    HWLOC_DISTANCES_TRANSFORM_MERGE_SWITCH_PORTS = 2
    HWLOC_DISTANCES_TRANSFORM_TRANSITIVE_CLOSURE = 3


@_cstructdoc()
class hwloc_distances_s(ctypes.Structure):
    _fields_ = [
        ("nbobjs", ctypes.c_uint),
        ("objs", ctypes.POINTER(obj_t)),
        ("kind", ctypes.c_ulong),
        ("values", ctypes.POINTER(hwloc_uint64_t)),
    ]


_LIB.hwloc_distances_get.argtypes = [
    topology_t,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.POINTER(hwloc_distances_s)),
    ctypes.c_ulong,
    ctypes.c_ulong,
]
_LIB.hwloc_distances_get.restype = ctypes.c_int


if TYPE_CHECKING:
    DistancesPtr = ctypes._Pointer[hwloc_distances_s]
    DistancesPtrPtr = (
        ctypes._Pointer[ctypes._Pointer[hwloc_distances_s]]
        | ctypes._CArgObject
        | ctypes.Array[ctypes._Pointer[hwloc_distances_s]]
        | None
    )
    UintPtr = ctypes._Pointer[ctypes.c_uint] | ctypes._CArgObject
else:
    DistancesPtr = ctypes._Pointer
    DistancesPtrPtr = ctypes._Pointer
    UintPtr = ctypes._Pointer


@_cfndoc
def distances_get(
    topology: topology_t,
    nr: UintPtr,
    distances: DistancesPtrPtr,
    kind: int,
) -> None:
    # flag must be 0 for now.
    _checkc(_LIB.hwloc_distances_get(topology, nr, distances, kind, 0))


_LIB.hwloc_distances_get_by_depth.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.POINTER(hwloc_distances_s)),
    ctypes.c_ulong,
    ctypes.c_ulong,
]
_LIB.hwloc_distances_get_by_depth.restype = ctypes.c_int


@_cfndoc
def distances_get_by_depth(
    topology: topology_t,
    depth: int,
    nr: UintPtr,
    distances: DistancesPtrPtr,
    kind: int,
    flags: int,
) -> None:
    _checkc(
        _LIB.hwloc_distances_get_by_depth(topology, depth, nr, distances, kind, flags)
    )


_LIB.hwloc_distances_get_by_type.argtypes = [
    topology_t,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.POINTER(hwloc_distances_s)),
    ctypes.c_ulong,
    ctypes.c_ulong,
]
_LIB.hwloc_distances_get_by_type.restype = ctypes.c_int


@_cfndoc
def distances_get_by_type(
    topology: topology_t,
    obj_type: hwloc_obj_type_t,
    nr: UintPtr,  # this is both input and output
    distances: DistancesPtrPtr,
    kind: int,
) -> None:
    # flags must be 0 for now
    _checkc(
        _LIB.hwloc_distances_get_by_type(topology, obj_type, nr, distances, kind, 0)
    )


_LIB.hwloc_distances_get_by_name.argtypes = [
    topology_t,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.POINTER(hwloc_distances_s)),
    ctypes.c_ulong,
]
_LIB.hwloc_distances_get_by_name.restype = ctypes.c_int


@_cfndoc
def distances_get_by_name(
    topology: topology_t,
    name: bytes,
    nr: UintPtr,
    distances: DistancesPtrPtr,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_distances_get_by_name(topology, name, nr, distances, flags))


_LIB.hwloc_distances_get_name.argtypes = [
    topology_t,
    ctypes.POINTER(hwloc_distances_s),
]
_LIB.hwloc_distances_get_name.restype = ctypes.c_char_p


@_cfndoc
def distances_get_name(topology: topology_t, distances: DistancesPtr) -> str | None:
    result = _LIB.hwloc_distances_get_name(topology, distances)
    if result:
        return result.decode("utf-8")
    return None


_LIB.hwloc_distances_release.argtypes = [
    topology_t,
    ctypes.POINTER(hwloc_distances_s),
]
_LIB.hwloc_distances_release.restype = None


@_cfndoc
def distances_release(topology: topology_t, distances: DistancesPtr) -> None:
    _LIB.hwloc_distances_release(topology, distances)


_LIB.hwloc_distances_transform.argtypes = [
    topology_t,
    ctypes.POINTER(hwloc_distances_s),
    ctypes.c_int,  # hwloc_distances_transform_e
    ctypes.c_void_p,
    ctypes.c_ulong,
]
_LIB.hwloc_distances_transform.restype = ctypes.c_int


@_cfndoc
def distances_transform(
    topology: topology_t,
    distances: DistancesPtr,
    transform: hwloc_distances_transform_e,
    transform_attr: ctypes.c_void_p,
    flags: int,
) -> None:
    _checkc(
        _LIB.hwloc_distances_transform(
            topology, distances, transform, transform_attr, flags
        )
    )


##########################################
# Helpers for consulting distance matrices
##########################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00165.php

_pyhwloc_lib.pyhwloc_distances_obj_index.argtypes = [
    ctypes.POINTER(hwloc_distances_s),
    obj_t,
]
_pyhwloc_lib.pyhwloc_distances_obj_index.restype = ctypes.c_int


@_cfndoc
def distances_obj_index(distances: DistancesPtr, obj: ObjPtr) -> int:
    # Returns -1 if not found
    return _pyhwloc_lib.pyhwloc_distances_obj_index(distances, obj)


_pyhwloc_lib.pyhwloc_distances_obj_pair_values.argtypes = [
    ctypes.POINTER(hwloc_distances_s),
    obj_t,
    obj_t,
    ctypes.POINTER(hwloc_uint64_t),
    ctypes.POINTER(hwloc_uint64_t),
]
_pyhwloc_lib.pyhwloc_distances_obj_pair_values.restype = ctypes.c_int


@_cfndoc
def distances_obj_pair_values(
    distances: DistancesPtr,
    obj1: ObjPtr,
    obj2: ObjPtr,
) -> tuple[int, int]:
    value1to2 = ctypes.c_uint64(0)
    value2to1 = ctypes.c_uint64(0)
    rc = _pyhwloc_lib.pyhwloc_distances_obj_pair_values(
        distances, obj1, obj2, ctypes.byref(value1to2), ctypes.byref(value2to1)
    )
    if rc == -1:
        raise ValueError("obj1 or obj2 is not involved in the distances structure.")
    _checkc(rc)
    return int(value1to2.value), int(value2to1.value)


###############################
# Add distances between objects
###############################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00166.php

# This is an opaque pointer of hwloc_internal_distances_s
# FIXME(jiamingy): How to make sure this is not leaked?
hwloc_distances_add_handle_t = ctypes.c_void_p


@_cenumdoc
class hwloc_distances_add_flag_e(IntEnum):
    HWLOC_DISTANCES_ADD_FLAG_GROUP = 1 << 0
    HWLOC_DISTANCES_ADD_FLAG_GROUP_INACCURATE = 1 << 1


_LIB.hwloc_distances_add_create.argtypes = [
    topology_t,
    ctypes.c_char_p,
    ctypes.c_ulong,
    ctypes.c_ulong,
]
_LIB.hwloc_distances_add_create.restype = hwloc_distances_add_handle_t


@_cfndoc
def distances_add_create(
    topology: topology_t, name: str, kind: int
) -> hwloc_distances_add_handle_t:
    # The distance from object i to object j is in slot i*nbobjs+j. (row-major)
    name_bytes = name.encode("utf-8")
    # flags must be 0 for now
    dist_obj = _LIB.hwloc_distances_add_create(topology, name_bytes, kind, 0)
    if not dist_obj:
        raise _hwloc_error("hwloc_distances_add_create")
    return dist_obj


_LIB.hwloc_distances_add_values.argtypes = [
    topology_t,
    hwloc_distances_add_handle_t,
    ctypes.c_uint,
    ctypes.POINTER(obj_t),
    ctypes.POINTER(hwloc_uint64_t),
    ctypes.c_ulong,
]
_LIB.hwloc_distances_add_values.restype = ctypes.c_int


@_cfndoc
def distances_add_values(
    topology: topology_t,
    handle: hwloc_distances_add_handle_t,
    nbobjs: int,
    objs: ctypes.Array,
    values: ctypes.Array,
) -> None:
    # flags must be 0 for now
    _checkc(_LIB.hwloc_distances_add_values(topology, handle, nbobjs, objs, values, 0))


_LIB.hwloc_distances_add_commit.argtypes = [
    topology_t,
    hwloc_distances_add_handle_t,
    ctypes.c_ulong,
]
_LIB.hwloc_distances_add_commit.restype = ctypes.c_int


@_cfndoc
def distances_add_commit(
    topology: topology_t, handle: hwloc_distances_add_handle_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_distances_add_commit(topology, handle, flags))


##################################
# Remove distances between objects
##################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00167.php

_LIB.hwloc_distances_remove.argtypes = [topology_t]
_LIB.hwloc_distances_remove.restype = ctypes.c_int


@_cfndoc
def distances_remove(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_distances_remove(topology))


_LIB.hwloc_distances_remove_by_depth.argtypes = [topology_t, ctypes.c_int]
_LIB.hwloc_distances_remove_by_depth.restype = ctypes.c_int


@_cfndoc
def distances_remove_by_depth(topology: topology_t, depth: int) -> None:
    _checkc(_LIB.hwloc_distances_remove_by_depth(topology, depth))


_pyhwloc_lib.pyhwloc_distances_remove_by_type.argtypes = [topology_t, ctypes.c_int]
_pyhwloc_lib.pyhwloc_distances_remove_by_type.restype = ctypes.c_int


@_cfndoc
def distances_remove_by_type(topology: topology_t, obj_type: hwloc_obj_type_t) -> None:
    _checkc(_pyhwloc_lib.pyhwloc_distances_remove_by_type(topology, obj_type))


_LIB.hwloc_distances_release_remove.argtypes = [
    topology_t,
    ctypes.POINTER(hwloc_distances_s),
]
_LIB.hwloc_distances_release_remove.restype = ctypes.c_int


@_cfndoc
def distances_release_remove(topology: topology_t, distances: DistancesPtr) -> None:
    _checkc(_LIB.hwloc_distances_release_remove(topology, distances))


###################################################################
# Comparing memory node attributes for finding where to allocate on
###################################################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00168.php

hwloc_memattr_id_t = ctypes.c_uint


@_cenumdoc
class hwloc_memattr_id_e(IntEnum):
    HWLOC_MEMATTR_ID_CAPACITY = 0
    HWLOC_MEMATTR_ID_LOCALITY = 1
    HWLOC_MEMATTR_ID_BANDWIDTH = 2
    HWLOC_MEMATTR_ID_LATENCY = 3
    HWLOC_MEMATTR_ID_READ_BANDWIDTH = 4
    HWLOC_MEMATTR_ID_WRITE_BANDWIDTH = 5
    HWLOC_MEMATTR_ID_READ_LATENCY = 6
    HWLOC_MEMATTR_ID_WRITE_LATENCY = 7
    HWLOC_MEMATTR_ID_MAX = 8


@_cenumdoc
class hwloc_location_type_e(IntEnum):
    HWLOC_LOCATION_TYPE_OBJECT = 0
    HWLOC_LOCATION_TYPE_CPUSET = 1


@_cenumdoc
class hwloc_local_numanode_flag_e(IntEnum):
    HWLOC_LOCAL_NUMANODE_FLAG_LARGER_LOCALITY = 1 << 0
    HWLOC_LOCAL_NUMANODE_FLAG_SMALLER_LOCALITY = 1 << 1
    HWLOC_LOCAL_NUMANODE_FLAG_ALL = 1 << 2
    HWLOC_LOCAL_NUMANODE_FLAG_INTERSECT_LOCALITY = 1 << 3


@_cuniondoc("hwloc_location")
class hwloc_location_u(ctypes.Union):
    _fields_ = [
        ("cpuset", hwloc_cpuset_t),
        ("object", obj_t),
    ]


@_cstructdoc()
class hwloc_location(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),  # hwloc_location_type_e
        ("location", hwloc_location_u),
    ]


if TYPE_CHECKING:
    LocationPtr = ctypes._Pointer[hwloc_location] | ctypes._CArgObject
else:
    LocationPtr = ctypes._Pointer


_LIB.hwloc_memattr_get_by_name.argtypes = [
    topology_t,
    ctypes.c_char_p,
    ctypes.POINTER(hwloc_memattr_id_t),
]
_LIB.hwloc_memattr_get_by_name.restype = ctypes.c_int


@_cfndoc
def memattr_get_by_name(
    topology: topology_t,
    name: bytes,
    idx: ctypes._Pointer,  # [hwloc_memattr_id_t]
) -> None:
    _checkc(_LIB.hwloc_memattr_get_by_name(topology, name, idx))


_LIB.hwloc_get_local_numanode_objs.argtypes = [
    topology_t,
    ctypes.POINTER(hwloc_location),
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(obj_t),
    ctypes.c_ulong,
]
_LIB.hwloc_get_local_numanode_objs.restype = ctypes.c_int


@_cfndoc
def get_local_numanode_objs(
    topology: topology_t,
    location: LocationPtr,
    nr: UintPtr,
    nodes: ObjPtr,
    flags: int,
) -> None:
    _checkc(_LIB.hwloc_get_local_numanode_objs(topology, location, nr, nodes, flags))


_LIB.hwloc_topology_get_default_nodeset.argtypes = [
    topology_t,
    hwloc_nodeset_t,
    ctypes.c_ulong,
]
_LIB.hwloc_topology_get_default_nodeset.restype = ctypes.c_int


@_cfndoc
def topology_get_default_nodeset(
    topology: topology_t, nodeset: hwloc_nodeset_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_topology_get_default_nodeset(topology, nodeset, flags))


_LIB.hwloc_memattr_get_value.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    obj_t,
    ctypes.POINTER(hwloc_location),
    ctypes.c_ulong,
    ctypes.POINTER(hwloc_uint64_t),
]
_LIB.hwloc_memattr_get_value.restype = ctypes.c_int


@_cfndoc
def memattr_get_value(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
    target_node: ObjPtr,
    initiator: LocationPtr,
) -> int:
    value = hwloc_uint64_t(0)
    # flags must be 0 for now.
    _checkc(
        _LIB.hwloc_memattr_get_value(
            topology, attribute, target_node, initiator, 0, ctypes.byref(value)
        )
    )
    return int(value.value)


_LIB.hwloc_memattr_get_best_target.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    ctypes.POINTER(hwloc_location),
    ctypes.c_ulong,
    ctypes.POINTER(obj_t),
    ctypes.POINTER(hwloc_uint64_t),
]
_LIB.hwloc_memattr_get_best_target.restype = ctypes.c_int


@_cfndoc
def memattr_get_best_target(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
    initiator: LocationPtr,
    flags: int,
    best_target: ObjPtr,
    value: ctypes._Pointer,  # [hwloc_uint64_t]
) -> None:
    _checkc(
        _LIB.hwloc_memattr_get_best_target(
            topology, attribute, initiator, flags, best_target, value
        )
    )


_LIB.hwloc_memattr_get_best_initiator.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    obj_t,
    ctypes.c_ulong,
    ctypes.POINTER(hwloc_location),
    ctypes.POINTER(hwloc_uint64_t),
]
_LIB.hwloc_memattr_get_best_initiator.restype = ctypes.c_int


@_cfndoc
def memattr_get_best_initiator(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
    target_node: ObjPtr,
    flags: int,
    best_initiator: ctypes._Pointer,  # [hwloc_location]
    value: ctypes._Pointer,  # [hwloc_uint64_t]
) -> None:
    _checkc(
        _LIB.hwloc_memattr_get_best_initiator(
            topology, attribute, target_node, flags, best_initiator, value
        )
    )


_LIB.hwloc_memattr_get_targets.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    ctypes.POINTER(hwloc_location),
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(obj_t),
    ctypes.POINTER(hwloc_uint64_t),
]
_LIB.hwloc_memattr_get_targets.restype = ctypes.c_int


@_cfndoc
def memattr_get_targets(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
    initiator: LocationPtr,
    flags: int,
    nr: UintPtr,
    targets: ObjPtr,  # [obj_t]
    values: ctypes._Pointer,  # [hwloc_uint64_t]
) -> None:
    _checkc(
        _LIB.hwloc_memattr_get_targets(
            topology, attribute, initiator, flags, nr, targets, values
        )
    )


_LIB.hwloc_memattr_get_initiators.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    obj_t,
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(hwloc_location),
    ctypes.POINTER(hwloc_uint64_t),
]
_LIB.hwloc_memattr_get_initiators.restype = ctypes.c_int


@_cfndoc
def memattr_get_initiators(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
    target_node: ObjPtr,
    flags: int,
    nr: UintPtr,
    initiators: LocationPtr,  # [hwloc_location]
    values: ctypes._Pointer,  # [hwloc_uint64_t]
) -> None:
    _checkc(
        _LIB.hwloc_memattr_get_initiators(
            topology, attribute, target_node, flags, nr, initiators, values
        )
    )


############################
# Managing memory attributes
############################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00169.php


@_cenumdoc
class hwloc_memattr_flag_e(IntEnum):
    HWLOC_MEMATTR_FLAG_HIGHER_FIRST = 1 << 0
    HWLOC_MEMATTR_FLAG_LOWER_FIRST = 1 << 1
    HWLOC_MEMATTR_FLAG_NEED_INITIATOR = 1 << 2


_LIB.hwloc_memattr_get_name.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    ctypes.POINTER(ctypes.c_char_p),
]
_LIB.hwloc_memattr_get_name.restype = ctypes.c_int


@_cfndoc
def memattr_get_name(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
) -> str:
    name = ctypes.c_char_p()
    _checkc(_LIB.hwloc_memattr_get_name(topology, attribute, ctypes.byref(name)))
    assert name.value
    return name.value.decode("utf-8")


_LIB.hwloc_memattr_get_flags.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    ctypes.POINTER(ctypes.c_ulong),
]
_LIB.hwloc_memattr_get_flags.restype = ctypes.c_int


@_cfndoc
def memattr_get_flags(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
) -> int:
    flags = ctypes.c_ulong(0)
    _checkc(_LIB.hwloc_memattr_get_flags(topology, attribute, ctypes.byref(flags)))
    return int(flags.value)


_LIB.hwloc_memattr_register.argtypes = [
    topology_t,
    ctypes.c_char_p,
    ctypes.c_ulong,
    ctypes.POINTER(hwloc_memattr_id_t),
]
_LIB.hwloc_memattr_register.restype = ctypes.c_int


@_cfndoc
def memattr_register(
    topology: topology_t,
    name: str,
    flags: int,
) -> hwloc_memattr_id_t:
    attr_id = hwloc_memattr_id_t()
    _checkc(
        _LIB.hwloc_memattr_register(
            topology, name.encode("utf-8"), flags, ctypes.byref(attr_id)
        )
    )
    return attr_id


_LIB.hwloc_memattr_set_value.argtypes = [
    topology_t,
    hwloc_memattr_id_t,
    obj_t,
    ctypes.POINTER(hwloc_location),
    ctypes.c_ulong,
    hwloc_uint64_t,
]
_LIB.hwloc_memattr_set_value.restype = ctypes.c_int


@_cfndoc
def memattr_set_value(
    topology: topology_t,
    attribute: hwloc_memattr_id_t,
    target_node: ObjPtr,
    initiator: LocationPtr,
    value: int,
) -> None:
    # flags must be 0 for now
    _checkc(
        _LIB.hwloc_memattr_set_value(
            topology, attribute, target_node, initiator, 0, value
        )
    )


####################
# Kinds of CPU cores
####################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00170.php

_LIB.hwloc_cpukinds_get_nr.argtypes = [topology_t, ctypes.c_ulong]
_LIB.hwloc_cpukinds_get_nr.restype = ctypes.c_int


@_cfndoc
def cpukinds_get_nr(topology: topology_t) -> int:
    # flags must be 0 for now.
    result = _LIB.hwloc_cpukinds_get_nr(topology, 0)
    if result < 0:
        _checkc(result)
    return result


_LIB.hwloc_cpukinds_get_by_cpuset.argtypes = [
    topology_t,
    const_bitmap_t,
    ctypes.c_ulong,
]
_LIB.hwloc_cpukinds_get_by_cpuset.restype = ctypes.c_int


@_cfndoc
def cpukinds_get_by_cpuset(topology: topology_t, cpuset: const_bitmap_t) -> int:
    # flags must be 0 for now.
    result = _LIB.hwloc_cpukinds_get_by_cpuset(topology, cpuset, 0)
    if result < 0:
        _checkc(result)
    return result


_LIB.hwloc_cpukinds_get_info.argtypes = [
    topology_t,
    ctypes.c_uint,
    bitmap_t,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.POINTER(hwloc_infos_s)),
    ctypes.c_ulong,
]
_LIB.hwloc_cpukinds_get_info.restype = ctypes.c_int


@_cfndoc
def cpukinds_get_info(
    topology: topology_t, kind_index: int
) -> tuple[bitmap_t, int, InfosPtr]:
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
            0,
        )
    )

    return cpuset, efficiency.value, infos_ptr


_LIB.hwloc_cpukinds_register.argtypes = [
    topology_t,
    bitmap_t,
    ctypes.c_int,
    ctypes.POINTER(hwloc_infos_s),
    ctypes.c_ulong,
]
_LIB.hwloc_cpukinds_register.restype = ctypes.c_int


@_cfndoc
def cpukinds_register(
    topology: topology_t,
    cpuset: bitmap_t,
    forced_efficiency: int,
    infos: hwloc_infos_s | None,
) -> None:
    pinfos = ctypes.byref(infos) if infos is not None else None
    # The parameter flags must be 0 for now.
    _checkc(
        _LIB.hwloc_cpukinds_register(topology, cpuset, forced_efficiency, pinfos, 0)
    )


######################################
# Sharing topologies between processes
######################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.0/a00185.php

_LIB.hwloc_shmem_topology_get_length.argtypes = [
    topology_t,
    ctypes.POINTER(ctypes.c_size_t),
    ctypes.c_ulong,
]
_LIB.hwloc_shmem_topology_get_length.restype = ctypes.c_int


@_cfndoc
def shmem_topology_get_length(
    topology: topology_t,
) -> int:
    length = ctypes.c_size_t()
    # flags must be 0 for now.
    _checkc(_LIB.hwloc_shmem_topology_get_length(topology, ctypes.byref(length), 0))
    return length.value


_LIB.hwloc_shmem_topology_write.argtypes = [
    topology_t,
    ctypes.c_int,
    hwloc_uint64_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_ulong,
]
_LIB.hwloc_shmem_topology_write.restype = ctypes.c_int


@_cfndoc
def shmem_topology_write(
    topology: topology_t,
    fd: int,
    fileoffset: int,
    mmap_address: ctypes.c_void_p,
    length: int,
) -> None:
    # flags must be 0 for now.
    _checkc(
        _LIB.hwloc_shmem_topology_write(
            topology, fd, fileoffset, mmap_address, length, 0
        )
    )


_LIB.hwloc_shmem_topology_adopt.argtypes = [
    ctypes.POINTER(topology_t),
    ctypes.c_int,
    hwloc_uint64_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_ulong,
]
_LIB.hwloc_shmem_topology_adopt.restype = ctypes.c_int


@_cfndoc
def shmem_topology_adopt(
    topologyp: ctypes._Pointer,  # [topology_t]
    fd: int,
    fileoffset: int,
    mmap_address: ctypes.c_void_p,
    length: int,
    flags: int,
) -> None:
    _checkc(
        _LIB.hwloc_shmem_topology_adopt(
            topologyp, fd, fileoffset, mmap_address, length, flags
        )
    )


###########
# Utilities
###########


def is_same_obj(a: ctypes._Pointer, b: ctypes._Pointer) -> bool:
    return (
        ctypes.cast(a, ctypes.c_void_p).value == ctypes.cast(b, ctypes.c_void_p).value
    )
