#include "pyhwloc_export.h"
#include <hwloc.h>

extern "C" {
PYHWLOC_EXPORT int pyhwloc_get_type_or_below_depth(hwloc_topology_t topology,
                                                   hwloc_obj_type_t type) {
  return hwloc_get_type_or_below_depth(topology, type);
}

PYHWLOC_EXPORT void *pyhwloc_alloc_membind_policy(hwloc_topology_t topology,
                                                  size_t len,
                                                  hwloc_const_cpuset_t set,
                                                  hwloc_membind_policy_t policy,
                                                  int flags) {
  return hwloc_alloc_membind_policy(topology, len, set, policy, flags);
}

// Bitmap
PYHWLOC_EXPORT int pyhwloc_bitmap_alloc(void **out) {
  hwloc_bitmap_t ptr = hwloc_bitmap_alloc();
  hwloc_bitmap_alloc_full();
  if (!ptr) {
    return 1;
  }
  *out = ptr;
  return 0;
}

PYHWLOC_EXPORT int pyhwloc_bitmap_alloc_full(void **out) {
  hwloc_bitmap_t ptr = hwloc_bitmap_alloc_full();
  if (!ptr) {
    return 1;
  }
  *out = ptr;

  return 0;
}

// Object levels, depths and types
PYHWLOC_EXPORT int pyhwloc_get_type_or_above_depth(hwloc_topology_t topology,
                                                   hwloc_obj_type_t type) {

  return hwloc_get_type_or_above_depth(topology, type);
}

PYHWLOC_EXPORT int pyhwloc_get_nbobjs_by_type(hwloc_topology_t topology,
                                              hwloc_obj_type_t type) {
  return hwloc_get_nbobjs_by_type(topology, type);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_root_obj(hwloc_topology_t topology) {

  return hwloc_get_root_obj(topology);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_obj_by_type(hwloc_topology_t topology,
                                                   hwloc_obj_type_t type,
                                                   unsigned idx) {

  return hwloc_get_obj_by_type(topology, type, idx);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_next_obj_by_depth(
    hwloc_topology_t topology, int depth, hwloc_obj_t prev) {

  return hwloc_get_next_obj_by_depth(topology, depth, prev);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_next_obj_by_type(
    hwloc_topology_t topology, hwloc_obj_type_t type, hwloc_obj_t prev) {
  return hwloc_get_next_obj_by_type(topology, type, prev);
}

// Consulting and Adding Info Attributes
PYHWLOC_EXPORT int pyhwloc_obj_add_info(hwloc_obj_t obj, const char *name,
                                        const char *value) {
  return hwloc_obj_add_info(obj, name, value);
}

PYHWLOC_EXPORT char const *pyhwloc_get_info_by_name(struct hwloc_infos_s *infos,
                                                    const char *name) {
  return hwloc_get_info_by_name(infos, name);
}

// Finding I/O objects
PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_non_io_ancestor_obj(
    hwloc_topology_t topology __hwloc_attribute_unused, hwloc_obj_t ioobj) {
  return hwloc_get_non_io_ancestor_obj(topology, ioobj);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_next_pcidev(hwloc_topology_t topology,
                                                   hwloc_obj_t prev) {
  return hwloc_get_next_pcidev(topology, prev);
}

PYHWLOC_EXPORT hwloc_obj_t
pyhwloc_get_pcidev_by_busid(hwloc_topology_t topology, unsigned domain,
                            unsigned bus, unsigned dev, unsigned func) {
  return hwloc_get_pcidev_by_busid(topology, domain, bus, dev, func);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_pcidev_by_busidstring(
    hwloc_topology_t topology, const char *busid) {
  return hwloc_get_pcidev_by_busidstring(topology, busid);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_next_osdev(hwloc_topology_t topology,
                                                  hwloc_obj_t prev) {
  return hwloc_get_next_osdev(topology, prev);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_next_bridge(hwloc_topology_t topology,
                                                   hwloc_obj_t prev) {
  return hwloc_get_next_bridge(topology, prev);
}

PYHWLOC_EXPORT int pyhwloc_bridge_covers_pcibus(hwloc_obj_t bridge,
                                                unsigned domain, unsigned bus) {

  return hwloc_bridge_covers_pcibus(bridge, domain, bus);
}

// Looking at Cache Objects
PYHWLOC_EXPORT int
pyhwloc_get_cache_type_depth(hwloc_topology_t topology, unsigned cachelevel,
                             hwloc_obj_cache_type_t cachetype) {

  return hwloc_get_cache_type_depth(topology, cachelevel, cachetype);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_cache_covering_cpuset(
    hwloc_topology_t topology, hwloc_const_cpuset_t set) {
  return hwloc_get_cache_covering_cpuset(topology, set);
}

PYHWLOC_EXPORT hwloc_obj_t pyhwloc_get_shared_cache_covering_obj(
    hwloc_topology_t topology __hwloc_attribute_unused, hwloc_obj_t obj) {
  return hwloc_get_shared_cache_covering_obj(topology, obj);
}
}
