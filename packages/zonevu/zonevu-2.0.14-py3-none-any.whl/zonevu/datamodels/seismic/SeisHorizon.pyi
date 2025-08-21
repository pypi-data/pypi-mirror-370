from ..geomodels.GriddedData import GriddedData as GriddedData
from ..geospatial.Coordinate import Coordinate as Coordinate
from dataclasses import dataclass
from strenum import StrEnum

class GridUsageEnum(StrEnum):
    Undefined = 'Undefined'
    Structural = 'Structural'
    Isopach = 'Isopach'
    Attribute = 'Attribute'

@dataclass
class SeisHorizon(GriddedData):
    symbol: str | None = ...
    thickness: int | None = ...
    color: str | None = ...
    interpreter: str | None = ...
