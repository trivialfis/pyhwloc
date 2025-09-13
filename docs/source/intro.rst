####################
High Level Interface
####################

Handling Enum Flags
===================

Many hwloc options and flags are enums, and some of the flags can be or'd to create
composite flags. For non-composite flags, we can obtain the name through helpers from the
Python :py:class:`enum.IntEnum`:

.. code-block::

    from pyhwloc.topology import MemBindPolicy

    policy = MemBindPolicy.HWLOC_MEMBIND_BIND
    # Get a string name instead of using integers
    name = MemBindPolicy(policy).name
    print(name)