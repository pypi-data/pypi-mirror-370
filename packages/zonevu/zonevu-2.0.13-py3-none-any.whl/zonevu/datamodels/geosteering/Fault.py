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

"""
Geosteering fault model.

Represents a structural fault used to adjust interpretation picks.
"""

from dataclasses import dataclass, field
from .Horizon import Horizon
from .Pick import Pick
from .Blocks import Block
from typing import List
from ..geospatial.Polyline import Polyline
from ..geospatial.GeoLocation import GeoLocation
from ..geospatial.Coordinate import Coordinate


@dataclass
class Throw:
    """
    A throw in a geosteering fault corresponding to a horizon in a geosteering interpretation
    """
    fault: 'Fault'
    horz: Horizon
    tvd_start: float
    tvd_end: float
    throw_amt: float

    @property
    def line(self) -> Polyline:
        line = Polyline([Coordinate(self.fault.md, self.tvd_start), Coordinate(self.fault.md, self.tvd_end)])
        return line


@dataclass
class Fault:
    """
    A geosteering fault derived from a pair of geosteering interpretation picks
    """
    pick: Pick
    next_block: Block
    throws: List[Throw] = field(default_factory=list[Throw])

    @property
    def md(self) -> float:
        return self.pick.md

    @property
    def location(self) -> GeoLocation:
        return GeoLocation(self.pick.latitude, self.pick.longitude)

    def xyz(self) -> Coordinate:
        """
        XYZ of the top of target on heel-ward side of fault.
        :return:
        """
        return Coordinate(self.pick.x, self.pick.y, self.pick.target_tvd)

    @property
    def elevation(self) -> float:
        """
        Elevation of the top of target on heel-ward side of fault.
        :return:
        """
        return self.pick.target_elevation

    @property
    def trace(self) -> Polyline:
        pts = [Coordinate(self.md, min(t.tvd_start, t.tvd_end)) for t in self.throws]
        last_t = self.throws[-1]
        max_tvd = max(last_t.tvd_start, last_t.tvd_end)
        pts.append(Coordinate(self.md, max_tvd))
        return Polyline(pts)