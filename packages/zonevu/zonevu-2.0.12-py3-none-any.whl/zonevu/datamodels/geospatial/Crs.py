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
Coordinate reference system (CRS) definitions.

Includes CRS specs and entries used for coordinate transforms.
"""

from typing import Optional
from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
from .Enums import DistanceUnitsEnum


# Projected coordinate system specification
# @dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CrsSpec(DataClassJsonMixin):
    """Projected CRS specification including units and linearization."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    """
    Used to specify a projected coordinate system
    The EPSG code takes preference if both are specified.
    The Units data member if provided overrides the default units of the specified coordinate system
    """
    epsg_code: Optional[int] = None
    projection: Optional[str] = None       # DotSpatial string for projection
    zone: Optional[str] = None              # DotSpatial string for zone
    units: Optional[DistanceUnitsEnum] = DistanceUnitsEnum.Undefined         # Distance units override.

    @classmethod
    def from_epsg_code(cls, code: int, units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined) -> 'CrsSpec':
        return cls(code, None, None, units)

    @classmethod
    def from_names(cls, projection: str, zone: str, units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined) -> 'CrsSpec':
        return cls(None, projection, zone, units)

    def to_string(self) -> str:
        has_epsg = self.epsg_code is not None
        if has_epsg:
            return 'CRS (EPSG=%s, UNITS=%s)' % (self.epsg_code, self.units)
        else:
            return 'CRS (PROJ=%s, ZONE=%s, UNITS=%s)' % (self.projection, self.zone, self.units)


# @dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CrsEntry(DataClassJsonMixin):
    """CRS catalog entry with identifier and display name."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    id: str        # DotSpatial string for projection
    name: str              # DotSpatial string for zone


