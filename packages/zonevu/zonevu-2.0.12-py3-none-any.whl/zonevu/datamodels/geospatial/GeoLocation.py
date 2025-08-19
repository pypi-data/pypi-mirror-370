#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#

"""
Geographic location (lat, lon) with optional elevation.

Used for positioning data in a geographic CRS.
"""

from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
import math
from typing import Tuple


# @dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GeoLocation(DataClassJsonMixin):
    """Latitude/longitude (and optional elevation) in WGS84."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    latitude: float
    longitude: float

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.longitude, self.latitude

    @property
    def tuple2(self) -> Tuple[float, float]:
        return self.latitude, self.longitude

    @staticmethod
    def error(l1: 'GeoLocation', l2: 'GeoLocation') -> float:
        loc_err_lat = l1.latitude - l2.latitude
        loc_err_lon = l1.longitude - l2.longitude
        e = math.sqrt(math.pow(loc_err_lat, 2) + math.pow(loc_err_lon, 2))
        return e

    def __hash__(self):
        return hash((self.latitude, self.longitude))

    def __eq__(self, other):
        if isinstance(other, GeoLocation):
            return (self.latitude, self.longitude) == (other.latitude, other.longitude)
        return False

    def arc_latitude(self) -> float:
        return self.latitude * math.pi / 180

    def arc_longitude(self) -> float:
        return self.longitude * math.pi / 180

    @staticmethod
    def bearing(s: 'GeoLocation', f: 'GeoLocation') -> float:
        latitude1 = s.arc_latitude()
        latitude2 = f.arc_latitude()
        longitudeDifference = f.arc_longitude() - s.arc_longitude()
        y = math.sin(longitudeDifference) * math.cos(latitude2)
        x = math.cos(latitude1) * math.sin(latitude2) - \
            math.sin(latitude1) * math.cos(latitude2) * math.cos(longitudeDifference)
        bearing = (math.atan2(y, x) * 180 / math.pi + 360) % 360
        return bearing

    @classmethod
    def lower_left_of(cls, l1: 'GeoLocation', l2: 'GeoLocation') -> 'GeoLocation':
        min_latitude = min(l1.latitude, l2.latitude)
        min_longitude = min(l1.longitude, l2.longitude)
        return cls(min_latitude, min_longitude)

    @classmethod
    def upper_right_of(cls, l1: 'GeoLocation', l2: 'GeoLocation') -> 'GeoLocation':
        max_latitude = max(l1.latitude, l2.latitude)
        max_longitude = max(l1.longitude, l2.longitude)
        return cls(max_latitude, max_longitude)

