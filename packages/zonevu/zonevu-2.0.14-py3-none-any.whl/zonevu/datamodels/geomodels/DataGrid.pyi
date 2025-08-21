from .GriddedData import GriddedData as GriddedData
from dataclasses import dataclass
from strenum import StrEnum

class GridUsageEnum(StrEnum):
    Undefined = 'Undefined'
    Structural = 'Structural'
    Isopach = 'Isopach'
    Attribute = 'Attribute'

@dataclass
class DataGrid(GriddedData):
    usage: GridUsageEnum | None = ...
