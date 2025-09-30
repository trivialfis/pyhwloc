###########
PyHwloc API
###########

This page provides the reference for the high-level interface. Most classes in this
interface have a ``native_handle`` property that returns a C handle for the underlying
type. Users can use it to reach to the :doc:`low-level </low_level>` interface.

.. contents::
    :backlinks: none
    :local:

.. automodule:: pyhwloc
  :members:
  :exclude-members: Topology

.. automodule:: pyhwloc.bitmap
  :members:

.. automodule:: pyhwloc.topology
  :members:


.. automodule:: pyhwloc.hwobject

.. autoclass:: pyhwloc.hwobject.ObjType
.. autoclass:: pyhwloc.hwobject.ObjOsdevType
.. autoclass:: pyhwloc.hwobject.ObjBridgeType
.. autoclass:: pyhwloc.hwobject.ObjSnprintfFlag
.. autoclass:: pyhwloc.hwobject.GetTypeDepth
.. autoclass:: pyhwloc.hwobject.ObjTypeCmp

.. autofunction:: compare_types

.. autoclass:: pyhwloc.hwobject.Object
  :members:

.. autoclass:: pyhwloc.hwobject.NumaNode
  :members:
  :inherited-members:

.. autoclass:: pyhwloc.hwobject.Cache
  :members:
  :inherited-members:

.. autoclass:: pyhwloc.hwobject.Group
  :members:
  :inherited-members:

.. autoclass:: pyhwloc.hwobject.PciDevice
  :members:
  :inherited-members:

.. autoclass:: pyhwloc.hwobject.Bridge
  :members:
  :inherited-members:

.. autoclass:: pyhwloc.hwobject.OsDevice
  :members:
  :inherited-members:

.. automodule:: pyhwloc.distances
  :members:
  :special-members: __getitem__

.. automodule:: pyhwloc.cpukinds
  :members:

.. automodule:: pyhwloc.memattrs
  :members:

.. automodule:: pyhwloc.cuda_runtime
  :members:

.. automodule:: pyhwloc.nvml
  :members:

.. automodule:: pyhwloc.cuda_driver
  :members:

.. automodule:: pyhwloc.utils
  :members: