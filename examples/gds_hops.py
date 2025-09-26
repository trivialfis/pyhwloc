# Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: BSD-3-Clause
"""
Count the number of hops between PCI storage and GPUs
=====================================================

This script counts the number of hops between NVIDIA GPUs and NVME drives and checks
whether the communication needs to go through the host socket.

Please see the `GDS document
<https://docs.nvidia.com/gpudirect-storage/configuration-guide/>`__ for a use case.

"""

from typing import TypeGuard, cast

from pyhwloc import Topology
from pyhwloc.hwobject import GetTypeDepth, Object, ObjType, OsDevice
from pyhwloc.topology import TypeFilter


def is_osdev_gpu(obj: Object) -> TypeGuard[OsDevice]:
    return isinstance(obj, OsDevice) and obj.is_gpu()


def is_osdev_storage(obj: Object) -> TypeGuard[OsDevice]:
    return isinstance(obj, OsDevice) and obj.is_storage()


def cnt_hops(gpu: Object, nvme: Object) -> tuple[int, bool]:
    """Count the number of hops, and check whether the host socket is required for
    communication.

    """
    print("GPU:", gpu, "<-> NVME:", nvme)
    gpu_ancestors = []
    while gpu.parent is not None:
        gpu_ancestors.append(gpu.parent)
        gpu = gpu.parent

    nvme_ancestors = []
    while nvme.parent is not None:
        nvme_ancestors.append(nvme.parent)
        nvme = nvme.parent

    # Find the common ancestor
    gpu_ancestors = list(reversed(gpu_ancestors))
    nvme_ancestors = list(reversed(nvme_ancestors))
    i, j = 0, 0
    assert gpu_ancestors[i] == nvme_ancestors[j]  # must have the same root
    while (
        i < len(gpu_ancestors)
        and j < len(nvme_ancestors)
        and gpu_ancestors[i] == nvme_ancestors[j]
    ):
        i += 1
        j += 1
    assert i >= 1 and j >= 1, (i, j)
    # It might be better to check whether this is a PCI bridge instead of checking
    # whether this is a host device.
    crossed = gpu_ancestors[i - 1].is_package() or gpu_ancestors[i - 1].is_machine()
    # Assuming GPU is an OS device attached to a PCI device. There are GPUs that are
    # connected through nvlink-C2C, which does not use PCI.
    assert gpu_ancestors[-1].is_pci_device() and nvme_ancestors[-1].is_pci_device()
    gpu_path = []
    for k in range(i - 1, len(gpu_ancestors)):
        gpu_path.append(str(gpu_ancestors[k]))
    print("- GPU path:", " -> ".join(gpu_path[::-1]))
    nvme_path = []

    for k in range(j - 1, len(nvme_ancestors)):
        nvme_path.append(str(nvme_ancestors[k]))
    print("- NVME path:", " -> ".join(nvme_path[::-1]))
    print()

    # +1 for the common ancestor. -1 for removing the PCI device. OS device is a
    # software device, which is "attached" to the PCI device. But they are the same
    # thing.
    n_hops = (len(gpu_ancestors) - i - 1) + (len(nvme_ancestors) - j - 1) + 1
    return n_hops, crossed


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
        print()


if __name__ == "__main__":
    with Topology.from_this_system().set_io_types_filter(TypeFilter.KEEP_ALL) as topo:
        # Look for GPUs
        gpus = []
        for obj in topo.iter_objs_by_type(ObjType.OS_DEVICE):
            # Check if it's a GPU device
            if is_osdev_gpu(obj):
                assert obj.depth == GetTypeDepth.OS_DEVICE
                assert obj.name is not None
                if obj.name.lower().startswith("cuda"):
                    gpus.append(obj)

        # Look for NVME drives
        nvmes = []
        for obj in topo.iter_objs_by_type(ObjType.OS_DEVICE):
            if is_osdev_storage(obj):
                assert obj.depth == GetTypeDepth.OS_DEVICE
                assert obj.name is not None
                if obj.name.lower().startswith("nvme"):
                    nvmes.append(obj)

        hops_rows: list[list[str | int]] = []
        cross_rows: list[list[str | bool]] = []
        hops_rows.append([cast(str, dev.name) for dev in nvmes])
        cross_rows.append([cast(str, dev.name) for dev in nvmes])
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
