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
Geographic bounding box.

Defines min/max latitude and longitude extents.
"""

from typing import List, Tuple
from functools import reduce
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from .GeoLocation import GeoLocation
from ...services.Error import ZonevuError


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GeoBox:
    """
    Represents the bounds of a map in geolocations
    """
    lower_left: GeoLocation
    upper_right: GeoLocation

    @classmethod
    def from_locations(cls, locations: List[GeoLocation]):
        if len(locations) == 0:
            raise ZonevuError.local('cannot create a GeoBox from a zero length list of geolocations')

        lower_left = reduce(lambda l1, l2: GeoLocation.lower_left_of(l1, l2), locations)
        upper_right = reduce(lambda l1, l2: GeoLocation.upper_right_of(l1, l2), locations)
        g = cls(lower_left, upper_right)
        return g

    @classmethod
    def from_boxes(cls, b1: 'GeoBox', b2: 'GeoBox') -> 'GeoBox':
        lower_left = GeoLocation.lower_left_of(b1.lower_left, b2.lower_left)
        upper_right = GeoLocation.upper_right_of(b1.upper_right, b2.upper_right)
        return cls(lower_left, upper_right)

    @classmethod
    def from_box_list(cls, boxes: List['GeoBox']) -> 'GeoBox':
        largest_box = reduce(lambda b1, b2: GeoBox.from_boxes(b1, b2), boxes)
        return largest_box

    @property
    def tuple(self) -> Tuple[float, float, float, float]:
        geobox_tuple = self.lower_left.tuple + self.upper_right.tuple
        return geobox_tuple

