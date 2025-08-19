"""
Line segment geometry.

Helper for operations on 2D segments.
"""

from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
from .Coordinate import Coordinate
from typing import List, Tuple


@dataclass
class LineSegment(DataClassJsonMixin):
    """2D line segment defined by start and end coordinates with helpers."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    start: Coordinate
    end: Coordinate

    @property
    def tuples(self) -> List[Tuple[float, float]]:
        return [self.start.tuple, self.end.tuple]

    @property
    def x(self) -> List[float]:
        return [self.start.x, self.end.x]

    @property
    def y(self) -> List[float]:
        return [self.start.y, self.end.y]
