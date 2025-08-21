from .Enums import DistanceUnitsEnum as DistanceUnitsEnum
from abc import ABC
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from strenum import StrEnum
from typing import ClassVar

class StateCode(StrEnum):
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
    NAD27 = 'Nad1927'
    NAD83 = 'Nad1983'
    WGS1984 = 'Wgs1984'

class StateZone(StrEnum):
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
    N = 'N'
    S = 'S'

@dataclass
class CrsDescriptor(DataClassJsonMixin, ABC):
    crs_type: str = field(init=False)

@dataclass
class WGS84CrsDescriptor(CrsDescriptor):
    CRSType: ClassVar[str] = ...
    crs_type = ...
    def __post_init__(self) -> None: ...

@dataclass
class ProjectedCrsDescriptor(CrsDescriptor):
    units: DistanceUnitsEnum
    datum: Datum

@dataclass
class WebMercatorDescriptor(ProjectedCrsDescriptor):
    CRSType: ClassVar[str] = ...
    crs_type = ...
    units = ...
    datum = ...
    def __post_init__(self) -> None: ...

@dataclass
class UtmDescriptor(ProjectedCrsDescriptor):
    zone: int
    hemisphere: UtmHemisphere
    CRSType: ClassVar[str] = ...
    crs_type = ...
    def __post_init__(self) -> None: ...
    def get_projection_str(self) -> str: ...
    def get_zone_str(self) -> str: ...

@dataclass
class StatePlaneDescriptor(ProjectedCrsDescriptor):
    code: StateCode
    zone: StateZone | int | None = ...
    CRSType: ClassVar[str] = ...
    crs_type = ...
    def __post_init__(self) -> None: ...

def deserialize_crs(json_str: str) -> CrsDescriptor: ...
