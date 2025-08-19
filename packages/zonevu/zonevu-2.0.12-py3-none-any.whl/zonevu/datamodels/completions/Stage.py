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
Frac stage details.

Represents a single stage within a frac job, including timing and parameters.
"""

from ..DataModel import DataModel
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from ...datamodels.completions.DepthFeature import DepthFeature
from ...datamodels.completions.Plug import Plug
from ...datamodels.Helpers import MakeIsodateOptionalField


@dataclass
class Stage(DataModel):
    """Single frac stage with timing, features (perfs/plugs), and notes."""
    # Represents a ZoneVu frac stage data object on a wellbore
    sequence_num: int = 0
    key: Optional[str] = ''
    gap: bool = False
    note: Optional[str] = ''
    start_date: Optional[datetime] = MakeIsodateOptionalField()
    duration: Optional[float] = None
    toe_md: float = 0
    heel_md: float = 0

    screened_out: bool = False
    frac_hit: bool = False
    num_clusters: Optional[int] = None
    proppant_weight: Optional[float] = None
    water_volume: Optional[float] = None

    pressure: Optional[float] = None
    bottom_pressure: Optional[float] = None
    slurry_rate: Optional[float] = None
    breakdown_pressure: Optional[float] = None
    closure_pressure: Optional[float] = None
    avg_surface_pressure: Optional[float] = None
    max_surface_pressure: Optional[float] = None
    max_bottom_pressure: Optional[float] = None
    isip_pressure: Optional[float] = None
    closure_gradient: Optional[float] = None
    frac_gradient: Optional[float] = None
    tvd_depth: Optional[float] = None
    slurry_volume: Optional[float] = None
    avg_proppant_conc: Optional[float] = None
    max_proppant_conc: Optional[float] = None
    user_param_values: List[Optional[float]] = field(default_factory=list[Optional[float]])

    toe_plug: Optional[Plug] = None
    depth_features: List[DepthFeature] = field(default_factory=list[DepthFeature])

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Stage):
            if source.toe_plug is not None and self.toe_plug is not None:
                self.toe_plug.copy_ids_from(source.toe_plug)
            DataModel.merge_lists(self.depth_features, source.depth_features)