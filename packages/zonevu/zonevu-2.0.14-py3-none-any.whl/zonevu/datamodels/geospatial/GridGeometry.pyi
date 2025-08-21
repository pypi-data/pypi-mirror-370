from ..geomodels.SimpleGrid import SimpleGrid as SimpleGrid
from .Coordinate import Coordinate as Coordinate
from .Crs import CrsSpec as CrsSpec
from .Enums import DistanceUnitsEnum as DistanceUnitsEnum
from .GridCorner import GridCorner as GridCorner
from dataclasses import dataclass
from numpy import dtype, float32 as float32, float64 as float64, ndarray

@dataclass
class GridAxisInfo:
    start: int
    stop: int
    count: int

@dataclass
class GridInfo:
    inline_range: GridAxisInfo
    crossline_range: GridAxisInfo
    @property
    def num_samples(self) -> int: ...
    def load_z_values(self, float_bytes: bytes) -> ndarray[tuple[int, int], dtype[float]]: ...

@dataclass
class GridValue:
    inline: int
    crossline: int
    c: Coordinate

@dataclass
class GridGeometry:
    corner1: GridCorner
    corner2: GridCorner
    corner3: GridCorner
    corner4: GridCorner
    coordinate_system: CrsSpec
    inclination: float | None = ...
    geo_inclination: float | None = ...
    inline_bin_interval: float | None = ...
    crossline_bin_interval: float | None = ...
    area: float | None = ...
    @property
    def inline_start(self) -> int: ...
    @property
    def inline_stop(self) -> int: ...
    @property
    def crossline_start(self) -> int: ...
    @property
    def crossline_stop(self) -> int: ...
    @property
    def num_inlines(self) -> int: ...
    @property
    def num_crosslines(self) -> int: ...
    @property
    def grid_info(self) -> GridInfo: ...
    @classmethod
    def from_simple_grid(cls, grid: SimpleGrid) -> GridGeometry: ...
    def get_xy(self, inline: int, crossline: int) -> Coordinate | None: ...
    def get_xyz(self, inline: int, crossline: int, z_values: ndarray[tuple[int, int], dtype[float]]) -> Coordinate: ...
