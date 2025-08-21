from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from strenum import StrEnum
from typing import TypeVar

class DataObjectTypeEnum(StrEnum):
    SeismicSurvey = 'SeismicSurvey'
    Well = 'Well'
    Project = 'Project'
    Geomodel = 'Geomodel'
    StratColumn = 'StratColumn'
    Unknown = 'Unknown'

class ChangeAgentEnum(StrEnum):
    Unknown = 'Unknown'
    GuiCreate = 'GuiCreate'
    GuiImport = 'GuiImport'
    GuiBulkImport = 'GuiBulkImport'
    WebApi = 'WebApi'

class WellElevationUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    FeetUS = 'FeetUS'
T = TypeVar('T', bound='DataModel')

@dataclass
class DataModel(DataClassJsonMixin):
    dataclass_json_config = ...
    id: int = ...
    row_version: str | None = ...
    name: str | None = ...
    def merge_from(self, source: DataModel): ...
    def copy_ids_from(self, source: DataModel): ...
    @staticmethod
    def merge_lists(dst_list: list[T], src_list: list[T]): ...
