"""
Segment of a mapped fault trace.

Represents a continuous section of a seismic fault defined by points.
"""

from dataclasses import dataclass, field
from typing import List
from dataclasses_json import dataclass_json
from .FaultPoint import FaultPoint
from ..DataModel import DataModel

@dataclass_json
@dataclass
class FaultSegment(DataModel):
    """
    Represents a fault segment interpreted on a seismic survey in the ZoneVu application.
    """

    # List of points that comprise the fault segment
    points: List[FaultPoint] = field(default_factory=list[FaultPoint])