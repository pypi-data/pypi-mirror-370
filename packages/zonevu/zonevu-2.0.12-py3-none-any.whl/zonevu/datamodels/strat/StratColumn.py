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
Stratigraphic column.

A sequence of formations used to define the stratigraphy.
"""

from typing import Optional, ClassVar
from dataclasses import dataclass, field
from ...datamodels.DataModel import DataModel
from ...datamodels.PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from ..Company import Division
from .Formation import Formation


@dataclass
class StratColumn(PrimaryDataObject):
    """Stratigraphic column composed of named formations for an area."""
    description: Optional[str] = None
    division: Optional[Division] = None
    basin: Optional[str] = None
    formations: list[Formation] = field(default_factory=list[Formation])

    archive_dir_name: ClassVar[str] = 'stratcolumns'
    archive_json_filename: ClassVar[str] = 'stratcolumn.json'

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, StratColumn):
            DataModel.merge_lists(self.formations, source.formations)

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.StratColumn

    @property
    def full_name(self) -> str:
        return self.name


@dataclass
class StratColumnEntry(DataModel):
    """Listing record for a stratigraphic column with minimal info."""
    # Represents a ZoneVu Strat Column catalog entry Object (lightweight)
    division: Optional[Division] = None
    description: Optional[str] = None
    row_version: Optional[str] = None
