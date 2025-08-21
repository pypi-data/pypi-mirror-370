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
Seismic survey geometry and parameters.

Describes the spatial extent, sampling, and coordinate system for a survey.
"""

from typing import Optional, ClassVar, List
from dataclasses import dataclass, field
from datetime import datetime
from .Fault import FaultEntry
from .SeisHorizon import SeisHorizon
from ..DataModel import DataModel
from ..Company import Division
from ..PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from ..Document import Document
from strenum import StrEnum
from ...datamodels.Helpers import MakeIsodateOptionalField
from .SeismicDataset import SeismicDataset

class SurveyTypeEnum(StrEnum):
    """Seismic survey acquisition type (2D, 3D)."""
    Unknown = "Unknown"
    Type_2D = "Type_2D"
    Type_3D = "Type_3D"

@dataclass
class SeismicSurvey(PrimaryDataObject):
    """
    Represents a ZoneVu seismic survey which can encompass multiple seismic datasets
    """
    # PrimaryDataObject has name, id, and row_version fields
    # Business Unit
    division: Optional[Division] = None
    number: Optional[str] = None
    type: SurveyTypeEnum = SurveyTypeEnum.Unknown
    description: Optional[str] = None
    # How many volumes or lines
    num_datasets: int = 0
    # List of documents in seismic folder
    documents: List[Document] = field(default_factory=list[Document])
    # List of seismic datasets in this survey (Volumes or Lines)
    seismic_datasets: List[SeismicDataset] = field(default_factory=list[SeismicDataset])  # 3D seismic volumes in this survey.
    # List of faults interpreted on this survey
    faults: List[FaultEntry] = field(default_factory=list[FaultEntry])
    # List of horizons interpreted on this survey
    horizons: List[SeisHorizon] = field(default_factory=list[SeisHorizon])

    # Catalog fields
    fold: Optional[int] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    year_recorded: Optional[int] = None
    day_recorded: Optional[int] = None
    contractor: Optional[int] = None
    contractee: Optional[int] = None
    environment: Optional[str] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    geologic_region: Optional[str] = None
    date_acquired: Optional[datetime] = MakeIsodateOptionalField()
    contractor_name: Optional[str] = None
    energy_source: Optional[str] = None
    dynamite_charge_size: Optional[str] = None
    dynamite_depth: Optional[str] = None
    vibroseis_num_vibrators: Optional[int] = None
    vibroseis_sweep: Optional[str] = None
    vibroseis_sweep_length: Optional[str] = None
    airgun_num_airguns: Optional[int] = None
    airgun_pressure: Optional[str] = None
    recording_equipment: Optional[str] = None
    num_channels: Optional[int] = None
    surveyed_by: Optional[str] = None
    processed_by: Optional[str] = None
    date_processed: Optional[datetime] = MakeIsodateOptionalField()
    processing_remarks: Optional[str] = None
    original_owner: Optional[str] = None
    purchase_afe: Optional[str] = None
    purchase_date: Optional[datetime] = MakeIsodateOptionalField()
    purchased_from: Optional[str] = None
    price: Optional[float] = None  # Price per sq. mile or sq. km
    total_cost: Optional[float] = None
    purchase_reference: Optional[str] = None
    original_media: Optional[str] = None
    date_copied: Optional[datetime] = MakeIsodateOptionalField()
    date_sent: Optional[datetime] = MakeIsodateOptionalField()
    media_remarks: Optional[str] = None

    archive_dir_name: ClassVar[str] = 'seismicsurveys'
    archive_json_filename: ClassVar[str] = 'seismicsurvey.json'

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.SeismicSurvey


@dataclass
class SeismicSurveyEntry(DataModel):
    """Listing record for a seismic survey with minimal fields."""
    # Represents a ZoneVu seismic survey catalog entry Object (lightweight)
    division: Optional[Division] = None
    number: Optional[str] = None
    type: SurveyTypeEnum = SurveyTypeEnum.Unknown
    description: Optional[str] = None
    num_datasets: int = 0

    @property
    def seismic_survey(self) -> SeismicSurvey:
        return SeismicSurvey(id=self.id, name=self.name, row_version=self.row_version, description=self.description,
                             division=self.division, number=self.number,
                             num_datasets=self.num_datasets, type=self.type)
