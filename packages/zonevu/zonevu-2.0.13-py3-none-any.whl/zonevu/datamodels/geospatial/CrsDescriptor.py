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

"""
Compact CRS descriptor types.

State Plane and UTM descriptors used to derive full CRS specs.
"""

from strenum import StrEnum
from typing import Union, Dict, Type, ClassVar, Optional
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from .Enums import DistanceUnitsEnum
from abc import ABC
import json


class StateCode(StrEnum):
    """Two-letter state/province codes used in State Plane descriptors."""
    AL = 'Alabama'
    AK = 'Alaska'
    AZ = 'Arizona'
    AR = 'Arkansas'
    CA = 'California'
    CO = 'Colorado'
    CT = 'Connecticut'
    DE = 'Delaware'
    FL = 'Florida'
    GA = 'Georgia'
    HI = 'Hawaii'
    ID = 'Idaho'
    IL = 'Illinois'
    IN = 'Indiana'
    IA = 'Iowa'
    KS = 'Kansas'
    KY = 'Kentucky'
    LA = 'Louisiana'
    ME = 'Maine'
    MD = 'Maryland'
    MA = 'Massachusetts'
    MI = 'Michigan'
    MN = 'Minnesota'
    MS = 'Mississippi'
    MO = 'Missouri'
    MT = 'Montana'
    NE = 'Nebraska'
    NV = 'Nevada'
    NH = 'New Hampshire'
    NJ = 'New Jersey'
    NM = 'New Mexico'
    NY = 'New York'
    NC = 'North Carolina'
    ND = 'North Dakota'
    OH = 'Ohio'
    OK = 'Oklahoma'
    OR = 'Oregon'
    PA = 'Pennsylvania'
    RI = 'Rhode Island'
    SC = 'South Carolina'
    SD = 'South Dakota'
    TN = 'Tennessee'
    TX = 'Texas'
    UT = 'Utah'
    VT = 'Vermont'
    VA = 'Virginia'
    WA = 'Washington'
    WV = 'West Virginia'
    WI = 'Wisconsin'
    WY = 'Wyoming'


class Datum(StrEnum):
    """Geodetic datum used for CRS derivation (e.g., WGS84, NAD83)."""
    NAD27 = 'Nad1927'
    NAD83 = 'Nad1983'
    WGS1984 = 'Wgs1984'


class StateZone(StrEnum):
    """Zone identifiers within a State Plane system."""
    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'
    Central = 'Central'
    SouthCentral = 'SouthCentral'
    EastCentral = 'EastCentral'
    WestCentral = 'WestCentral'
    NorthCentral = 'NorthCentral'
    I = 'I'
    II = 'II'
    III = 'III'
    IV = 'IV'
    V = 'V'
    VI = 'VI'
    VII = 'VII'


class UtmHemisphere(StrEnum):
    """UTM hemisphere selector (North/South)."""
    N = 'N'
    S = 'S'

@dataclass
class CrsDescriptor(DataClassJsonMixin, ABC):
    """Abstract base for compact CRS descriptors that expand to CrsSpec."""
    crs_type: str = field(init=False)

@dataclass
class WGS84CrsDescriptor(CrsDescriptor):
    """Descriptor for WGS84 latitude/longitude coordinate system."""
    CRSType: ClassVar[str] = "wgs84"

    def __post_init__(self):
        self.crs_type = "wgs84"

    def __str__(self):
        return "WGS 84 (EPSG:4326) – Lat/Lon in degrees"

@dataclass
class ProjectedCrsDescriptor(CrsDescriptor):
    """Base for projected CRS descriptors with units and EPSG-like fields."""
    units: DistanceUnitsEnum
    datum: Datum

@dataclass
class WebMercatorDescriptor(ProjectedCrsDescriptor):
    CRSType: ClassVar[str] = "webmercator"

    def __post_init__(self):
        self.crs_type = "webmercator"
        self.units = DistanceUnitsEnum.Meters
        self.datum = Datum.WGS1984

    def __str__(self):
        return "WGS 84 / WebMercator (EPSG:3857) – Lat/Lon in web mercator projected x,y's"

@dataclass
class UtmDescriptor(ProjectedCrsDescriptor):
    """Universal Transverse Mercator descriptor (zone and hemisphere)."""
    zone: int
    hemisphere: UtmHemisphere
    CRSType: ClassVar[str] = "utm"

    def __post_init__(self):
        self.crs_type = "utm"

    def get_projection_str(self) -> str:
         return str('Utm%s' % self.datum)
    
    def get_zone_str(self) -> str:
        zone_base = '%s%s' % (self.zone, self.hemisphere)
        return str('%sUtmZone%s' % (self.datum, zone_base)).lower()


@dataclass
class StatePlaneDescriptor(ProjectedCrsDescriptor):
    """State Plane CRS descriptor (state code, zone, datum, units)."""
    code: StateCode
    zone: Optional[Union[StateZone, int]] = None
    CRSType: ClassVar[str] = "stateplane"

    def __post_init__(self):
        self.crs_type = "stateplane"

_CRS_CLASS_MAP: Dict[str, Type[CrsDescriptor]] = {
    WGS84CrsDescriptor.CRSType: WGS84CrsDescriptor,
    UtmDescriptor.CRSType: UtmDescriptor,
    StatePlaneDescriptor.CRSType: StatePlaneDescriptor,
    WebMercatorDescriptor.CRSType: WebMercatorDescriptor
}

def deserialize_crs(json_str: str) -> CrsDescriptor:
    data = json.loads(json_str)
    crs_type = data.get("crs_type")
    cls = _CRS_CLASS_MAP.get(crs_type)
    if not cls:
        raise ValueError(f"Unknown crs_type in JSON: {crs_type}")
    return cls.from_dict(data)
