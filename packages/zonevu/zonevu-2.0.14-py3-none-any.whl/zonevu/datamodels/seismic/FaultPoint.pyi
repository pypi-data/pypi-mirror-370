from ..geospatial.GeoLocation import GeoLocation as GeoLocation
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class FaultPoint(DataClassJsonMixin):
    dataclass_json_config = ...
    location: GeoLocation
    time: float
    depth: float
