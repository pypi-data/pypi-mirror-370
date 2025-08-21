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
Geosteering pick.

Represents a point along the well path with target TVD.
"""

import math
from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import config
from ..DataModel import DataModel


@dataclass
class Pick(DataModel):
    """Geosteering pick at a measured depth with target TVD/TVT and coordinates."""
    # Represents a ZoneVu geosteering interpretation pick
    #: TVD for this md on wellbore
    tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    #: MD (Measured Depth) of this along wellbore
    md: float = field(default=0, metadata=config(field_name="MD"))
    #: Vx (Vs) x-coordinate for this pick along wellbore projected into a plane for the current display azimuth
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    #: TVT (True Vertical Thickness) of pick from target TVD
    target_tvt: Optional[float] = field(default=None, metadata=config(field_name="TargetTVT"))
    #: TVD (True Vertical Depth) of pick in wellbore depth coordinates
    target_tvd: Optional[float] = field(default=None, metadata=config(field_name="TargetTVD"))
    #: Absolute elevation of pick
    target_elevation: Optional[float] = field(default=None, metadata=config(field_name="TargetElevation"))
    #: Latitude of pick in WGS84 Datum
    latitude: Optional[float] = None
    #: Longitude of pick in WGS84 Datum
    longitude: Optional[float] = None
    #: X-coordinate of pick in projected x,y coordinates of project well is in
    x: Optional[float] = None
    #: Y-coordinate of pick in projected x,y coordinates of project well is in
    y: Optional[float] = None
    #: X-offset of pick relative to well surface location
    dx: Optional[float] = field(default=None, metadata=config(field_name="DX"))
    #: Y-offset of pick relative to well surface location
    dy: Optional[float] = field(default=None, metadata=config(field_name="DY"))
    #: Elevation for this md on wellbore
    elevation: Optional[float] = None
    #: If true, this pick represents the end of the last block and the beginning of the next block.
    block_flag: bool = False
    # If true, this pick represents the end of the last block and a fault throw, and start of the next block.
    fault_flag: bool = False
    #: The system id of the type wellbore
    type_wellbore_id: int = -1
    #: The system id of the type well log curve def
    type_curve_def_id: Optional[int] = None

    @property
    def valid(self) -> bool:
        """
        Validity check on this pick.
        :return:
        """
        correct_flags = self.block_flag or (not self.block_flag and self.fault_flag)
        md_ok = self.md is not None and math.isfinite(self.md)
        tvd_ok = self.target_tvd is not None and math.isfinite(self.target_tvd)
        tvt_ok = self.target_tvt is not None and math.isfinite(self.target_tvt)
        x_ok = self.x is not None and math.isfinite(self.x)
        y_ok = self.y is not None and math.isfinite(self.y)
        lat_ok = self.latitude is not None and math.isfinite(self.latitude)
        lon_ok = self.longitude is not None and math.isfinite(self.longitude)
        elev_ok = self.target_elevation is not None and math.isfinite(self.target_elevation)
        ok = correct_flags and md_ok and tvd_ok and tvt_ok and x_ok and y_ok and lat_ok and lon_ok and elev_ok
        return ok

    def hidden(self) -> bool:
        """
        Note: a hidden pick is one that the user may have temporarily obscured in the GUI but it is still a valid pick.
        :return:
        """
        is_hidden = self.block_flag and self.fault_flag
        return is_hidden
