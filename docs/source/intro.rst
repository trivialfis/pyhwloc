####################
Getting Started Guide
####################

.. contents::
    :backlinks: none
    :local:

Overview
========

``PyHwloc`` provides a Python interface to the Hardware Locality (hwloc) library,
providing an easier and more interactive way to discover and interact with your system's
hardware topology. For a comprehensive introduction to hardware topology concepts and
background information, please refer to the official `hwloc documentation
<https://www.open-mpi.org/projects/hwloc/>`__. This document primarily concerns the usage
of the Python interface.

**Two-Tier Architecture**

PyHwloc is designed with two layers:

1. **High-Level Interface** (Recommended): Provides Pythonic classes and methods that are
   easy to use and follow Python conventions, but has limited feature set at the moment.
2. **Low-Level Interface**: Direct mapping of the C API through ``ctypes`` for advanced
   use cases when high-level features are insufficient.

Most users should start with the high-level interface and only use the low-level API
when specific functionality is missing.

Quick Start Example
===================

Here's a simple example to get started with ``pyhwloc``:

.. code-block:: python

    from pyhwloc import Topology

    # Create and load system topology
    with Topology.from_this_system() as topo:
        # Get basic system information
        n_cores = topo.n_cores
        n_numa = topo.n_numa_nodes

        print(f"System has {n_cores} CPU cores")
        print(f"System has {n_numa} NUMA nodes")

        # Get current CPU binding
        cpuset = topo.get_cpubind()
        print(f"Current CPU binding: {cpuset}")

We have some more examples in the :doc:`/examples/index`.


Working with Enum Flags
=======================

PyHwloc uses enums extensively for options and flags, following hwloc's C API design. We
provide some syntax sugar to work with these flags in Python.

**Simple Enums**

For basic enum values, you can work with them like standard Python enums:

.. code-block:: python

    from pyhwloc.topology import MemBindPolicy

    # Use enum values directly (integer 2)
    policy = MemBindPolicy.HWLOC_MEMBIND_BIND

    # Get human-readable name
    policy_name = MemBindPolicy(policy).name
    print(f"Policy: {policy_name}")

**Composite Flags**

Some flags can be combined using bitwise OR operations. ``pyhwloc`` provides convenient
ways to work with these:

.. code-block:: python

    from pyhwloc.topology import MemBindFlags
    from pyhwloc import Topology

    with Topology.from_this_system() as topo:
        # Method 1: Pass a list of flags (recommended)
        topo.set_membind(
            target_set,
            MemBindPolicy.HWLOC_MEMBIND_BIND,
            [MemBindFlags.HWLOC_MEMBIND_STRICT, MemBindFlags.HWLOC_MEMBIND_THREAD],
        )

        # Method 2: Use bitwise OR manually
        combined_flags = MemBindFlags.HWLOC_MEMBIND_STRICT | MemBindFlags.HWLOC_MEMBIND_THREAD
        topo.set_membind(
            target_set,
            MemBindPolicy.HWLOC_MEMBIND_BIND,
            combined_flags,
        )

Please note that you can't create an instance of ``MemBindFlags`` with the ``combined``
here. The composite value is not a valid Python enum. We are using integer values after
the composition.

**Testing Flag Membership**

To check if a specific flag is present in a composite flag value:

.. code-block:: python

    # Check if a flag is set
    is_strict = bool(flags & MemBindFlags.HWLOC_MEMBIND_STRICT)
