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
Geologic horizon used in geosteering.

Named surface used to segment interpretations into zones.
"""

from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import config
from ..DataModel import DataModel
from ..styles.LineStyle import LineStyle
from ..styles.FillStyle import FillStyle
from strenum import StrEnum


class GeosteerHorizonRole(StrEnum):
    """Semantic role of a geosteering horizon (zone tops/bases, targets)."""
    Default = 'Default'
    ZoneTop = 'ZoneTop'
    ZoneBottom = 'ZoneBottom'    
    AnalysisTop = 'AnalysisTop'
    AnalysisBase = 'AnalysisBase'
    TargetTop = 'TargetTop'
    TargetBase = 'TargetBase'


@dataclass
class Horizon(DataModel):
    """
    Represents a geosteering horizon.
    """
    role: GeosteerHorizonRole = GeosteerHorizonRole.Default
    formation_id: int = -1
    show: bool = True
    line_style: Optional[LineStyle] = None
    fill_style: Optional[FillStyle] = None
    zone_name: Optional[str] = None
    defines_zone: Optional[bool] = None

    def get_line_color(self) -> str:
        if self.line_style is None:
            return 'black'
        return self.line_style.color


@dataclass
class TypewellHorizonDepth(DataModel):
    """
    Represents a depth of a geosteering horizon on a type well, which often is a well top depth.
    Includes tvt, which is relative to the type_wellbore_target top tvd.
    """
    type_wellbore_id: int = 0
    horizon_id: int = 0
    md: float = field(default=0.0, metadata=config(field_name="MD"))
    tvd: float = field(default=0.0, metadata=config(field_name="TVD"))
    tvt: float = field(default=0.0, metadata=config(field_name="TVT"))

    @property
    def key(self) -> str:
        return TypewellHorizonDepth.make_key(self.type_wellbore_id, self.horizon_id)

    @staticmethod
    def make_key(type_wellbore_id: int, horizon_id: int) -> str:
        return '%s-%s' % (type_wellbore_id, horizon_id)