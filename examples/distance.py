#!/usr/bin/env python3
"""
Hardware Distance Exploration with pyhwloc
==========================================

This example demonstrates how to use the pyhwloc library to explore hardware
distance information in your system's topology. Distance matrices provide
crucial information about latency, bandwidth, and hop counts between different
hardware components.
"""

from pyhwloc.distance import Kind
from pyhwloc.hwobject import ObjType
from pyhwloc.topology import Topology


def discover_basic_distances() -> None:
    """Basic distance discovery - finding and examining distance matrices."""
    print("=" * 60)
    print("Basic Distance Discovery")
    print("=" * 60)

    with Topology() as topo:
        print(f"System topology loaded with {topo.depth} levels")
        print(
            f"Total objects: NUMA nodes={topo.n_numa_nodes}, "
            f"Cores={topo.n_cores}, CPUs={topo.n_cpus}"
        )
        print()

        # Discover all distance matrices in the system
        distances = topo.get_distances()

        if not distances:
            print("No distance matrices found in the system topology.")
            print("This is common on systems without NUMA or custom distances.")
            print()
            return

        print(f"Found {len(distances)} distance matrix(es):")
        print()

        for i, dist in enumerate(distances):
            print(f"Distance Matrix #{i + 1}:")
            print(f"  Name: {dist.name or '<unnamed>'}")
            print(f"  Kind: {dist.kind.name}")
            print(f"  Objects: {dist.nbobjs}")
            print(f"  Shape: {dist.shape}")

            # Show the object types in this distance matrix
            if dist.objects:
                obj_types = {obj.type.name for obj in dist.objects}
                print(f"  Object Types: {', '.join(obj_types)}")

            print()


def discover_distances_by_type() -> None:
    """Discover distance matrices filtered by object type."""
    print("=" * 60)
    print("Distance Discovery by Object Type")
    print("=" * 60)

    with Topology() as topo:
        # Check for NUMA node distances specifically
        numa_distances = topo.get_distances_by_type(ObjType.HWLOC_OBJ_NUMANODE)

        if numa_distances:
            print(f"Found {len(numa_distances)} NUMA distance matrix(es):")
            for dist in numa_distances:
                print(
                    f"  - {dist.name or 'Unnamed'} "
                    f"({dist.nbobjs} NUMA nodes, kind: {dist.kind.name})"
                )
        else:
            print("No NUMA distance matrices found.")
        print()

        # Check for other object types
        for obj_type in [
            ObjType.HWLOC_OBJ_PACKAGE,
            ObjType.HWLOC_OBJ_CORE,
            ObjType.HWLOC_OBJ_PU,
        ]:
            type_distances = topo.get_distances_by_type(obj_type)
            type_name = obj_type.name.replace("HWLOC_OBJ_", "")

            if type_distances:
                print(f"Found {len(type_distances)} {type_name} distance matrix(es)")
            else:
                print(f"No {type_name} distance matrices found")


def discover_distances_by_kind() -> None:
    """Discover distance matrices filtered by distance kind."""
    print("=" * 60)
    print("Distance Discovery by Kind")
    print("=" * 60)

    with Topology() as topo:
        # Check for different kinds of distances
        distance_kinds = [
            (Kind.HWLOC_DISTANCES_KIND_VALUE_LATENCY, "Latency"),
            (Kind.HWLOC_DISTANCES_KIND_VALUE_BANDWIDTH, "Bandwidth"),
            (Kind.HWLOC_DISTANCES_KIND_VALUE_HOPS, "Hops"),
        ]

        for kind, kind_name in distance_kinds:
            kind_distances = topo.get_distances(kind)

            if kind_distances:
                print(f"{kind_name} distances: {len(kind_distances)} matrix(es)")
                for dist in kind_distances:
                    print(f"  - {dist.name or 'Unnamed'} ({dist.nbobjs} objects)")
            else:
                print(f"{kind_name} distances: None found")
        print()


def inspect_distance_properties() -> None:
    """Inspect detailed properties of discovered distance matrices."""
    print("=" * 60)
    print("Distance Matrix Properties")
    print("=" * 60)

    with Topology() as topo:
        distances = topo.get_distances()

        if not distances:
            print("No distances to inspect.")
            return

        for i, dist in enumerate(distances):
            print(f"Inspecting Distance Matrix #{i + 1}:")
            print(f"  String representation: {str(dist)}")
            print(f"  Repr: {repr(dist)}")
            print(f"  Native handle valid: {dist.native_handle is not None}")
            print(f"  Matrix shape: {dist.shape}")
            print(f"  Total values: {len(dist.values)}")

            # Show first few objects if available
            if dist.objects:
                print(f"  First few objects:")
                for j, obj in enumerate(dist.objects[:3]):
                    print(f"    [{j}] {obj}")
                if len(dist.objects) > 3:
                    print(f"    ... and {len(dist.objects) - 3} more")

            print()


def main() -> None:
    print("Hardware Distance Exploration Example")
    print("====================================")

    # Basic discovery on real system
    discover_basic_distances()

    # Discovery by type
    discover_distances_by_type()

    # Discovery by kind
    discover_distances_by_kind()

    # Inspect properties
    inspect_distance_properties()


if __name__ == "__main__":
    main()
