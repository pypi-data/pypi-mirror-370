import pygeojson as geo
from ...services.Error import ZonevuError as ZonevuError
from ..DataModel import DataModel as DataModel
from ..geospatial.GeoBox import GeoBox as GeoBox
from dataclasses import dataclass
from strenum import StrEnum

class LayerTypeEnum(StrEnum):
    Unspecified = 'Unspecified'
    Lease = 'Lease'
    Hardline = 'Hardline'
    Pad = 'Pad'

@dataclass
class UserLayer(DataModel):
    project_id: int = ...
    description: str | None = ...
    layer_type: LayerTypeEnum = ...
    geo_json: str | None = ...
    extents: GeoBox | None = ...
    @property
    def geojson(self) -> geo.FeatureCollection | None: ...
