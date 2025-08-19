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

import dataclasses
from typing import Optional, Union, ClassVar, List
from dataclasses import dataclass, field
from datetime import datetime
from ...datamodels.wells.Wellbore import Wellbore
from ...datamodels.Document import Document
from dataclasses_json import config, dataclass_json, LetterCase, DataClassJsonMixin
from strenum import StrEnum, PascalCaseStrEnum
from enum import auto
import copy
from ...datamodels.Helpers import MakeIsodateOptionalField
from ...datamodels.DataModel import DataModel, ChangeAgentEnum, WellElevationUnitsEnum
from ...datamodels.PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from ...datamodels.strat.StratColumn import StratColumnEntry
from ...datamodels.geospatial.GeoLocation import GeoLocation
from ..Company import Division


class WellElevationTypeEnum(StrEnum):
    KB = 'KB'
    Wellhead = 'Wellhead'
    Ground = 'Ground'
    Water = 'Water'

@dataclass
class WellElevation(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    elevation: float
    elevation_type: WellElevationTypeEnum

class WellDirectionEnum(StrEnum):
    Unknown = 'Unknown'
    HuffNPuff = 'HuffNPuff'
    Injector = 'Injector'
    Producer = 'Producer'
    Uncertain = 'Uncertain'


class WellPurposeEnum(StrEnum):
    Unknown = 'Unknown'
    Appraisal = 'Appraisal'
    Appraisal_Confirmation = 'Appraisal_Confirmation'
    Appraisal_Exploratory = 'Appraisal_Exploratory'
    Exploration = 'Exploration'
    Exploration_DeeperPoolWildcat = 'Exploration_DeeperPoolWildcat'
    Exploration_NewFieldWildcat = 'Exploration_NewFieldWildcat'
    Exploration_NewPoolWildcat = 'Exploration_NewPoolWildcat'
    Exploration_OutpostWildcat = 'Exploration_OutpostWildcat'
    Exploration_ShallowerPoolWildcat = 'Exploration_ShallowerPoolWildcat'
    Development = 'Development'
    Development_InfillDevelopment = 'Development_InfillDevelopment'
    Development_Injector = 'Development_Injector'
    Development_Producer = 'Development_Producer'
    FluidStorage = 'FluidStorage'
    FluidStorage_Gas = 'FluidStorage_Gas'
    GeneralServices = 'GeneralServices'
    GeneralServices_BoreholeReacquisition = 'GeneralServices_BoreholeReacquisition'
    GeneralServices_Observation = 'GeneralServices_Observation'
    GeneralServices_Relief = 'GeneralServices_Relief'
    GeneralServices_Research = 'GeneralServices_Research'
    GeneralServices_Research_DrillTest = 'GeneralServices_Research_DrillTest'
    GeneralServices_Research_StratTest = 'GeneralServices_Research_StratTest'
    Mineral = 'Mineral'


class WellFluidEnum(StrEnum):
    Unknown = 'Unknown'
    Air = 'Air'
    Condensate = 'Condensate'
    Dry = 'Dry'
    Gas = 'Gas'
    Gas_Water = 'Gas_Water'
    Non_Hydrocarbon_Gas = 'Non_Hydrocarbon_Gas'
    Non_Hydrocarbon_Gas_CO2 = 'Non_Hydrocarbon_Gas_CO2'
    Oil = 'Oil'
    Oil_Gas = 'Oil_Gas'
    Oil_Water = 'Oil_Water'
    Steam = 'Steam'
    Water = 'Water'
    Water_Brine = 'Water_Brine'
    Water_FreshWater = 'Water_FreshWater'


class EnvironmentTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Land = 'Land'
    Marine = 'Marine'
    Transition = 'Transition'


class WellStatusEnum(PascalCaseStrEnum):
    Unknown = auto()
    Active = auto()
    ActiveInjecting = auto()
    ActiveProducing = auto()
    Completed = auto()
    Drilling = auto()
    PartiallyPlugged = auto()
    Permitted = auto()
    PluggedAndAbandoned = auto()
    Proposed = auto()
    Sold = auto()
    Suspended = auto()
    TemporarilyAbandoned = auto()
    Testing = auto()
    Tight = auto()
    WorkingOver = auto()

class WellInterestEnum(StrEnum):
    Unknown = 'Unknown'
    Operated = 'Operated'
    NonOperated = 'NonOperated'
    Royalty = 'Royalty'
    Override = 'Override'
    NoInterest = 'NoInterest'


@dataclass
class Well(PrimaryDataObject):
    """
    Represents a ZoneVu Well Object
    """
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodateOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodateOptionalField()
    number: Optional[str] = None
    description: Optional[str] = None
    uwi: Optional[str] = field(default=None, metadata=config(field_name="UWI"))
    original_uwi: Optional[str] = None
    division: Optional[Division] = None
    status: Optional[WellStatusEnum] = WellStatusEnum.Unknown
    is_live: Optional[bool] = False
    environment: Optional[EnvironmentTypeEnum] = EnvironmentTypeEnum.Unknown
    purpose: Optional[WellPurposeEnum] = WellPurposeEnum.Unknown
    fluid_type: Optional[WellFluidEnum] = WellFluidEnum.Unknown
    well_direction: Optional[WellDirectionEnum] = WellDirectionEnum.Unknown
    property_number: Optional[str] = None
    afe_number: Optional[str] = field(default=None, metadata=config(field_name="AFENumber"))
    spud_date: Optional[datetime] = MakeIsodateOptionalField()
    completion_date: Optional[datetime] = MakeIsodateOptionalField()
    permit_date: Optional[datetime] = MakeIsodateOptionalField()
    plugged_date: Optional[datetime] = MakeIsodateOptionalField()
    target_zone: Optional[str] = None
    target_zone_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rig: Optional[str] = None
    pad: Optional[str] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    zone: Optional[str] = None
    oil_field: Optional[str] = field(default=None, metadata=config(field_name="Field"))
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    land_grid_location: Optional[str] = None
    license_number: Optional[str] = None
    license_issue_date: Optional[datetime] = MakeIsodateOptionalField()
    operator: Optional[str] = None
    operator_division: Optional[str] = None
    operator_property_number: Optional[str] = None
    interest: Optional[float] = None
    interest_type: Optional[WellInterestEnum] = WellInterestEnum.Operated
    elevation: Optional[float] = None
    elevation_type: Optional[WellElevationTypeEnum] = WellElevationTypeEnum.KB
    elevation_units: Optional[WellElevationUnitsEnum] = None
    elevations: List[WellElevation] = dataclasses.field(default_factory=list[WellElevation])
    location_datum: Optional[str] = None
    strat_column: Optional[StratColumnEntry] = None
    azimuth: Optional[float] = None
    primary_well_bore_md: Optional[float] = field(default=None, metadata=config(field_name="PrimaryWellBoreMD"))
    primary_well_bore_tvd: Optional[float] = field(default=None, metadata=config(field_name="PrimaryWellBoreTVD"))
    wellbores: List[Wellbore] = dataclasses.field(default_factory=list[Wellbore])
    primary_well_bore_net_pay: Optional[float] = None


    documents: List[Document] = dataclasses.field(default_factory=list[Document])

    # region Storage
    archive_dir_name: ClassVar[str] = 'wells'
    archive_json_filename: ClassVar[str] = 'well.json'
    # endregion

    @property
    def location(self) -> GeoLocation:
        return GeoLocation(self.latitude, self.longitude)

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.Well

    def init_primary_wellbore(self):
        primary_wellbore = Wellbore()
        primary_wellbore.name = 'Primary'
        self.wellbores = []
        self.wellbores.append(primary_wellbore)

    def copy_ids_from(self, source: 'DataModel'):
        super().copy_ids_from(source)
        # well: Well = cast(Well, source)
        if isinstance(source, Well):
            DataModel.merge_lists(self.wellbores, source.wellbores)

    def make_trimmed_copy(self) -> 'Well':
        # Make a copy that is suitable for creating wells through the Web API
        wellbores = self.wellbores
        self.wellbores = []
        well_copy = copy.deepcopy(self)
        well_copy.wellbores = [bore.make_trimmed_copy() for bore in wellbores]
        self.wellbores = wellbores
        return well_copy

    def get_documents(self) -> List[Document]:
        return self.documents

    @property
    def full_name(self) -> str:
        if self.number is None:
            return self.name or 'unnamed'
        else:
            return '%s %s' % (self.name, self.number)

    @property
    def primary_wellbore(self) -> Union[Wellbore, None]:
        """
        Gets the primary wellbore on the well. Normally, there is only a wellbore per well,
        and it is the primary wellbore
        """
        return self.wellbores[0] if len(self.wellbores) > 0 else None


@dataclass_json
@dataclass
class WellEntry(DataModel):
    # Represents a ZoneVu Well catalog entry Object (lightweight)
    id: int = -1
    uwi: Optional[str] = field(default=None, metadata=config(field_name="UWI"))
    name: str = ''
    number: Optional[str] = None
    description: Optional[str] = None
    division: Optional[Division] = None
    status: Optional[str] = None
    is_live: Optional[bool] = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @property
    def location(self) -> GeoLocation:
        return GeoLocation(self.latitude, self.longitude)

    @property
    def full_name(self):
        name = (self.name or 'unnamed').strip()
        number = (self.number or '').strip()
        has_number = len(number) > 0
        result = f'{name} {number}' if has_number else name
        return result

    @property
    def well(self) -> Well:
        return Well(id=self.id, name=self.name, row_version=self.row_version, number=self.number,
                    description=self.description, division=self.division,
                    status=self.status)







