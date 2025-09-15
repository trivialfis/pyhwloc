"""
Count the number of hops between PCI storage and GPUs
=====================================================

This script counts the number of hops between NVIDIA GPUs and NVME drives and checks
whether the communication needs to go through the host socket.

Please see the `GDS document
<https://docs.nvidia.com/gpudirect-storage/configuration-guide/>`__ for a use case.

"""

from pyhwloc import Topology
from pyhwloc.hwobject import GetTypeDepth, Object, ObjType
from pyhwloc.topology import TypeFilter


def cnt_hops(gpu: Object, nvme: Object) -> tuple[int, bool]:
    """Count the number of hops, and check whether the host socket is required for
    communication.

    """
    gpu_ancestors = []
    while gpu.parent is not None:
        gpu_ancestors.append(gpu.parent)
        gpu = gpu.parent

    nvme_ancestors = []
    while nvme.parent is not None:
        nvme_ancestors.append(nvme.parent)
        nvme = nvme.parent

    # Find the common ancestor
    i, j = -1, -1
    assert gpu_ancestors[i] == nvme_ancestors[j]
    while (
        -i <= len(gpu_ancestors)
        and -j <= len(nvme_ancestors)
        and gpu_ancestors[i] == nvme_ancestors[j]
    ):
        i -= 1
        j -= 1
    assert gpu_ancestors[i + 1] == nvme_ancestors[j + 1]
    # It might be better to check whether this is a PCI bridge instead of checking
    # whether this is a host device.
    crossed = gpu_ancestors[i + 1].is_package or gpu_ancestors[i + 1].is_machine
    return (-(i + 1) + -(j + 1)), crossed


def pprint(table: list[list]) -> None:
    """Print the result as a table."""
    for i in range(len(table)):
        if i == 0:
            print(" " * 7, end="")
        row = table[i]
        for j in range(len(row)):
            if j == 0:
                print(f"{row[j]}", end="")
            else:
                print(f"{row[j]:7},", end="")
        print("\n")


if __name__ == "__main__":
    with Topology.from_this_system(load=False).set_io_types_filter(
        TypeFilter.HWLOC_TYPE_FILTER_KEEP_ALL
    ) as topo:
        # Look for GPUs
        gpus = []
        for obj in topo.iter_objects_by_type(ObjType.HWLOC_OBJ_OS_DEVICE):
            # Check if it's a GPU device
            if obj.is_osdev_gpu:
                assert obj.depth == GetTypeDepth.HWLOC_TYPE_DEPTH_OS_DEVICE
                assert obj.name is not None
                if obj.name.lower().startswith("cuda"):
                    gpus.append(obj)

        # Look for NVME drives
        nvmes = []
        for obj in topo.iter_objects_by_type(ObjType.HWLOC_OBJ_OS_DEVICE):
            if obj.is_osdev_storage:
                assert obj.depth == GetTypeDepth.HWLOC_TYPE_DEPTH_OS_DEVICE
                assert obj.name is not None
                if obj.name.lower().startswith("nvme"):
                    nvmes.append(obj)

        hops_rows: list[list[str | int]] = []
        cross_rows: list[list[str | bool]] = []
        hops_rows.append([dev.name for dev in nvmes])  # type: ignore
        cross_rows.append([dev.name for dev in nvmes])  # type: ignore
        for i, gpu in enumerate(gpus):
            assert gpu.name is not None
            hops_row: list[str | int] = [gpu.name]
            cross_row: list[str | bool] = [gpu.name]
            for j, nvme in enumerate(nvmes):
                hops, cross = cnt_hops(gpu, nvme)
                cross_row.append(cross)
                hops_row.append(hops)
            hops_rows.append(hops_row)
            cross_rows.append(cross_row)

        print("Hops:")
        pprint(hops_rows)
        print("Cross CPU:")
        pprint(cross_rows)
