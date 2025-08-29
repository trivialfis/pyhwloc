#include "pyhwloc_export.h"
#include <hwloc.h>

extern "C" {
PYHWLOC_EXPORT int pyhwloc_get_type_or_below_depth(hwloc_topology_t topology,
                                                   hwloc_obj_type_t type) {
  return hwloc_get_type_or_below_depth(topology, type);
}

PYHWLOC_EXPORT int pyhwloc_obj_add_info(hwloc_obj_t obj, const char *name,
                                        const char *value) {
  return hwloc_obj_add_info(obj, name, value);
}

PYHWLOC_EXPORT char const *pyhwloc_get_info_by_name(struct hwloc_infos_s *infos,
                                                    const char *name) {
  return hwloc_get_info_by_name(infos, name);
}

PYHWLOC_EXPORT void *pyhwloc_alloc_membind_policy(hwloc_topology_t topology,
                                                  size_t len,
                                                  hwloc_const_cpuset_t set,
                                                  hwloc_membind_policy_t policy,
                                                  int flags) {
  return hwloc_alloc_membind_policy(topology, len, set, policy, flags);
}
}
