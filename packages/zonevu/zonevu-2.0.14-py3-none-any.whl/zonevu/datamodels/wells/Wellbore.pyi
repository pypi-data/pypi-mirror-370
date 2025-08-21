from ...datamodels.DataModel import DataModel as DataModel
from ...datamodels.completions.Frac import Frac as Frac
from ...datamodels.geosteering.Interpretation import Interpretation as Interpretation
from ...datamodels.wells.Curve import AppMnemonicCodeEnum as AppMnemonicCodeEnum, Curve as Curve
from ...datamodels.wells.CurveGroup import CurveGroup as CurveGroup
from ...datamodels.wells.Note import Note as Note
from ...datamodels.wells.Survey import DeviationSurveyUsageEnum as DeviationSurveyUsageEnum, Survey as Survey
from ...datamodels.wells.Welllog import Welllog as Welllog
from ...datamodels.wells.Welltop import Welltop as Welltop
from dataclasses import dataclass, field
from dataclasses_json import config
from strenum import StrEnum
from typing import Iterator

class WellBoreShapeEnum(StrEnum):
    BuildAndHold = 'BuildAndHold'
    Deviated = 'Deviated'
    DoubleKickoff = 'DoubleKickoff'
    Horizontal = 'Horizontal'
    S_Shaped = 'S_Shaped'
    Vertical = 'Vertical'
    Unknown = 'Unknown'

@dataclass
class Wellbore(DataModel):
    uwi: str | None = field(default=None, metadata=config(field_name='UWI'))
    shape: WellBoreShapeEnum | None = ...
    welllogs: list[Welllog] = field(default_factory=list[Welllog])
    surveys: list[Survey] = field(default_factory=list[Survey])
    tops: list[Welltop] = field(default_factory=list[Welltop])
    interpretations: list[Interpretation] = field(default_factory=list[Interpretation])
    notes: list[Note] = field(default_factory=list[Note])
    fracs: list[Frac] = field(default_factory=list[Frac])
    def copy_ids_from(self, source: DataModel): ...
    def make_trimmed_copy(self) -> Wellbore: ...
    @property
    def actual_survey(self) -> Survey | None: ...
    @property
    def plan_surveys(self) -> list[Survey]: ...
    @property
    def well_log_curves(self) -> list[Curve]: ...
    @property
    def well_log_curve_groups(self) -> list[CurveGroup]: ...
    def get_curves(self) -> Iterator[Curve]: ...
    def get_first_curve(self, code: AppMnemonicCodeEnum) -> Curve | None: ...
    def get_depth_curve(self) -> Curve | None: ...
    def get_starred_interp(self) -> Interpretation | None: ...
