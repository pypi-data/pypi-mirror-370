from ..geospatial.Coordinate import Coordinate as Coordinate
from ..geospatial.GeoLocation import GeoLocation as GeoLocation
from ..geospatial.Polyline import Polyline as Polyline
from .Blocks import Block as Block
from .Horizon import Horizon as Horizon
from .Pick import Pick as Pick
from dataclasses import dataclass, field

@dataclass
class Throw:
    fault: Fault
    horz: Horizon
    tvd_start: float
    tvd_end: float
    throw_amt: float
    @property
    def line(self) -> Polyline: ...

@dataclass
class Fault:
    pick: Pick
    next_block: Block
    throws: list[Throw] = field(default_factory=list[Throw])
    @property
    def md(self) -> float: ...
    @property
    def location(self) -> GeoLocation: ...
    def xyz(self) -> Coordinate: ...
    @property
    def elevation(self) -> float: ...
    @property
    def trace(self) -> Polyline: ...
