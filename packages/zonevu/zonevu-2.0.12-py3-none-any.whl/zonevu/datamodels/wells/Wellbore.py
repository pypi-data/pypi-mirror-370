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
Wellbore entity.

Represents a borehole with MD/TVD extents, trajectory, and related data.
"""

from typing import Optional, Union, List, Iterator
from dataclasses import dataclass, field
from dataclasses_json import config
from strenum import StrEnum
from ...datamodels.DataModel import DataModel
from ...datamodels.wells.Welllog import Welllog
from ...datamodels.wells.Survey import Survey, DeviationSurveyUsageEnum
from ...datamodels.wells.Welltop import Welltop
from ...datamodels.geosteering.Interpretation import Interpretation
from ...datamodels.wells.Curve import Curve, AppMnemonicCodeEnum
from ...datamodels.wells.CurveGroup import CurveGroup
from ...datamodels.wells.Note import Note
from ...datamodels.completions.Frac import Frac


class WellBoreShapeEnum(StrEnum):
    """Generalized trajectory shape classification for a wellbore."""
    BuildAndHold = 'BuildAndHold'
    Deviated = 'Deviated'
    DoubleKickoff = 'DoubleKickoff'
    Horizontal = 'Horizontal'
    S_Shaped = 'S_Shaped'
    Vertical = 'Vertical'
    Unknown = 'Unknown'


@dataclass
class Wellbore(DataModel):
    """Borehole with logs, surveys, tops, interpretations, notes, and fracs."""
    uwi: Optional[str] = field(default=None, metadata=config(field_name="UWI"))
    shape: Optional[WellBoreShapeEnum] = WellBoreShapeEnum.Unknown
    welllogs: List[Welllog] = field(default_factory=list[Welllog])
    surveys: List[Survey] = field(default_factory=list[Survey])
    tops: List[Welltop] = field(default_factory=list[Welltop])
    interpretations: List[Interpretation] = field(default_factory=list[Interpretation])
    notes: List[Note] = field(default_factory=list[Note])
    fracs: List[Frac] = field(default_factory=list[Frac])

    def copy_ids_from(self, source: 'DataModel'):
        super().copy_ids_from(source)
        if isinstance(source, Wellbore):
            DataModel.merge_lists(self.welllogs, source.welllogs)
            DataModel.merge_lists(self.surveys, source.surveys)
            DataModel.merge_lists(self.tops, source.tops)
            DataModel.merge_lists(self.interpretations, source.interpretations)

    def make_trimmed_copy(self) -> 'Wellbore':
        # Make a copy that is suitable for creating wells through the Web API
        # In this case, don't include any lists of sub well data. Those get created via Web API separately
        copy = Wellbore()
        copy.name = self.name
        copy.id = self.id
        copy.row_version = self.row_version
        copy.uwi = self.uwi
        copy.shape = self.shape
        return copy

    @property
    def actual_survey(self) -> Union[Survey, None]:
        surveys = self.surveys
        survey = next((s for s in surveys if s.usage == DeviationSurveyUsageEnum.Actual), None)  # Get actual survey
        return survey

    @property
    def plan_surveys(self) -> List[Survey]:
        surveys = self.surveys
        plans = [s for s in surveys if s.usage == DeviationSurveyUsageEnum.Plan]
        return plans

    @property
    def well_log_curves(self) -> List[Curve]:
        return [c for log in self.welllogs for c in log.curves]

    @property
    def well_log_curve_groups(self) -> List[CurveGroup]:
        return [c for log in self.welllogs for c in log.curve_groups]

    def get_curves(self) -> Iterator[Curve]:
        for log in self.welllogs:
            for curve in log.curves:
                yield curve

    def get_first_curve(self, code: AppMnemonicCodeEnum) -> Curve | None:
        for curve in self.get_curves():
            if curve.system_mnemonic == code:        
                return curve
        return None

    def get_depth_curve(self) -> Curve | None:
        return self.get_first_curve(AppMnemonicCodeEnum.DEPT)

    def get_starred_interp(self) -> Optional[Interpretation]:
        """
        Get starred or first interpretation
        """
        geosteering_data = self.interpretations
        if len(geosteering_data) == 0:
            return None
        return next((g for g in geosteering_data if g.starred), geosteering_data[0])