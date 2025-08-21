from ...services.Error import ZonevuError as ZonevuError
from .GeoLocation import GeoLocation as GeoLocation
from dataclasses import dataclass

@dataclass
class GeoBox:
    lower_left: GeoLocation
    upper_right: GeoLocation
    @classmethod
    def from_locations(cls, locations: list[GeoLocation]): ...
    @classmethod
    def from_boxes(cls, b1: GeoBox, b2: GeoBox) -> GeoBox: ...
    @classmethod
    def from_box_list(cls, boxes: list['GeoBox']) -> GeoBox: ...
    @property
    def tuple(self) -> tuple[float, float, float, float]: ...
