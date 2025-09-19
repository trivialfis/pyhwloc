/*
 * Copyright (c) 2025, NVIDIA CORPORATION.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
#include "pyhwloc_cuda_export.h"
#include <hwloc/cuda.h>

PYHWLOC_CUDA_EXPORT int pyhwloc_cuda_get_device_pci_ids(
    hwloc_topology_t topology __hwloc_attribute_unused, CUdevice cudevice,
    int *domain, int *bus, int *dev) {
  return hwloc_cuda_get_device_pci_ids(topology, cudevice, domain, bus, dev);
}

PYHWLOC_CUDA_EXPORT int pyhwloc_cuda_get_device_cpuset(
    hwloc_topology_t topology __hwloc_attribute_unused, CUdevice cudevice,
    hwloc_cpuset_t set) {
  return hwloc_cuda_get_device_cpuset(topology, cudevice, set);
}

PYHWLOC_CUDA_EXPORT hwloc_obj_t
pyhwloc_cuda_get_device_pcidev(hwloc_topology_t topology, CUdevice cudevice) {
  return hwloc_cuda_get_device_pcidev(topology, cudevice);
}

PYHWLOC_CUDA_EXPORT hwloc_obj_t
pyhwloc_cuda_get_device_osdev(hwloc_topology_t topology, CUdevice cudevice) {
  return hwloc_cuda_get_device_osdev(topology, cudevice);
}

PYHWLOC_CUDA_EXPORT hwloc_obj_t pyhwloc_cuda_get_device_osdev_by_index(
    hwloc_topology_t topology, unsigned idx) {
  return hwloc_cuda_get_device_osdev_by_index(topology, idx);
}
