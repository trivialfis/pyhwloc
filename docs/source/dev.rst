###############
Developer Notes
###############

Some design decisions were made in the initial development phase. For instance, whether
something should be a Python attribute or a Python method. My choice at the time was
simple, if it's part of a C struct, it's an attribute, otherwise, it's a function. If both
are possible, like the ``cpuset``, we use property. This way, we can keep it simple and
allow future extension for parameters.

Hwloc has lots of setters and getters, some Python users might frown upon this design
pattern, but we keep it instead. Most of these setters and getters have parameters,
there's no need to wrap them into more complicated properties like
``topology.membind[proc_id] = Membind(policy, flags)``. I feel that this might be more
ergonomic, but overtime only creates complexity. In addition, the setter and getters don't
have exact match. For instance, setting the ``DEFAULT`` policy with the membind setter
might get you a ``FIRST_TOUCH`` policy in the getter.