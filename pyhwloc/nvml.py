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
import pynvml

from .core import ObjType, _pyhwloc_lib, obj_t, topology_t

_pyhwloc_lib.pyhwloc_nvml_get_device_osdev.restype = obj_t


def get_device_osdev(topology: topology_t, device: pynvml.c_nvmlDevice_t) -> ObjType:
    dev_obj = _pyhwloc_lib.pyhwloc_nvml_get_device_osdev(topology, device)
    return dev_obj
