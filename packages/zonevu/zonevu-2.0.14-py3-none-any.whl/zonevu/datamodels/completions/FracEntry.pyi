from ..DataModel import DataModel as DataModel
from dataclasses import dataclass
from strenum import StrEnum

class FracTypeEnum(StrEnum):
    Plan = 'Plan'
    Actual = 'Actual'

@dataclass
class FracEntry(DataModel):
    description: str | None = ...
    frac_type: FracTypeEnum = ...
