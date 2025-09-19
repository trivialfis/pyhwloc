/*
 * Copyright (c) 2025, NVIDIA CORPORATION.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
#include "pyhwloc_nvml_export.h"
#include <hwloc/nvml.h>

PYHWLOC_NVML_EXPORT int pyhwloc_nvml_get_device_cpuset(
    hwloc_topology_t topology __hwloc_attribute_unused, nvmlDevice_t device,
    hwloc_cpuset_t set) {
  return hwloc_nvml_get_device_cpuset(topology, device, set);
}

PYHWLOC_NVML_EXPORT hwloc_obj_t pyhwloc_nvml_get_device_osdev_by_index(
    hwloc_topology_t topology, unsigned idx) {
  return hwloc_nvml_get_device_osdev_by_index(topology, idx);
}

PYHWLOC_NVML_EXPORT hwloc_obj_t
pyhwloc_nvml_get_device_osdev(hwloc_topology_t topology, nvmlDevice_t device) {
  return hwloc_nvml_get_device_osdev(topology, device);
}
