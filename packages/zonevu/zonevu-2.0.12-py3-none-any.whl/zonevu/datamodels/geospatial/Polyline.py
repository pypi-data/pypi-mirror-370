"""
Polyline geometry.

Ordered list of vertices representing a path.
"""

from dataclasses import dataclass, field
from dataclasses_json import LetterCase, config, DataClassJsonMixin
from .Coordinate import Coordinate
from typing import List, Tuple


@dataclass
class Polyline(DataClassJsonMixin):
    """Ordered sequence of coordinates representing a path."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    points: List[Coordinate] = field(default_factory=list[Coordinate])

    @property
    def tuples(self) -> List[Tuple[float, float]]:
        return [p.tuple for p in self.points]

    @property
    def x(self) -> List[float]:
        return [p.x for p in self.points]

    @property
    def y(self) -> List[float]:
        return [p.y for p in self.points]

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        min_x = min((p.x for p in self.points))
        max_x = max((p.x for p in self.points))
        min_y = min((p.y for p in self.points))
        max_y = max((p.y for p in self.points))
        return min_x, min_y, max_x, max_y