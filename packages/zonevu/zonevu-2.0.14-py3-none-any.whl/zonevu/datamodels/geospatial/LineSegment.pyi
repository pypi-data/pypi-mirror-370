from .Coordinate import Coordinate as Coordinate
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class LineSegment(DataClassJsonMixin):
    dataclass_json_config = ...
    start: Coordinate
    end: Coordinate
    @property
    def tuples(self) -> list[tuple[float, float]]: ...
    @property
    def x(self) -> list[float]: ...
    @property
    def y(self) -> list[float]: ...
