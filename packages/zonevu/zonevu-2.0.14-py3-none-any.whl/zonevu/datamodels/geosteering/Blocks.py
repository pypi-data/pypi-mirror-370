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
Geosteering block model.

Defines blocks used to model stratigraphy for geosteering predictions.
"""

from dataclasses import dataclass, field
from ...datamodels.geosteering.Horizon import Horizon
from ...datamodels.geosteering.Pick import Pick
from typing import List, Optional, Union
from vectormath import Vector3, Vector2
from ..geospatial.GeoLocation import GeoLocation
from ..geospatial.Coordinate import Coordinate
from ..geospatial.Polyline import Polyline
from ..geospatial.LineSegment import LineSegment
import math
import numpy as np
from abc import ABC, abstractmethod


@dataclass
class GeosteerItem(ABC):
    """Base for geosteering items used in interpretations (picks, horizons)."""
    next_item: Optional['GeosteerItem']

    @property
    @abstractmethod
    def kind(self) -> str:
        pass

    @property
    # @abstractmethod
    def next(self) -> 'GeosteerItem':
        return self.next_item

    def find_next_block(self) -> Union['Block', None]:
        item = self
        while True:
            item = item.next
            if item is None or isinstance(item, Block):
                return item


@dataclass
class Layer:
    """
    A layer in a geosteering block corresponding to a horizon in a geosteering interpretation
    """
    block: 'Block'
    horz: Horizon
    tvd_start: float
    tvd_end: float
    thickness: float

    @property
    def polygon(self) -> Polyline:
        """
        A polygon in (md, tvd) space that is a layer in a geosteering block
        :return:
        """
        s = self
        x1 = s.block.md_start
        x2 = s.block.md_end
        y1a = s.tvd_start
        y1b = y1a + s.thickness
        y2a = s.tvd_end
        y2b = y2a + s.thickness
        coordinates = [Coordinate(x1, y1a), Coordinate(x2, y2a), Coordinate(x2, y2b), Coordinate(x1, y1b)]
        p = Polyline(coordinates)
        return p

    @property
    def top(self) -> LineSegment:
        s = self
        return LineSegment(Coordinate(s.block.md_start, s.tvd_start), Coordinate(s.block.md_end, s.tvd_end))

    @property
    def bottom(self) -> LineSegment:
        s = self
        return LineSegment(Coordinate(s.block.md_start, s.tvd_start + s.thickness), Coordinate(s.block.md_end, s.tvd_end + s.thickness))


@dataclass
class Block(GeosteerItem):
    """
    A geosteering block derived from a pair of geosteering interpretation pick
    NOTE: start = the heel-ward direction, and end = the toe-ward direction
    NOTE: in the interpretation, each block is followed by either a block or a fault.
    """
    start_pick: Pick
    end_pick: Pick
    layers: List[Layer] = field(default_factory=list[Layer])
    target_layer: Optional[Layer] = None
    # next_block: Optional['Block'] = None  # Either 'next_block' or 'next_fault' will not be None
    # next_fault: Optional['Fault'] = None

    @property
    def kind(self) -> str:
        return 'Block'

    # @property
    # def next(self) -> 'GeosteerItem':
    #     """
    #     Return next block (while skipping over any faults) after this block
    #     :return:
    #     """
    #     next_item = self.next_fault if self.next_block is None else self.next_block
    #     return next_item

    @property
    def md_start(self) -> float:
        return self.start_pick.md

    @property
    def md_end(self) -> float:
        return self.end_pick.md

    @property
    def location_start(self) -> GeoLocation:
        return GeoLocation(self.start_pick.latitude, self.start_pick.longitude)

    @property
    def location_end(self) -> GeoLocation:
        return GeoLocation(self.end_pick.latitude, self.end_pick.longitude)

    @property
    def xyz_start(self) -> Coordinate:
        return Coordinate(self.start_pick.x, self.start_pick.y, self.start_pick.target_tvd)

    @property
    def xyz_end(self) -> Coordinate:
        return Coordinate(self.end_pick.x, self.end_pick.y, self.end_pick.target_tvd)

    @property
    def elevation_start(self) -> float:
        """
        Get elevation of target formation at start of block
        :return:
        """
        return self.start_pick.target_elevation

    @property
    def elevation_end(self) -> float:
        """
        Get elevation of target formation at end of block
        :return:
        """
        return self.end_pick.target_elevation

    @property
    def dip(self) -> float:
        """
        Get geologic dip of block in direction of increasing MD
        :return:
        """
        c1 = self.xyz_start.vector
        c2 = self.xyz_end.vector
        v: Vector3 = c2 - c1  # Vector pointing along top of block
        h = Vector3(v.x, v.y, 0)  # Vector pointing along plane in direction of block
        cos_theta = v.dot(h) / (v.length * h.length)
        if cos_theta > 1:
            cos_theta = 1
        elif cos_theta < -1:
            cos_theta = -1
        try:
            dip_radians = math.acos(cos_theta)
            dip_degrees = math.degrees(dip_radians)
            return dip_degrees
        except ValueError as err:
            return np.nan

    @property
    def inclination(self) -> float:
        """
        This is the "MD dip" - inclination relative to the wellbore inclination
        :return:
        """
        dHX = self.end_pick.md - self.start_pick.md
        dTVD = self.end_pick.target_tvd - self.start_pick.target_tvd
        incl = 90 + math.atan2(-dTVD, dHX) * 180 / math.pi
        return incl

    @property
    def length(self) -> float:
        """
        Get length of block
        :return:
        """
        c1 = self.xyz_start.vector
        c2 = self.xyz_end.vector
        v: Vector3 = c2 - c1  # Vector pointing along top of block
        return v.length

    @property
    def md_length(self) -> float:
        md_len = self.md_end - self.md_start
        return md_len

    def contains_md(self, md: float):
        if self.md_start <= md < self.md_end:
            return True
        return False

    def make_copy(self) -> 'Block':
        block_copy = Block(next_item=None, start_pick=self.start_pick, end_pick=self.end_pick)
        for L in self.layers:
            l_copy = Layer(block=block_copy, tvd_start=L.tvd_start, tvd_end=L.tvd_end, horz=L.horz,
                           thickness=L.thickness)
            block_copy.layers.append(l_copy)
        return block_copy

    @classmethod
    def make_infill_block(cls, b1: 'Block', b2: 'Block') -> 'Block':
        b = Block(next_item=None, start_pick=b1.end_pick, end_pick=b2.start_pick)
        for l1, l2 in zip(b1.layers, b2.layers):
            infill_layer = Layer(block=b, tvd_start=l1.tvd_end, tvd_end=l2.tvd_start, horz=l1.horz,
                                 thickness=(l2.tvd_start - l1.tvd_end))
            b.layers.append(infill_layer)
            if b1.target_layer is not None and infill_layer.horz == b1.target_layer.horz:
                b.target_layer = infill_layer
        return b

    def make_pick(self, md: float) -> Pick:
        p1 = self.start_pick
        p2 = self.end_pick
        m = (md - p1.md) / (p2.md - p1.md)

        def lerp(a, b):
            return a + (b - a) * m

        c = lerp(self.xyz_start.vector, self.xyz_end.vector)
        g1 = Vector3(self.location_start.longitude, self.location_start.latitude, self.elevation_start)
        g2 = Vector3(self.location_end.longitude, self.location_end.latitude, self.elevation_start)
        g = lerp(g1, g2)
        d = lerp(Vector2(p1.dx, p1.dy), Vector2(p2.dx, p2.dy))
        tvt = lerp(p1.target_tvt, p2.target_tvt)
        elev = lerp(p1.elevation, p2.elevation)
        tvd = lerp(p1.tvd, p2.tvd)
        vx = lerp(p1.vx, p2.vx)
        p = Pick(target_tvd=c.z, x=c.x, y=c.y, md=md, block_flag=True, type_wellbore_id=p1.type_wellbore_id,
                 type_curve_def_id=p1.type_curve_def_id, latitude=g.y, longitude=g.x, target_elevation=g.z,
                 dx=d.x, dy=d.y, target_tvt=tvt, elevation=elev, tvd=tvd, vx=vx)
        return p


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
class Fault(GeosteerItem):
    """
    A geosteering fault derived from a pair of geosteering interpretation picks
    NOTE: in the interpretation, each fault is followed by a block.
    """
    pick: Pick
    throws: List[Throw] = field(default_factory=list[Throw])
    target_throw: Optional[Throw] = None
    # next_block: Optional[Block] = None

    @property
    def kind(self) -> str:
        return 'Fault'

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
        if len(self.throws) > 0:
            last_t = self.throws[-1]
            max_tvd = max(last_t.tvd_start, last_t.tvd_end)
            pts.append(Coordinate(self.md, max_tvd))
        return Polyline(pts)

