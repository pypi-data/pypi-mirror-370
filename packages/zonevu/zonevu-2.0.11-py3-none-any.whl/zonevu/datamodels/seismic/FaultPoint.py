from dataclasses import dataclass
from dataclasses_json import dataclass_json
from ..geospatial.GeoLocation import GeoLocation
from dataclasses_json import LetterCase, config, DataClassJsonMixin

@dataclass_json
@dataclass
class FaultPoint(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    """
    Represents an interpreted point on a fault segment in the ZoneVu application
    """

    # Geolocation of the fault point in WGS84 latitude and longitude
    location: GeoLocation

    # The interpreted time in positive milliseconds below survey datum.
    # Note: float.NegativeInfinity means null.
    time: float

    # The interpreted depth in elevation (+ above sea level, - below).
    # Note: float.NegativeInfinity means null.
    depth: float
