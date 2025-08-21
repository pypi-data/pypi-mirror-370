from .GriddedData import GriddedData as GriddedData
from dataclasses import dataclass

@dataclass
class Structure(GriddedData):
    formation_id: int = ...
    formation_name: str = ...
