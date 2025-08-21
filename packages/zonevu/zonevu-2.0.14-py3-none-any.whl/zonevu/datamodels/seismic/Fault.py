"""
Seismic fault models.

Defines a fault and its catalog entry composed of one or more segments.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from dataclasses_json import dataclass_json
from .FaultSegment import FaultSegment
from ..DataModel import DataModel

@dataclass_json
@dataclass
class Fault(DataModel):
    """
    Represents a fault interpreted on a seismic survey in the ZoneVu application.
    """

    # Shorthand symbol of the fault
    symbol: Optional[str] = None

    # Thickness in CSS units of the fault
    thickness: Optional[int] = None

    # Color of the fault. A CSS web color name.
    # Can be a hex value -- detect difference by seeing if it starts with 0x.
    color: Optional[str] = None

    # Name of fault interpreter
    interpreter: Optional[str] = None

    # List of fault segments.
    segments: List[FaultSegment] = field(default_factory=list[FaultSegment])


@dataclass_json
@dataclass
class FaultEntry(DataModel):
    """
    Catalog entry for a fault interpreted on a seismic survey in the ZoneVu application.
    """
