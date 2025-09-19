/*
 * Copyright (c) 2025, NVIDIA CORPORATION.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
#include "pyhwloc_cudart_export.h"
#include <hwloc/cudart.h>

PYHWLOC_CUDART_EXPORT int pyhwloc_cudart_get_device_pci_ids(
    hwloc_topology_t topology __hwloc_attribute_unused, int idx, int *domain,
    int *bus, int *dev) {
  return hwloc_cudart_get_device_pci_ids(topology, idx, domain, bus, dev);
}

PYHWLOC_CUDART_EXPORT int pyhwloc_cudart_get_device_cpuset(
    hwloc_topology_t topology __hwloc_attribute_unused, int idx,
    hwloc_cpuset_t set) {
  return hwloc_cudart_get_device_cpuset(topology, idx, set);
}

PYHWLOC_CUDART_EXPORT hwloc_obj_t
pyhwloc_cudart_get_device_pcidev(hwloc_topology_t topology, int idx) {
  return hwloc_cudart_get_device_pcidev(topology, idx);
}

PYHWLOC_CUDART_EXPORT hwloc_obj_t pyhwloc_cudart_get_device_osdev_by_index(
    hwloc_topology_t topology, unsigned idx) {
  return hwloc_cudart_get_device_osdev_by_index(topology, idx);
}
