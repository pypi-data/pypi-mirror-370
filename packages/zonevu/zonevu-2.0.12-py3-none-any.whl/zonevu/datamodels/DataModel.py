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
Base datamodel mixins and enums.

Provides common base classes and shared enums for ZoneVu SDK objects,
including serialization helpers and change tracking.
"""

from typing import Optional, TypeVar, List
from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
from strenum import StrEnum


class DataObjectTypeEnum(StrEnum):
    """Enumeration of primary ZoneVu object types (Well, Project, Geomodel, etc.)."""
    SeismicSurvey = 'SeismicSurvey'
    Well = 'Well'
    Project = 'Project'
    Geomodel = 'Geomodel'
    StratColumn = 'StratColumn'
    Unknown = 'Unknown'


class ChangeAgentEnum(StrEnum):
    """Identifies the actor responsible for a change (user, system, migration)."""
    Unknown = 'Unknown'
    GuiCreate = 'GuiCreate'
    GuiImport = 'GuiImport'
    GuiBulkImport = 'GuiBulkImport'
    WebApi = 'WebApi'


class WellElevationUnitsEnum(StrEnum):
    """Elevation units for wells (feet/meters) used for KB/DF/GL references."""
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    FeetUS = 'FeetUS'


T = TypeVar("T", bound='DataModel')


@dataclass
class DataModel(DataClassJsonMixin):
    """Base mixin for SDK dataclasses providing JSON (de)serialization support."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    #: System id of this data object
    id: int = -1
    #: Row version for tracking changes on this data object
    row_version: Optional[str] = None
    #: Data object name
    name: Optional[str] = None

    def merge_from(self, source: 'DataModel'):
        self.__dict__.update(source.__dict__)

    def copy_ids_from(self, source: 'DataModel'):
        self.id = source.id

    @staticmethod
    def merge_lists(dst_list: List[T], src_list: List[T]):
        for (dst, src) in zip(dst_list, src_list):
            if dst is not None and src is not None:
                dst.copy_ids_from(src)



