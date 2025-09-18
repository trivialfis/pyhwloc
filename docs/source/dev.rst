###############
Developer Notes
###############

Some design decisions were made in the initial development phase. For instance, whether
something should be a Python attribute or a Python method. My choice at the time was
simple, if it's part of a C struct, it's an attribute, otherwise, it's a function. If both
are possible, like the ``cpuset`` and the ``pci_id``, we use property. This way, we can
keep it simple and allow future extension for parameters. It's ok, Python stdlib does not
use property very often: ``threading.get_ident()``, let's move on.

Hwloc has lots of setters and getters, some Python users might frown upon this design
pattern, but we decided keep it instead. Most of these setters and getters have
parameters. We could have wrapped them into properties like:

.. code-block:: python

  topology.membind[proc_id] = Membind(policy, flags)

It might be more ergonomic this way, but also feels like an un-intuitive way to writing
code. In addition, the setter and getters don't have exact match. For instance, setting
the ``DEFAULT`` policy with the membind setter might get you a ``FIRST_TOUCH`` policy in
the getter.