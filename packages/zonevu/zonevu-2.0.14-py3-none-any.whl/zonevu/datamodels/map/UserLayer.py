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
User-defined map layer.

Holds metadata and GeoJSON content for layers displayed in ZoneVu maps.
"""

from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from ..DataModel import DataModel
from strenum import StrEnum
from ..geospatial.GeoBox import GeoBox
import pygeojson as geo
from ...services.Error import ZonevuError


class LayerTypeEnum(StrEnum):
    """Categorization for user layers (lease, hardline, pad)."""
    Unspecified = "Unspecified"
    Lease = "Lease"
    Hardline = "Hardline"
    Pad = "Pad"


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class UserLayer(DataModel):
    """
    A user provided map layer.
    """
    #: Project this map layer is associated with
    project_id: int = -1
    #: Optional description of map layer
    description: Optional[str] = None
    #: Type of map layer
    layer_type: LayerTypeEnum = LayerTypeEnum.Unspecified
    #: Map layer data as a geojson string
    geo_json: Optional[str] = None
    #: Map box that encompasses the map layer
    extents: Optional[GeoBox] = None

    @property
    def geojson(self) -> Optional[geo.FeatureCollection]:
        """
        Courtesy function to convert geojson string into a valid geojson object
        :return:
        """
        fc = geo.loads(self.geo_json or '')
        if fc.bbox is None:
            if self.extents is None:
                return None
            upper_right = self.extents.upper_right
            lower_left = self.extents.lower_left
            minx = min(upper_right.longitude, lower_left.longitude)
            maxx = max(upper_right.longitude, lower_left.longitude)
            miny = min(upper_right.latitude, lower_left.latitude)
            maxy = max(upper_right.latitude, lower_left.latitude)
            bbox = (minx, miny, maxx, maxy)
            features2 = geo.FeatureCollection(fc.features, bbox, fc.type, fc.extra_attributes)  # type: ignore
            return features2
        else:
            if isinstance(fc, geo.FeatureCollection):
                return fc
            raise ZonevuError.local('Unexpected geojson data structure encountered')

