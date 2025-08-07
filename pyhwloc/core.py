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
import ctypes
import os
from ctypes.util import find_library
from enum import IntEnum
from typing import TYPE_CHECKING, Any


def normpath(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


_LIB = ctypes.CDLL("libhwloc.so", use_errno=True)

bitmap_t = ctypes.c_void_p
const_bitmap_t = ctypes.c_void_p

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


def get_api_version() -> int:
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


class hwloc_obj_cache_type_t(IntEnum):
    HWLOC_OBJ_CACHE_UNIFIED = 0
    HWLOC_OBJ_CACHE_DATA = 1
    HWLOC_OBJ_CACHE_INSTRUCTION = 2


class hwloc_obj_bridge_type_t(IntEnum):
    HWLOC_OBJ_BRIDGE_HOST = 0
    HWLOC_OBJ_BRIDGE_PCI = 1


class hwloc_obj_osdev_type_t(IntEnum):
    HWLOC_OBJ_OSDEV_STORAGE = 1 << 0
    HWLOC_OBJ_OSDEV_MEMORY = 1 << 1
    HWLOC_OBJ_OSDEV_GPU = 1 << 2
    HWLOC_OBJ_OSDEV_COPROC = 1 << 3
    HWLOC_OBJ_OSDEV_NETWORK = 1 << 4
    HWLOC_OBJ_OSDEV_OPENFABRICS = 1 << 5
    HWLOC_OBJ_OSDEV_DMA = 1 << 6


# int hwloc_compare_types 	( 	hwloc_obj_type_t  	type1, hwloc_obj_type_t  	type2)


###################################
# Topology Creation and Destruction
###################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00142.php#ga9d1e76ee15a7dee158b786c30b6a6e38

topology_t = ctypes.c_void_p


def topology_init(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_init(ctypes.byref(topology)))


def topology_load(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_load(topology))


def topology_destroy(topology: topology_t) -> None:
    _LIB.hwloc_topology_destroy(topology)


_LIB.hwloc_topology_dup.argtypes = [ctypes.POINTER(topology_t), topology_t]
_LIB.hwloc_topology_dup.restype = ctypes.c_int


def topology_dup(topology: topology_t) -> topology_t:
    new = topology_t()
    _checkc(_LIB.hwloc_topology_dup(ctypes.byref(new), topology))
    return new


def topology_abi_check(topology: topology_t) -> None:
    _checkc(_LIB.hwloc_topology_abi_check(topology))


def topology_check(topology: topology_t) -> None:
    _LIB.hwloc_topology_check(topology)


#################################
# Object levels, depths and types
#################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00143.php#gae54d1782ca9b54bea915f5c18a9158fa


def topology_get_depth(topology: topology_t) -> int:
    return _LIB.hwloc_topology_get_depth(topology)


def get_nbobjs_by_depth(topology: topology_t, depth: int) -> int:
    return _LIB.hwloc_get_nbobjs_by_depth(topology, depth)


class hwloc_obj_attr_u(ctypes.Union):
    pass


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


_LIB.hwloc_get_obj_by_depth.argtypes = [topology_t, ctypes.c_int, ctypes.c_uint]
_LIB.hwloc_get_obj_by_depth.restype = ctypes.POINTER(hwloc_obj)


if TYPE_CHECKING:
    ObjType = ctypes._Pointer[hwloc_obj]
else:
    ObjType = ctypes._Pointer


def get_obj_by_depth(topology: topology_t, depth: int, idx: int) -> ObjType:
    return _LIB.hwloc_get_obj_by_depth(topology, depth, idx)


_LIB.hwloc_bitmap_dup.argtypes = [bitmap_t]
_LIB.hwloc_bitmap_dup.restype = bitmap_t

################
# The bitmap API
################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00161.php#gae679434c1a5f41d3560a8a7e2c1b0dee


def bitmap_dup(bitmap: bitmap_t) -> bitmap_t:
    return _LIB.hwloc_bitmap_dup(bitmap)


_LIB.hwloc_bitmap_singlify.argtypes = [bitmap_t]


def bitmap_singlify(bitmap: bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_singlify(bitmap))


_LIB.hwloc_bitmap_free.argtypes = [bitmap_t]


def bitmap_free(bitmap: bitmap_t) -> None:
    _checkc(_LIB.hwloc_bitmap_free(bitmap))


_LIB.hwloc_set_cpubind.argtypes = [topology_t, bitmap_t, ctypes.c_int]


def set_cpubind(topology: topology_t, cpuset: bitmap_t, flags: int) -> None:
    _checkc(_LIB.hwloc_set_cpubind(topology, cpuset, flags))


_LIB.hwloc_bitmap_asprintf.argtypes = [ctypes.POINTER(ctypes.c_char_p), bitmap_t]
_LIB.hwloc_bitmap_asprintf.restype = ctypes.c_int


def bitmap_asprintf(strp: Any, bitmap: bitmap_t) -> int:
    # strp: char**
    result = _LIB.hwloc_bitmap_asprintf(strp, bitmap)
    if result == -1:
        errno = ctypes.get_errno()
        msg = _libc.strerror(errno)
        raise HwLocError(-1, errno, msg)
    return result


class hwloc_get_type_depth_e(IntEnum):
    HWLOC_TYPE_DEPTH_UNKNOWN = -1
    HWLOC_TYPE_DEPTH_MULTIPLE = -2
    HWLOC_TYPE_DEPTH_NUMANODE = -3
    HWLOC_TYPE_DEPTH_BRIDGE = -4
    HWLOC_TYPE_DEPTH_PCI_DEVICE = -5
    HWLOC_TYPE_DEPTH_OS_DEVICE = -6
    HWLOC_TYPE_DEPTH_MISC = -7
    HWLOC_TYPE_DEPTH_MEMCACHE = -8


def get_type_or_below_depth(topology: topology_t, obj_type: hwloc_obj_type_t) -> int:
    return _pyhwloc_lib.pyhwloc_get_type_or_below_depth(topology, obj_type)


if TYPE_CHECKING:
    PInfosType = ctypes._Pointer[hwloc_infos_s]
else:
    PInfosType = ctypes._Pointer

_LIB.hwloc_topology_get_infos.argtypes = [topology_t]
_LIB.hwloc_topology_get_infos.restype = ctypes.POINTER(hwloc_infos_s)


def topology_get_infos(topology: topology_t) -> PInfosType:
    infos = _LIB.hwloc_topology_get_infos(topology)
    return infos


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


class hwloc_type_filter_e(IntEnum):
    HWLOC_TYPE_FILTER_KEEP_ALL = 0
    HWLOC_TYPE_FILTER_KEEP_NONE = 1
    HWLOC_TYPE_FILTER_KEEP_STRUCTURE = 2
    HWLOC_TYPE_FILTER_KEEP_IMPORTANT = 3


# int 	hwloc_topology_set_flags (hwloc_topology_t topology, unsigned long flags)

# unsigned long 	hwloc_topology_get_flags (hwloc_topology_t topology)

# int 	hwloc_topology_is_thissystem (hwloc_topology_t restrict topology)

# const struct hwloc_topology_support * 	hwloc_topology_get_support (hwloc_topology_t restrict topology)

# int 	hwloc_topology_set_type_filter (hwloc_topology_t topology, hwloc_obj_type_t type, enum hwloc_type_filter_e filter)

# int 	hwloc_topology_get_type_filter (hwloc_topology_t topology, hwloc_obj_type_t type, enum hwloc_type_filter_e *filter)


def topology_set_all_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_all_types_filter(topology, filter))


