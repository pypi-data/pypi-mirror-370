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
Grid geometry parameters.

Grid size, origin, spacing, and rotation used by gridded datasets.
"""

from typing import Optional, Tuple, Union, Any, Tuple
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from numpy import ndarray, dtype, float64, float32

from .GridCorner import GridCorner
from .Crs import CrsSpec
from ..geomodels.SimpleGrid import SimpleGrid
from .Coordinate import Coordinate
import math
from .Enums import DistanceUnitsEnum
import numpy as np
from numpy import ndarray, dtype


@dataclass
class GridAxisInfo:
    """Axis parameters (count, spacing, origin) for a grid dimension."""
    start: int
    stop: int
    count: int


@dataclass
class GridInfo:
    """Grid size and rotation metadata for grid geometry construction."""
    inline_range: GridAxisInfo
    crossline_range: GridAxisInfo

    @property
    def num_samples(self) -> int:
        return self.inline_range.count * self.crossline_range.count

    def load_z_values(self, float_bytes: bytes) -> ndarray[Tuple[int, int], dtype[float]]:
        float_array = np.frombuffer(float_bytes, dtype=np.float32)
        z_values = float_array.reshape(self.inline_range.count, self.crossline_range.count)
        return z_values

@dataclass
class GridValue:
    """
    The value of a point on a grid
    """
    inline: int
    crossline: int
    c: Coordinate

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class GridGeometry:
    """Complete grid geometry including axes, origin, rotation, and CRS."""
    corner1: GridCorner  # The spec for the origin corner of the grid
    corner2: GridCorner
    corner3: GridCorner
    corner4: GridCorner
    coordinate_system: CrsSpec  # Specification of the projected coordinate system of grid
    inclination: Optional[float] = None  # In degrees
    geo_inclination: Optional[float] = None  # In degrees
    inline_bin_interval: Optional[float] = None # Distance units in meters
    crossline_bin_interval: Optional[float] = None # Distance units in meters
    area: Optional[float] = None

    @property
    def inline_start(self) -> int:
        return self.corner1.inline

    @property
    def inline_stop(self) -> int:
        return self.corner3.inline

    @property
    def crossline_start(self) -> int:
        return self.corner1.crossline

    @property
    def crossline_stop(self) -> int:
        return self.corner3.crossline

    @property
    def num_inlines(self) -> int:
        return self.corner3.inline - self.corner1.inline + 1

    @property
    def num_crosslines(self) -> int:
        return self.corner3.crossline - self.corner1.crossline + 1

    @property
    def grid_info(self) -> GridInfo:
        c1 = self.corner1
        c3 = self.corner3
        inline_info = GridAxisInfo(c1.inline, c3.inline, c3.inline - c1.inline + 1)
        crossline_info = GridAxisInfo(c1.crossline, c3.crossline, c3.crossline - c1.crossline + 1)
        return GridInfo(inline_info, crossline_info)

    @classmethod
    def from_simple_grid(cls, grid: SimpleGrid) -> 'GridGeometry':
        """
        Method to set up a simple grid geometry.
        For inclination = 0, rows are west to east, and columns south to north
        Must provide origin, dx, and dy in distance units of provided CRS
        @param grid: a simple grid definition
        @return: a partially filled GridGeometry, where geolocations and geo-inclination not populated.

        NOTES:
        We set up here a CW grid geometry, where rows (inlines) run from East to West, and columns (crosslines)
        run South to North.
        """

        radians = math.radians(grid.inclination)
        x_length = grid.dx * grid.num_cols
        y_length = grid.dy * grid.num_rows
        area = x_length * y_length
        units = grid.crs.units or DistanceUnitsEnum.Undefined
        if units.lower() == 'meters':
            area = area / 1000000
        else:
            area = area / 27878400

        c1 = GridCorner(1, 1, grid.origin, None)                    # LL Un-rotated case

        c2_offset = Coordinate(x_length, 0)
        c2_point = c2_offset.rotate(radians) + grid.origin
        c2 = GridCorner(grid.num_cols, 1, c2_point, None)            # LR Un-rotated case

        c3_offset = Coordinate(x_length, y_length)
        c3_point = c3_offset.rotate(radians) + grid.origin
        c3 = GridCorner(grid.num_cols, grid.num_rows, c3_point, None)   # UR Un-rotated case

        c4_offset = Coordinate(0, y_length)
        c4_point = c4_offset.rotate(radians) + grid.origin
        c4 = GridCorner(1, grid.num_rows, c4_point, None)           # UL Un-rotated case

        g = cls(c1, c2, c3, c4, grid.crs, grid.inclination, None, grid.dy, grid.dx, area)
        return g

    def get_xy(self, inline: int, crossline: int) -> Optional[Coordinate]:
        """
        Use this grid geometry to compute the (x,y) coordinate for a particular (inline, crossline)
        :param inline:
        :param crossline:
        :return The (x, y) coordinate in the spatial coordinate system of the grid geometry:
        """
        c1 = self.corner1
        c2 = self.corner2
        c4 = self.corner4
        num_inlines = self.num_inlines
        num_crosslines = self.num_crosslines

        if num_inlines == 0:
            raise ValueError("Invalid grid: c1 and c2 must differ in their inline values.")
        if num_crosslines == 0:
            raise ValueError("Invalid grid: c1 and c4 must differ in their crossline values.")
        if inline < self.inline_start or inline > self.inline_stop:
            raise ValueError("Inline number is out of range.")
        if crossline < self.crossline_start or crossline > self.crossline_stop:
            raise ValueError("Crossline number is out of range.")

        # Compute the unit vertical displacement from c1 to c2.
        vertical_dx = (c2.p.x - c1.p.x) / num_inlines
        vertical_dy = (c2.p.y - c1.p.y) / num_inlines

        # Compute the unit horizontal displacement from c1 to c4.
        horizontal_dx = (c4.p.x - c1.p.x) / num_crosslines
        horizontal_dy = (c4.p.y - c1.p.y) / num_crosslines

        # Calculate the offset from the origin in grid terms.
        d_inline = inline - c1.inline
        d_crossline = crossline - c1.crossline

        # Compute the Cartesian coordinates by combining the scaled unit vectors.
        x = c1.p.x + d_inline * vertical_dx + d_crossline * horizontal_dx
        y = c1.p.y + d_inline * vertical_dy + d_crossline * horizontal_dy
        return Coordinate(x, y)

    def get_xyz(self, inline: int, crossline: int, z_values: ndarray[Tuple[int, int], dtype[float]]) -> Coordinate:
        """
        Use this grid geometry to provide the (x,y, z) coordinate for a particular (inline, crossline) of the grid
        :param inline:
        :param crossline:
        :param z_values:  A 2D array of the z values for a grid with this grid geometry
        :return:
        """

        c = self.get_xy(inline, crossline)
        inline_index = inline - self.inline_start
        crossline_index = crossline - self.crossline_start
        c.z = z_values[inline_index, crossline_index]
        return c


