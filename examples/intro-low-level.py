import ctypes
from typing import cast

from pyhwloc.core import (
    HWLOC_UNKNOWN_INDEX,
    ObjType,
    obj_attr_snprintf,
    obj_type_snprintf,
    topology_t,
)


def print_children(topology: topology_t, obj: ObjType, depth: int) -> None:
    type_buf = ctypes.create_string_buffer(32)
    attr_buf = ctypes.create_string_buffer(1024)

    obj_type_snprintf(cast(ctypes.c_char_p, type_buf), 32, obj, 0)
    print("  " * depth + type_buf.value.decode(), end="")

    if obj.contents.os_index != HWLOC_UNKNOWN_INDEX:
        print(f"#{obj.contents.os_index}", end="")

    obj_attr_snprintf(cast(ctypes.c_char_p, attr_buf), 1024, obj, b" ", 0)
    if attr_buf.value:
        print(f"({attr_buf.value.decode()})", end="")

    print()

    for i in range(obj.contents.arity):
        child = obj.contents.children[i]
        print_children(topology, child, depth + 1)
