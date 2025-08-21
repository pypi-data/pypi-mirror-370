from ..geospatial.Coordinate import Coordinate as Coordinate
from ..geospatial.Crs import CrsSpec as CrsSpec
from ..geospatial.GeoLocation import GeoLocation as GeoLocation
from ..geospatial.GridGeometry import GridGeometry as GridGeometry
from .SeismicDataset import ZDomainEnum as ZDomainEnum
from dataclasses import dataclass, field
from dataclasses_json import config
from strenum import StrEnum

class SourceTypeEnum(StrEnum):
    UNDEFINED = 'Undefined'
    DYNAMITE = 'Dynamite'
    VIBROSEIS = 'Vibroseis'

class ReceiverTypeEnum(StrEnum):
    UNDEFINED = 'Undefined'
    VERTICAL = 'Vertical'
    MULTICOMPONENT = 'Multicomponent'

class EndianOrderEnum(StrEnum):
    BIG_ENDIAN = 'BigEndian'
    LITTLE_ENDIAN = 'LittleEndian'

class SegyRevisionEnum(StrEnum):
    REV0 = 'Rev0'
    REV1 = 'Rev1'
    REV2 = 'Rev2'

class SampleFormatEnum(StrEnum):
    UNDEFINED = 'Undefined'
    IBM_FLOAT = 'IbmFloat'
    IEEE_FLOAT = 'IeeeFloat'
    INT4 = 'Int4'
    INT2 = 'Int2'
    INT1 = 'Int1'

class TextFormatEnum(StrEnum):
    EBCDIC = 'Ebcdic'
    ASCII = 'Ascii'

class LineOrderEnum(StrEnum):
    INLINE_ORDER = 'InlineOrder'
    CROSSLINE_ORDER = 'CrosslineOrder'
    SLICE_ORDER = 'SliceOrder'
    BRICKED = 'Bricked'
    UNKNOWN = 'Unknown'

class ByteOrderEnum(StrEnum):
    BIG_ENDIAN = 'BigEndian'
    LITTLE_ENDIAN = 'LittleEndian'

class SampleIntervalUnitsEnum(StrEnum):
    UNDEFINED = 'Undefined'
    MILLISECS = 'Millisecs'
    FEET = 'Feet'
    METERS = 'Meters'

class TraceHeaderFieldUsageEnum(StrEnum):
    NOTHING = 'Nothing'
    INLINE = 'Inline'
    CROSSLINE = 'Crossline'
    X = 'X'
    Y = 'Y'
    CDP = 'CDP'
    SHOT = 'Shot'
    TR_SEQUENCE_LINE = 'TrSequenceLine'
    RECEIVER = 'Receiver'

@dataclass
class Geometry2D:
    cdp_interval: float = field(metadata=config(field_name='CDPInterval'))
    start_cdp: int = field(metadata=config(field_name='StartCDP'))
    end_cdp: int = field(metadata=config(field_name='EndCDP'))
    source_interval: float
    start_source: int
    end_source: int
    receiver_interval: float
    start_receiver: int
    end_receiver: int
    trace_interval: float
    start_trace_index: int
    end_trace_index: int
    length: float

@dataclass
class TraceGeometry:
    fixed_length_traces: bool
    num_samples: int
    sample_interval: int
    sample_interval_units: SampleIntervalUnitsEnum
    sample_interval_divisor: int
    sample_format: SampleFormatEnum
    domain: ZDomainEnum

@dataclass
class Datum:
    elevation: float
    replacement_velocity: float | None
    depth_units: str
    type: str | None
    has_value: bool

@dataclass
class Location:
    coordinates_spec: CrsSpec
    coordinates_scalar_override: str | None
    survey_polygon: list[Coordinate]
    lat_long_polygon: list[GeoLocation]
    survey_centerpoint: Coordinate
    lat_long_centerpoint: GeoLocation
    datum: Datum

@dataclass
class HeaderMapping:
    usage: TraceHeaderFieldUsageEnum
    header_definition: str
    header_description: str
    start_byte: int
    end_byte: int

@dataclass
class TraceHeaderInfo:
    header_mappings: list[HeaderMapping]

@dataclass
class IndexFields:
    asset_group: str | None
    business_unit: str | None
    property: str | None
    lease: str | None
    region: str | None
    basin: str | None
    play: str | None
    field: str | None
    prospect: str | None
    well: str | None
    ocean: str | None
    continent: str | None
    country: str
    state_province: str
    county_municipality: str
    owner: str | None
    ownership: str | None
    version: str | None
    fold: str | None
    source_type: SourceTypeEnum
    receiver_type: ReceiverTypeEnum

@dataclass
class FileInfo:
    file_length: int
    num_traces: int
    endian_order: EndianOrderEnum
    line_order: LineOrderEnum
    segy_revision: SegyRevisionEnum
    text_format: TextFormatEnum
    num_extended_text_headers: int

@dataclass
class SeismicRegistration:
    file_info: FileInfo
    survey_name: str
    line_name: str | None
    version_name: str
    survey_type: str
    survey_stage: str
    geometry3d: GridGeometry = field(metadata=config(field_name='Geometry3D'))
    geometry2d: Geometry2D = field(metadata=config(field_name='Geometry2D'))
    trace_geometry: TraceGeometry
    location: Location
    trace_header_info: TraceHeaderInfo
    index_fields: IndexFields
    text_header: str
