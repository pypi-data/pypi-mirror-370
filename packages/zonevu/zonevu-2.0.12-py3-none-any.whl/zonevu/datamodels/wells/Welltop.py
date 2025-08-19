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
Stratigraphic top pick.

Represents a formation pick along a wellbore with depth and metadata.
"""

from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import config
from ...datamodels.wells.Survey import Survey
from ...datamodels.DataModel import DataModel


@dataclass
class Welltop(DataModel):
    """Formation pick along a wellbore with MD/TVD and metadata."""
    observation_number: Optional[int] = None
    formation_id: int = -1
    formation_name: str = ''
    formation_symbol: str = ''
    strat_column_id:  int = -1
    md: Optional[float] = field(default=None, metadata=config(field_name="MD"))
    tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    elevation: Optional[float] = None
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    interpreter: Optional[str] = None
    description: Optional[str] = None
    porosity: Optional[float] = None
    water_saturation: Optional[float] = None
    shale_content: Optional[float] = None
    hc_porosity: Optional[float] = field(default=None, metadata=config(field_name="HCPorosity"))
    geoprog_top: bool = False               # Is this a geoprog top?
    survey_id: Optional[int] = None     # Wellbore survey top was picked on
    survey: Optional[Survey] = field(metadata=config(exclude=lambda x: True), default=None) # Do not emit to json