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
Lightweight regular grid.

Minimal grid representation for simple resampling and visualization tasks.
"""

from typing import List
from dataclasses import dataclass
from ..geospatial.Coordinate import Coordinate
from ..geospatial.Crs import CrsSpec


@dataclass
class SimpleGrid:
    """
    Represents a simple grid.
    Use float('-inf') to represent empty grid values
    """
    name: str
    origin: Coordinate      # x,y coordinate of grid origin
    inclination: float      # rotation of grid clockwise
    dx: float               # grid spacing in x-direction, when not rotated by inclination
    dy: float               # grid spacing in y-direction
    num_rows: int           # number of rows in grid. Rows are laid out along the x-direction  (non-rotated)
    num_cols: int           # number of columns in grid. Columns are laid out along the y-direction (non-rotated)
    crs: CrsSpec            # The projected coordinate system of the x,y origin.
    z_values: List[float]   # Z values of grid, as a 1-D array of 32-bit floats in row major order



