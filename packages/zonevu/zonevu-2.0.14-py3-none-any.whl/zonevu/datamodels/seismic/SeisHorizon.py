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
Seismic horizon surface.

Represents a picked horizon derived from seismic interpretation.
"""

from typing import Optional
from strenum import StrEnum
from dataclasses import dataclass
from ..geomodels.GriddedData import GriddedData
from ..geospatial.Coordinate import Coordinate


class GridUsageEnum(StrEnum):
    """Usage classification for seismic horizon grid values."""
    Undefined = 'Undefined'
    Structural = 'Structural'
    Isopach = 'Isopach'
    Attribute = 'Attribute'


@dataclass
class SeisHorizon(GriddedData):
    """
    A seismic horizon interpreted on a 3D seismic dataset.
    """
    symbol: Optional[str] = None
    thickness: Optional[int] = None
    color: Optional[str] = None
    interpreter: Optional[str] = None





