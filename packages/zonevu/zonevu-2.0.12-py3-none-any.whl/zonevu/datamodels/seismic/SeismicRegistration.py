"""
Seismic-to-model registration parameters.

Captures transformations and settings aligning seismic data to model space.
"""

from dataclasses import dataclass, field
from dataclasses_json import config, LetterCase
from strenum import StrEnum
from typing import List, Optional
from dataclasses_json import dataclass_json

from .SeismicDataset import ZDomainEnum
from ..geospatial.Coordinate import Coordinate
from ..geospatial.GeoLocation import GeoLocation
from ..geospatial.GridGeometry import GridGeometry
from ..geospatial.Crs import CrsSpec


class SourceTypeEnum(StrEnum):
    """Seismic source type used to acquire the data."""
    UNDEFINED = "Undefined"
    DYNAMITE = "Dynamite"
    VIBROSEIS = "Vibroseis"

class ReceiverTypeEnum(StrEnum):
    """Receiver type for seismic acquisition."""
    UNDEFINED = "Undefined"
    VERTICAL = "Vertical"
    MULTICOMPONENT = "Multicomponent"

class EndianOrderEnum(StrEnum):
    """Endian order of binary data in seismic files."""
    BIG_ENDIAN = "BigEndian"
    LITTLE_ENDIAN = "LittleEndian"

class SegyRevisionEnum(StrEnum):
    """SEG-Y revision level for the dataset."""
    REV0 = "Rev0"
    REV1 = "Rev1"
    REV2 = "Rev2"

class SampleFormatEnum(StrEnum):  # Use IntEnum since these enums are explicitly tied to integer values
    """Binary sample format (e.g., 32-bit float)."""
    UNDEFINED = "Undefined"
    IBM_FLOAT = "IbmFloat"
    IEEE_FLOAT = "IeeeFloat"
    INT4 = "Int4"
    INT2 = "Int2"
    INT1 = "Int1"

class TextFormatEnum(StrEnum):
    """Encoding used for textual headers (EBCDIC/ASCII)."""
    EBCDIC = "Ebcdic"
    ASCII = "Ascii"

class LineOrderEnum(StrEnum):
    """Ordering of lines in 2D datasets (inline/crossline)."""
    INLINE_ORDER = "InlineOrder"
    CROSSLINE_ORDER = "CrosslineOrder"
    SLICE_ORDER = "SliceOrder"
    BRICKED = "Bricked"
    UNKNOWN = "Unknown"

class ByteOrderEnum(StrEnum):  # Use IntEnum since specific integer values are assigned
    """Byte order for samples and headers."""
    BIG_ENDIAN = "BigEndian"
    LITTLE_ENDIAN = "LittleEndian"

class SampleIntervalUnitsEnum(StrEnum):  # Use IntEnum because of the explicit integer values
    """Units for sampling interval (ms, m, ft)."""
    UNDEFINED = "Undefined"
    MILLISECS = "Millisecs"
    FEET = "Feet"
    METERS = "Meters"

class TraceHeaderFieldUsageEnum(StrEnum):
    """Usage classification for trace header fields."""
    NOTHING = "Nothing"
    INLINE = "Inline"
    CROSSLINE = "Crossline"
    X = "X"
    Y = "Y"
    CDP = "CDP"
    SHOT = "Shot"
    TR_SEQUENCE_LINE = "TrSequenceLine"
    RECEIVER = "Receiver"

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Geometry2D:
    """2D survey geometry parameters (line spacing, shot/receiver config)."""
    cdp_interval: float = field(metadata=config(field_name="CDPInterval"))
    start_cdp: int = field(metadata=config(field_name="StartCDP"))
    end_cdp: int = field(metadata=config(field_name="EndCDP"))
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

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class TraceGeometry:
    """Trace indexing and mapping between units and samples."""
    fixed_length_traces: bool
    num_samples: int
    sample_interval: int
    sample_interval_units: SampleIntervalUnitsEnum
    sample_interval_divisor: int
    sample_format: SampleFormatEnum
    domain: ZDomainEnum

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Datum:
    """Elevation reference and geoid details for depth/time conversion."""
    elevation: float
    replacement_velocity: Optional[float]
    depth_units: str
    type: Optional[str]
    has_value: bool

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Location:
    """Survey location and CRS information."""
    coordinates_spec: CrsSpec   # Defines the coordinate system for the SurveyPolygon and SurveyCenterpoint.
    coordinates_scalar_override: Optional[str]  # If not null, overrides the Coordinates scalar field in the trace header, and scales the trace header x,y.
    survey_polygon: List[Coordinate]  # x,y's in Survey coordinate system.
    lat_long_polygon: List[GeoLocation]  # WGS84 Latitude / Longitudes.
    survey_centerpoint: Coordinate  # Center map location of the survey (as a map point);
    lat_long_centerpoint: GeoLocation  # WGS84 Latitude / Longitudes.
    datum: Datum

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class HeaderMapping:
    """Mapping of SEG-Y trace header fields."""
    usage: TraceHeaderFieldUsageEnum
    header_definition: str
    header_description: str
    start_byte: int
    end_byte: int

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class TraceHeaderInfo:
    """Trace header field definitions and byte offsets."""
    header_mappings: List[HeaderMapping]

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class IndexFields:
    """Fields used to index traces."""
    asset_group: Optional[str]
    business_unit: Optional[str]
    property: Optional[str]
    lease: Optional[str]
    region: Optional[str]
    basin: Optional[str]
    play: Optional[str]
    field: Optional[str]
    prospect: Optional[str]
    well: Optional[str]
    ocean: Optional[str]
    continent: Optional[str]
    country: str
    state_province: str
    county_municipality: str
    owner: Optional[str]
    ownership: Optional[str]
    version: Optional[str]
    fold: Optional[str]
    source_type: SourceTypeEnum
    receiver_type: ReceiverTypeEnum

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class FileInfo:
    """Metadata about the SEG-Y file."""
    file_length: int
    num_traces: int
    endian_order: EndianOrderEnum
    line_order: LineOrderEnum
    segy_revision: SegyRevisionEnum
    text_format: TextFormatEnum
    num_extended_text_headers: int

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class SeismicRegistration:
    """
    Information captured about seismic dataset during the SEGY registration process.
    """
    file_info: FileInfo  # Low-level information about file format.
    survey_name: str  # Survey name for identification purposes.
    line_name: Optional[str]  # Optional line name for identification purposes (2D only)
    version_name: str    # Optional version name for identification purposes (2D only)
    survey_type: str  # 3D or 2D
    survey_stage: str  # Stack or prestack.
    geometry3d: GridGeometry = field(metadata=config(field_name="Geometry3D")) # Volume geometry
    geometry2d: Geometry2D = field(metadata=config(field_name="Geometry2D"))  # Line geometry
    trace_geometry: TraceGeometry  # Seismic trace geometry / info
    location: Location   # Survey location
    trace_header_info: TraceHeaderInfo  # SEGY registration information
    index_fields: IndexFields  # Catalog info
    text_header: str  # SEGY Text header