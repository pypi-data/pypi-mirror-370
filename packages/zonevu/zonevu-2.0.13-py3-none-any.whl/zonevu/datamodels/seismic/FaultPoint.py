"""
Point sampled along a fault trace.

Stores position and optional attributes for a point on a seismic fault.
"""

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from ..geospatial.GeoLocation import GeoLocation
from dataclasses_json import LetterCase, config, DataClassJsonMixin

@dataclass_json
@dataclass
class FaultPoint(DataClassJsonMixin):
    """Point on a seismic fault with geolocation and interpreted time/depth."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]

    # Geolocation of the fault point in WGS84 latitude and longitude
    location: GeoLocation

    # The interpreted time in positive milliseconds below survey datum.
    # Note: float.NegativeInfinity means null.
    time: float

    # The interpreted depth in elevation (+ above sea level, - below).
    # Note: float.NegativeInfinity means null.
    depth: float