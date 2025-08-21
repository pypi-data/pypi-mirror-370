from ..DataModel import DataModel as DataModel
from .FaultPoint import FaultPoint as FaultPoint
from dataclasses import dataclass, field

@dataclass
class FaultSegment(DataModel):
    points: list[FaultPoint] = field(default_factory=list[FaultPoint])
