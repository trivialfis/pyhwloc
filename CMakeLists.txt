cmake_minimum_required(VERSION 3.18 FATAL_ERROR)

project(pyhwloc LANGUAGES C VERSION 0.0.0)

list(APPEND CMAKE_MODULE_PATH "${pyhwloc_SOURCE_DIR}/cmake/")

find_package(hwloc REQUIRED)
find_package(CUDAToolkit REQUIRED COMPONENTS nvml cuda_driver cudart_static)

add_library(pyhwloc SHARED src/src/pyhwloc.c)
target_link_libraries(pyhwloc PRIVATE ${HWLOC_LIBRARY})
target_include_directories(pyhwloc PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc)

add_library(pyhwloc_cuda SHARED src/src/cudr.c)
target_link_libraries(pyhwloc_cuda PRIVATE CUDA::cuda_driver ${HWLOC_LIBRARY})
target_include_directories(pyhwloc_cuda PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc_cuda)

add_library(pyhwloc_cudart SHARED src/src/cudart.c)
target_link_libraries(pyhwloc_cudart PRIVATE CUDA::cudart ${HWLOC_LIBRARY})
target_include_directories(pyhwloc_cudart PRIVATE ${HWLOC_INCLUDE_DIR})
list(APPEND PYHWLOC_LIBS pyhwloc_cudart)

add_library(pyhwloc_nvml SHARED src/src/nvml.c)
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
  set_output_directory(${lib} ${pyhwloc_SOURCE_DIR}/src/pyhwloc/_lib/)
  target_include_directories(${lib} PRIVATE ${pyhwloc_BINARY_DIR})
endforeach()
