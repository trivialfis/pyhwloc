import platform
from typing import TypeGuard

import pytest

from pyhwloc.hwloc.core import ObjPtr


def _skip_if_none(dev_obj: ObjPtr | None) -> TypeGuard[ObjPtr]:
    if dev_obj is None:
        assert platform.system() == "Windows"
        pytest.skip(reason="Windows is not supported")
    return True
