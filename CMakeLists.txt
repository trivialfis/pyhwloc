# Copyright (c) 2025, NVIDIA CORPORATION.
set(CMAKE_POLICY_DEFAULT_CMP0144 NEW)
cmake_minimum_required(VERSION 3.18 FATAL_ERROR)

project(pyhwloc LANGUAGES C VERSION 0.0.0)

list(APPEND CMAKE_MODULE_PATH "${pyhwloc_SOURCE_DIR}/cmake/")

option(PYHWLOC_FETCH_HWLOC "Fetch hwloc from GitHub instead of using system version" OFF)

add_library(pyhwloc SHARED src/ext/pyhwloc.c)

set(PYHWLOC_OUTPUT_DIR ${pyhwloc_SOURCE_DIR}/src/pyhwloc/_lib/)

if(PYHWLOC_FETCH_HWLOC)
  set(PYHWLOC_CONFIG_HWLOC OFF CACHE BOOL "")

  include(FetchContent)
  FetchContent_Declare(
    hwloc
    GIT_REPOSITORY https://github.com/open-mpi/hwloc.git
    GIT_TAG        1098578d77d9cec7b8154479ecb7aa9f7d483950
  )

  # Configure hwloc build options
  FetchContent_MakeAvailable(hwloc)
  message(STATUS "src: ${hwloc_SOURCE_DIR}, dst: ${hwloc_BINARY_DIR}")
  if(NOT PYHWLOC_CONFIG_HWLOC)
    execute_process(
      COMMAND ${hwloc_SOURCE_DIR}/autogen.sh WORKING_DIRECTORY ${hwloc_SOURCE_DIR}
    )
    execute_process(
      COMMAND ${hwloc_SOURCE_DIR}/configure --enable-plugins --prefix=${PYHWLOC_OUTPUT_DIR}
      WORKING_DIRECTORY ${hwloc_BINARY_DIR}
    )
    set(PYHWLOC_CONFIG_HWLOC ON CACHE BOOL "" FORCE)
  endif()
  include(ProcessorCount)
  ProcessorCount(nproc)

  add_custom_command(
    OUTPUT ${PYHWLOC_OUTPUT_DIR}/lib/libhwloc.so COMMAND make -j${nproc} install WORKING_DIRECTORY ${hwloc_BINARY_DIR}
  )
  add_custom_target(build_hwloc DEPENDS ${PYHWLOC_OUTPUT_DIR}/lib/libhwloc.so)
  add_dependencies(pyhwloc build_hwloc)
  set(HWLOC_ROOT ${PYHWLOC_OUTPUT_DIR})
  set_target_properties(pyhwloc PROPERTIES
    # Do not add anything outside of the package
    INSTALL_RPATH_USE_LINK_PATH OFF
    # Do not add system toolchain path
    INSTALL_REMOVE_ENVIRONMENT_RPATH ON
    # Use relative path
    BUILD_RPATH_USE_ORIGIN ON)
endif()

find_package(hwloc REQUIRED)
message(STATUS "HWLOC_LIBRARY: ${HWLOC_LIBRARY}")
find_package(CUDAToolkit REQUIRED COMPONENTS nvml cuda_driver cudart_static)

target_link_libraries(pyhwloc PRIVATE ${HWLOC_LIBRARY})
target_include_directories(pyhwloc PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc)

add_library(pyhwloc_cuda SHARED src/ext/cudr.c)
target_link_libraries(pyhwloc_cuda PRIVATE CUDA::cuda_driver ${HWLOC_LIBRARY})
target_include_directories(pyhwloc_cuda PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc_cuda)

add_library(pyhwloc_cudart SHARED src/ext/cudart.c)
target_link_libraries(pyhwloc_cudart PRIVATE CUDA::cudart ${HWLOC_LIBRARY})
target_include_directories(pyhwloc_cudart PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc_cudart)

add_library(pyhwloc_nvml SHARED src/ext/nvml.c)
target_link_libraries(pyhwloc_nvml PRIVATE CUDA::nvml ${HWLOC_LIBRARY})
target_include_directories(pyhwloc_nvml PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc_nvml)

include(GenerateExportHeader)
generate_export_header(pyhwloc)

function(set_output_directory target dir)
  set_target_properties(${target} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${dir}
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${dir}
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${dir}
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${dir}
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${dir}
    LIBRARY_OUTPUT_DIRECTORY ${dir}
    LIBRARY_OUTPUT_DIRECTORY_DEBUG ${dir}
    LIBRARY_OUTPUT_DIRECTORY_RELEASE ${dir}
    LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO ${dir}
    LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL ${dir}
    ARCHIVE_OUTPUT_DIRECTORY ${dir}
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG ${dir}
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${dir}
    ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO ${dir}
    ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL ${dir})
endfunction()

foreach(lib IN LISTS PYHWLOC_LIBS)
  target_include_directories(${lib} PRIVATE ${pyhwloc_BINARY_DIR})
  if(PYHWLOC_FETCH_HWLOC)
    set_target_properties(${lib} PROPERTIES
      INSTALL_RPATH "$ORIGIN/lib"
      INSTALL_RPATH_USE_LINK_PATH OFF
      BUILD_RPATH_USE_ORIGIN ON)
  endif()
endforeach()

include(GNUInstallDirs)
install(TARGETS ${PYHWLOC_LIBS}
  ARCHIVE DESTINATION ${PYHWLOC_OUTPUT_DIR}
  LIBRARY DESTINATION ${PYHWLOC_OUTPUT_DIR}
  RUNTIME DESTINATION ${PYHWLOC_OUTPUT_DIR}
  INCLUDES DESTINATION ${PYHWLOC_OUTPUT_DIR}
)
