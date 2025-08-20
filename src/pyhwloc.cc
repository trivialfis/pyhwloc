#include "pyhwloc_export.h"
#include <hwloc.h>

extern "C" {
PYHWLOC_EXPORT int pyhwloc_get_type_or_below_depth(hwloc_topology_t topology,
                                                   hwloc_obj_type_t type) {
  return hwloc_get_type_or_below_depth(topology, type);
}

PYHWLOC_EXPORT char const *pyhwloc_get_info_by_name(struct hwloc_infos_s *infos,
                                                    const char *name) {
  return hwloc_get_info_by_name(infos, name);
}
}
