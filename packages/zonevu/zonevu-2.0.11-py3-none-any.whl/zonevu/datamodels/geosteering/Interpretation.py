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
from dataclasses import dataclass, field
from typing import Optional
from ..misc.permission import Editability, Visibility
from ..DataModel import DataModel
from .Pick import Pick
from .CurveDef import CurveDef
from .Horizon import Horizon, TypewellHorizonDepth, GeosteerHorizonRole
from datetime import datetime
from ...datamodels.Helpers import MakeIsodateOptionalField


@dataclass
class Zone:
    top: Horizon
    bottom: Optional[Horizon]


@dataclass
class Interpretation(DataModel):
    description: Optional[str] = ''
    starred: bool = False
    target_wellbore_id: int = -1
    target_wellbore_name: Optional[str] = None
    target_wellbore_number: Optional[str] = None
    target_formation_id: int = -1
    target_formation_name: Optional[str] = None
    target_formation_member_name: Optional[str] = None
    owner_name: Optional[str] = None
    owner_id: int = -1
    owner_company_name: str = ''
    visibility: Visibility = Visibility.Owner
    editability: Editability = Editability.Locked
    thickness: Optional[float] = None
    coordinate_system: Optional[str] = None
    picks: list[Pick] = field(default_factory=list[Pick])
    curve_defs: list[CurveDef] = field(default_factory=list[CurveDef])
    horizons: list[Horizon] = field(default_factory=list[Horizon])
    typewell_horizon_depths: Optional[list[TypewellHorizonDepth]] = field(default_factory=list[TypewellHorizonDepth])
    _old_id: Optional[int] = None   # Internal use

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Interpretation):
            DataModel.merge_lists(self.picks, source.picks)
            DataModel.merge_lists(self.curve_defs, source.curve_defs)
            DataModel.merge_lists(self.horizons, source.horizons)

    @property
    def valid(self) -> bool:
        """
        Check if the picks in the interpretation are valid and in order.
        :return:
        """
        enough_picks = len(self.picks) > 1
        picks_valid = all(p.valid for p in self.picks)
        picks_md_increases = all(p1.md <= p2.md for p1, p2 in zip(self.picks, self.picks[1:]))
        ok = enough_picks and picks_valid and picks_md_increases
        return ok

    def get_zone(self) -> Optional[Zone]:
        """
          Gets the zone defined by user for this interpretation.
          If none is defined, use the target (hang) formation to find a top of zone where the bottom is
        assumed to be the next horizon down.
          NOTE: the target (hang) formation can be different from the user defined top of zone. So the target_formation
        and the horizon marked with the 'ZoneTop' role could be different.

        :return: Zone comprised of a top and bottom horizon.
        """
        top = next((h for h in self.horizons if h.role == GeosteerHorizonRole.ZoneTop), None)
        bottom = next((h for h in self.horizons if h.role == GeosteerHorizonRole.ZoneBottom), None)

        if top is None:
            top = next((h for h in self.horizons if h.formation_id == self.target_formation_id), None)
            bottom = None

        if bottom is None:
            index = self.horizons.index(top)
            bottom = self.horizons[index + 1] if index + 1 < len(self.horizons) else None

        zone =  Zone(top, bottom)
        return zone




@dataclass
class InterpretationEntry(DataModel):
    # Represents a ZoneVu Geosteering interpretation catalog entry Object (lightweight)
    description: Optional[str] = ''
    starred: bool = False
    owner_company_name: str = ''
    visibility: Visibility = Visibility.Owner
    editability: Editability = Editability.Locked
    last_modified_by_name: str = ''
    last_modified_date: Optional[datetime] = MakeIsodateOptionalField()

    @property
    def interpretation(self) -> Interpretation:
        return Interpretation(id=self.id, name=self.name, row_version=self.row_version, description=self.description,
                              starred=self.starred)



