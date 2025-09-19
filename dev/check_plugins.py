import pyhwloc

info = pyhwloc.hwloc.lib.libinfo()
print(info)

assert "hwloc_cuda.so" in info["plugins"]
assert "hwloc_nvml.so" in info["plugins"]
assert "hwloc_pci.so" in info["plugins"]
