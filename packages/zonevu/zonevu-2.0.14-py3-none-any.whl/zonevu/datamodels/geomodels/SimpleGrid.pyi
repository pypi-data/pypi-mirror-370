from ..geospatial.Coordinate import Coordinate as Coordinate
from ..geospatial.Crs import CrsSpec as CrsSpec
from dataclasses import dataclass

@dataclass
class SimpleGrid:
    name: str
    origin: Coordinate
    inclination: float
    dx: float
    dy: float
    num_rows: int
    num_cols: int
    crs: CrsSpec
    z_values: list[float]
