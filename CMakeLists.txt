cmake_minimum_required(VERSION 3.18 FATAL_ERROR)

project(pyhwloc LANGUAGES C VERSION 0.0.0)

list(APPEND CMAKE_MODULE_PATH "${pyhwloc_SOURCE_DIR}/cmake/")

find_package(hwloc REQUIRED)
find_package(CUDAToolkit REQUIRED)

add_library(pyhwloc SHARED src/nvml.c src/cudr.c src/cudart.c src/pyhwloc.c)

target_link_libraries(pyhwloc PRIVATE ${HWLOC_LIBRARY} CUDA::nvml CUDA::cuda_driver CUDA::cudart)
target_include_directories(pyhwloc PRIVATE ${HWLOC_INCLUDE_DIR})

include(GenerateExportHeader)
generate_export_header(pyhwloc)
target_include_directories(pyhwloc PRIVATE ${pyhwloc_BINARY_DIR})

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

set_output_directory(pyhwloc ${pyhwloc_SOURCE_DIR}/pyhwloc/_lib/)
