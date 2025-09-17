# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
if(HWLOC_LIBRARY)
  unset(HWLOC_LIBRARY CACHE)
endif()

set(HWLOC_LIB_NAME hwloc)

find_path(HWLOC_INCLUDE_DIR NAMES hwloc.h)
find_library(HWLOC_LIBRARY NAMES ${HWLOC_LIB_NAME})

message(STATUS "Using hwloc library: ${HWLOC_LIBRARY}")

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(hwloc DEFAULT_MSG
                                  HWLOC_INCLUDE_DIR HWLOC_LIBRARY)

mark_as_advanced(HWLOC_INCLUDE_DIR HWLOC_LIBRARY)