def topology_set_cache_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_cache_types_filter(topology, filter))


def hwloc_topology_set_icache_types_filter(
    topology: topology_t, filter: hwloc_type_filter_e
) -> None:
    _checkc(_LIB.hwloc_topology_set_icache_types_filter(topology, filter))


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


################
# Memory binding
################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00147.php#gadf87089ef533db40460ccc24b5bc0d65


class hwloc_membind_policy_t(IntEnum):
    HWLOC_MEMBIND_DEFAULT = 0
    HWLOC_MEMBIND_FIRSTTOUCH = 1
    HWLOC_MEMBIND_BIND = 2
    HWLOC_MEMBIND_INTERLEAVE = 3
    HWLOC_MEMBIND_WEIGHTED_INTERLEAVE = 5
    HWLOC_MEMBIND_NEXTTOUCH = 4
    HWLOC_MEMBIND_MIXED = -1


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


def get_area_memlocation(
    topology: topology_t, addr: ctypes.c_void_p, length: int, set: bitmap_t, flags: int
) -> None:
    _checkc(_LIB.hwloc_get_area_memlocation(topology, addr, length, set, flags))


_LIB.hwloc_alloc.argtypes = [topology_t, ctypes.c_size_t]
_LIB.hwloc_alloc.restype = ctypes.c_void_p


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


_LIB.hwloc_alloc_membind_policy.argtypes = [
    topology_t,
    ctypes.c_size_t,
    const_bitmap_t,
    ctypes.c_int,
    ctypes.c_int,
]
_LIB.hwloc_alloc_membind_policy.restype = ctypes.c_void_p


def alloc_membind_policy(
    topology: topology_t,
    length: int,
    set: const_bitmap_t,
    policy: hwloc_membind_policy_t,
    flags: int,
) -> ctypes.c_void_p:
    result = _LIB.hwloc_alloc_membind_policy(topology, length, set, policy, flags)
    if not result:
        raise HwLocError(-1, 0, b"hwloc_alloc_membind_policy failed")
    return result


_LIB.hwloc_free.argtypes = [topology_t, ctypes.c_void_p, ctypes.c_size_t]
_LIB.hwloc_free.restype = ctypes.c_int


def free(topology: topology_t, addr: ctypes.c_void_p, length: int) -> None:
    _checkc(_LIB.hwloc_free(topology, addr, length))


#############################################################
# Converting between Object Types and Attributes, and Strings
#############################################################

# https://www.open-mpi.org/projects/hwloc/doc/v2.12.1/a00144.php#ga6a38b931e5d45e8af4323a169482fe39

_LIB.hwloc_obj_type_string.argtypes = [ctypes.c_int]
_LIB.hwloc_obj_type_string.restype = ctypes.c_char_p


def hwloc_obj_type_string(obj_type: hwloc_obj_type_t) -> bytes:
    return _LIB.hwloc_obj_type_string(obj_type).value


_LIB.hwloc_obj_type_snprintf.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    obj_t,
    ctypes.c_int,
]
_LIB.hwloc_obj_type_snprintf.restype = ctypes.c_int


def obj_type_snprintf(
    string: ctypes.c_char_p, size: int, obj: ObjType, verbose: int
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


def obj_attr_snprintf(
    string: ctypes.c_char_p,
    size: int,
    obj: ObjType,
    separator: ctypes.c_char_p,
    verbose: int,
) -> int:
    return _LIB.hwloc_obj_attr_snprintf(string, size, obj, separator, verbose)
