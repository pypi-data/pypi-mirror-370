#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.

"""
ZoneVu Python SDK
=================

This is the main package for the ZoneVu Python SDK.
The primary entry point for users is the :class:`~zonevu.Zonevu` class.
"""

from .Zonevu import Zonevu
from .datamodels.geospatial.Enums import UnitsSystemEnum, DistanceUnitsEnum, DepthUnitsEnum
from .services.EndPoint import EndPoint
from .services.Error import ZonevuError

# --- Back-compat shim: support older import styles ---

# Ensure top-level Zonevu exists in __all__
try:
    __all__ = tuple(sorted(set(globals().get("__all__", [])) | {"Zonevu"}))
except Exception:
    pass

# 1) Allow "from zonevu import Zonevu" then "Zonevu.Zonevu"
try:
    if not hasattr(Zonevu, "Zonevu"):
        setattr(Zonevu, "Zonevu", Zonevu)
except Exception:
    # If Zonevu isn't bound yet or not a class, ignore
    pass

# 2) Provide virtual submodule "zonevu.Zonevu" exposing the class Zonevu
#    This enables "import zonevu.Zonevu as Z" or "from zonevu.Zonevu import Zonevu"
import sys
import types

_submod_name = __name__ + ".Zonevu"
if _submod_name not in sys.modules:
    _m = types.ModuleType(_submod_name, "Back-compat shim for zonevu.Zonevu")
    # expose the class on the virtual submodule
    _m.Zonevu = Zonevu  # type: ignore[name-defined]
    sys.modules[_submod_name] = _m