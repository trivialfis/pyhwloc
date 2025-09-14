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

from pyhwloc.hwloc.core import (
    get_obj_by_type,
    hwloc_location,
    hwloc_location_type_e,
    hwloc_location_u,
    hwloc_memattr_flag_e,
    hwloc_memattr_id_e,
    hwloc_memattr_id_t,
    ObjType,
    memattr_get_flags,
    memattr_get_name,
    memattr_get_value,
    memattr_register,
    memattr_set_value,
)

from .test_core import Topology

############################
# Managing memory attributes
############################


def test_memattr_get_name_flags() -> None:
    topo = Topology()

    attr_id = hwloc_memattr_id_e.HWLOC_MEMATTR_ID_BANDWIDTH
    exp_name = "Bandwidth"
    exp_flags = (
        hwloc_memattr_flag_e.HWLOC_MEMATTR_FLAG_HIGHER_FIRST
        | hwloc_memattr_flag_e.HWLOC_MEMATTR_FLAG_NEED_INITIATOR
    )

    name = memattr_get_name(topo.hdl, hwloc_memattr_id_t(attr_id))
    flags = memattr_get_flags(topo.hdl, hwloc_memattr_id_t(attr_id))

    assert name == exp_name
    assert flags == exp_flags


def test_memattr_register_and_set_value() -> None:
    """Test registering a custom memory attribute and setting its value."""
    topo = Topology()

    # Register a custom memory attribute
    attr_name = "CustomLatency"
    attr_flags = hwloc_memattr_flag_e.HWLOC_MEMATTR_FLAG_LOWER_FIRST

    # Register the new attribute
    attr_id = memattr_register(topo.hdl, attr_name, attr_flags)
    assert attr_id.value >= hwloc_memattr_id_e.HWLOC_MEMATTR_ID_MAX

    retrieved_name = memattr_get_name(topo.hdl, attr_id)
    assert retrieved_name == attr_name

    retrieved_flags = memattr_get_flags(topo.hdl, attr_id)
    assert retrieved_flags == attr_flags

    # Create an initiator location (using CPU object)
    cpu_obj = get_obj_by_type(topo.hdl, ObjType.HWLOC_OBJ_PU, 0)
    assert cpu_obj
    # Create location structure for the initiator
    initiator = hwloc_location()
    initiator.type = hwloc_location_type_e.HWLOC_LOCATION_TYPE_OBJECT
    initiator.location = hwloc_location_u()
    initiator.location.object = cpu_obj

    custom_value = 150

    # Set the attribute value
    memattr_set_value(topo.hdl, attr_id, cpu_obj, ctypes.byref(initiator), custom_value)
    value = memattr_get_value(topo.hdl, attr_id, cpu_obj, ctypes.byref(initiator))
    assert value == custom_value
