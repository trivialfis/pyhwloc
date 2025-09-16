###########
Hwloc C API
###########

This page provides the reference of the hwloc C interface. The Python package is built on
top of this interface. We created this page for reference purposes only and don't aim to
replace the original doxygen document.

.. contents::
    :backlinks: none
    :local:

Error reporting in the API
==========================

.. doxygengroup:: hwlocality_api_error_reporting
    :project: pyhwloc

API version
===========

.. doxygengroup:: hwlocality_api_version
    :project: pyhwloc

Object Sets (hwloc_cpuset_t and hwloc_nodeset_t)
================================================

.. doxygengroup:: hwlocality_object_sets
    :project: pyhwloc

Object Types
============

.. doxygengroup:: hwlocality_object_types
    :project: pyhwloc

Object Structure and Attributes
===============================

.. doxygengroup:: hwlocality_objects
    :project: pyhwloc

Topology Creation and Destruction
=================================

.. doxygengroup:: hwlocality_creation
    :project: pyhwloc

Object levels, depths and types
===============================

.. doxygengroup:: hwlocality_levels
    :project: pyhwloc

Converting between Object Types and Attributes, and Strings
===========================================================

.. doxygengroup:: hwlocality_object_strings
    :project: pyhwloc

Consulting and Adding Info Attributes
=====================================

.. doxygengroup:: hwlocality_info_attr
    :project: pyhwloc

CPU Binding
===========

.. doxygengroup:: hwlocality_cpubinding
    :project: pyhwloc

Memory Binding
==============

.. doxygengroup:: hwlocality_membinding
    :project: pyhwloc

Changing the Source of Topology Discovery
=========================================

.. doxygengroup:: hwlocality_setsource
    :project: pyhwloc

Topology Detection Configuration and Query
==========================================

.. doxygengroup:: hwlocality_configuration
    :project: pyhwloc

Modifying a loaded Topology
===========================

.. doxygengroup:: hwlocality_tinker
    :project: pyhwloc

Kinds of object Type
====================

.. doxygengroup:: hwlocality_helper_types
    :project: pyhwloc

Finding Objects inside a CPU set
================================

.. doxygengroup:: hwlocality_helper_find_inside
    :project: pyhwloc

Finding Objects covering at least CPU set
=========================================

.. doxygengroup:: hwlocality_helper_find_covering
    :project: pyhwloc

Looking at Ancestor and Child Objects
=====================================

.. doxygengroup:: hwlocality_helper_ancestors
    :project: pyhwloc

Looking at Cache Objects
========================

.. doxygengroup:: hwlocality_helper_find_cache
    :project: pyhwloc

Finding objects, miscellaneous helpers
======================================

.. doxygengroup:: hwlocality_helper_find_misc
    :project: pyhwloc

Distributing items over a topology
==================================

.. doxygengroup:: hwlocality_helper_distribute
    :project: pyhwloc

CPU and node sets of entire topologies
======================================

.. doxygengroup:: hwlocality_helper_topology_sets
    :project: pyhwloc

Converting between CPU sets and node sets
=========================================

.. doxygengroup:: hwlocality_helper_nodeset_convert
    :project: pyhwloc

Finding I/O objects
===================

.. doxygengroup:: hwlocality_advanced_io
    :project: pyhwloc

The bitmap API
==============

.. doxygengroup:: hwlocality_bitmap
    :project: pyhwloc

Exporting Topologies to XML
===========================

.. doxygengroup:: hwlocality_xmlexport
    :project: pyhwloc

Exporting Topologies to Synthetic
=================================

.. doxygengroup:: hwlocality_syntheticexport
    :project: pyhwloc

Retrieve distances between objects
==================================

.. doxygengroup:: hwlocality_distances_get
    :project: pyhwloc

Helpers for consulting distance matrices
========================================

.. doxygengroup:: hwlocality_distances_consult
    :project: pyhwloc

Add distances between objects
=============================

.. doxygengroup:: hwlocality_distances_add
    :project: pyhwloc

Remove distances between objects
================================

.. doxygengroup:: hwlocality_distances_remove
    :project: pyhwloc

Comparing memory node attributes for finding where to allocate on
=================================================================

.. doxygengroup:: hwlocality_memattrs
    :project: pyhwloc

Managing memory attributes
==========================

.. doxygengroup:: hwlocality_memattrs_manage
    :project: pyhwloc

Kinds of CPU cores
==================

.. doxygengroup:: hwlocality_cpukinds
    :project: pyhwloc

Linux-specific helpers
======================

.. doxygengroup:: hwlocality_linux
    :project: pyhwloc

Interoperability with Linux libnuma unsigned long masks
=======================================================

.. doxygengroup:: hwlocality_linux_libnuma_ulongs
    :project: pyhwloc

Interoperability with Linux libnuma bitmask
===========================================

.. doxygengroup:: hwlocality_linux_libnuma_bitmask
    :project: pyhwloc

Windows-specific helpers
========================

.. doxygengroup:: hwlocality_windows
    :project: pyhwloc

Interoperability with glibc sched affinity
==========================================

.. doxygengroup:: hwlocality_glibc_sched
    :project: pyhwloc

Interoperability with OpenCL
============================

.. doxygengroup:: hwlocality_opencl
    :project: pyhwloc

Interoperability with the CUDA Driver API
=========================================

.. doxygengroup:: hwlocality_cuda
    :project: pyhwloc

Interoperability with the CUDA Runtime API
==========================================

.. doxygengroup:: hwlocality_cudart
    :project: pyhwloc

Interoperability with the NVIDIA Management Library
===================================================

.. doxygengroup:: hwlocality_nvml
    :project: pyhwloc

Interoperability with the ROCm SMI Management Library
=====================================================

.. doxygengroup:: hwlocality_rsmi
    :project: pyhwloc

Interoperability with the oneAPI Level Zero interface
=====================================================

.. doxygengroup:: hwlocality_levelzero
    :project: pyhwloc

Interoperability with OpenGL displays
=====================================

.. doxygengroup:: hwlocality_gl
    :project: pyhwloc

Interoperability with OpenFabrics
=================================

.. doxygengroup:: hwlocality_openfabrics
    :project: pyhwloc

Topology differences
====================

.. doxygengroup:: hwlocality_diff
    :project: pyhwloc

Sharing topologies between processes
====================================

.. doxygengroup:: hwlocality_shmem
    :project: pyhwloc

Components and Plugins: Discovery components and backends
=========================================================

.. doxygengroup:: hwlocality_disc_components
    :project: pyhwloc

Components and Plugins: Generic components
==========================================

.. doxygengroup:: hwlocality_generic_components
    :project: pyhwloc

Components and Plugins: Core functions to be used by components
===============================================================

.. doxygengroup:: hwlocality_components_core_funcs
    :project: pyhwloc

Components and Plugins: Filtering objects
=========================================

.. doxygengroup:: hwlocality_components_filtering
    :project: pyhwloc

Components and Plugins: helpers for PCI discovery
=================================================

.. doxygengroup:: hwlocality_components_pcidisc
    :project: pyhwloc

Components and Plugins: finding PCI objects during other discoveries
====================================================================

.. doxygengroup:: hwlocality_components_pcifind
    :project: pyhwloc

Components and Plugins: distances
=================================

.. doxygengroup:: hwlocality_components_distances
    :project: pyhwloc
