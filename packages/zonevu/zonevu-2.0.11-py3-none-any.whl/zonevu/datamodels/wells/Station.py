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

from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import config
from ...datamodels.DataModel import DataModel
from datetime import datetime
import math
from ...datamodels.Helpers import MakeIsodateOptionalField


@dataclass
class Station(DataModel):
    """
    A deviation survey station
    """
    md: float = field(default=0, metadata=config(field_name="MD"))
    tvd: Optional[float] = field(default=0, metadata=config(field_name="TVD"))
    # md: Optional[float] = field(default=None, metadata=config(field_name="MD"))
    # tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    inclination: Optional[float] = None
    azimuth: Optional[float] = None
    elevation: Optional[float] = None
    delta_x: Optional[float] = None
    delta_y: Optional[float] = None
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    time: Optional[datetime] = MakeIsodateOptionalField()

    @property
    def valid(self) -> bool:
        if self.md is None or self.tvd is None:
            return False
        if math.isnan(self.md) is None or math.isnan(self.tvd) is None:
            return False
        return True



