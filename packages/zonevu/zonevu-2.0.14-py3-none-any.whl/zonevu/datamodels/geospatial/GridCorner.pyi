from .Coordinate import Coordinate as Coordinate
from .GeoLocation import GeoLocation as GeoLocation
from dataclasses import dataclass

@dataclass
class GridCorner:
    inline: int
    crossline: int
    p: Coordinate
    lat_long: GeoLocation | None = ...
