/*
 * Copyright (c) 2025, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include "pyhwloc_export.h"
#include <hwloc/cuda.h>

extern "C" {
PYHWLOC_EXPORT hwloc_obj_t
pyhwloc_cuda_get_device_osdev(hwloc_topology_t topology, CUdevice cudevice) {
  return hwloc_cuda_get_device_osdev(topology, cudevice);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_cuda_get_device_osdev_by_index(
    hwloc_topology_t topology, unsigned idx) {
  return hwloc_cuda_get_device_osdev_by_index(topology, idx);
}
}
