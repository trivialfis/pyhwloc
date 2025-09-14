####################
High Level Interface
####################

.. contents::
    :backlinks: none
    :local:

Overview
========

The ``pyhwloc`` document aims to provide an introduction to using ``hwloc`` with
Python. For an in-depth explanation about hardware topology and related concepts, please
visit the `hwloc <https://www.open-mpi.org/projects/hwloc/>`__ document instead.

Handling Enum Flags
===================

Many hwloc options and flags are enums, and some of the flags can be or'd to create
composite flags. This is a common design pattern in C (``hwloc`` is written in C), but
Python users might need some time to get used to. For non-composite flags, we can obtain
the name through helpers from the Python :py:class:`enum.IntEnum`:

.. code-block::

    from pyhwloc.topology import MemBindPolicy

    policy = MemBindPolicy.HWLOC_MEMBIND_BIND  # This is actually integer 2
    # Get a string name instead of using integers
    name = MemBindPolicy(policy).name
    print(name)

As for composite flags like the :py:class:`pyhwloc.topology.MemBindFlags`, we have helpers
for making the use of these flags more familiar for Python users. For example, one can
pass a sequence of these flags to a function:

.. code-block::

    topo.set_membind(
        target_set,
        MemBindPolicy.HWLOC_MEMBIND_BIND,
        [MemBindFlags.HWLOC_MEMBIND_STRICT, MemBindFlags.HWLOC_MEMBIND_THREAD],
    )

``set_membind`` will merge the flags internally with the ``|`` operator. Sometimes hwloc
returns composite flags. Let's pretend for a second that the ``flags`` variable is from
hwloc:

.. code-block::

    flags = MemBindFlags.HWLOC_MEMBIND_STRICT | MemBindFlags.HWLOC_MEMBIND_THREAD

To test the membership, we can simply do:

.. code-block:: python

   is_strict = flags & MemBindFlags.HWLOC_MEMBIND_STRICT
