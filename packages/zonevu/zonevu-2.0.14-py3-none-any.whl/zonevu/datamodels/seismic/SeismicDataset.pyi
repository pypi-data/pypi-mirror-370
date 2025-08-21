from ..DataModel import DataModel as DataModel
from dataclasses import dataclass
from strenum import StrEnum

class ZDomainEnum(StrEnum):
    Time = 'Time'
    Depth = 'Depth'
    Velocity = 'Velocity'
    Amplitude = 'Amplitude'

class DatasetType(StrEnum):
    Unknown = 'Unknown'
    Volume = 'Volume'
    Line = 'Line'

@dataclass
class SeismicDataset(DataModel):
    dataset_type: DatasetType = ...
    description: str | None = ...
    vintage: str | None = ...
    domain: ZDomainEnum = ...
    size: int = ...
    segy_filename: str | None = ...
    is_registered: bool = ...
