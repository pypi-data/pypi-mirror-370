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
Generic container for gridded scalar data.

Stores a 2D array with associated grid geometry metadata.
"""

from typing import Optional
from dataclasses import field
from dataclasses_json import config
from abc import ABC
from dataclasses import dataclass
from ..DataModel import DataModel
from ..geospatial.GridGeometry import GridGeometry
import numpy as np


@dataclass
class GriddedData(DataModel, ABC):
    """Abstract base for 2D gridded scalar data with geometry and stats."""
    geometry: Optional[GridGeometry] = None
    description: Optional[str] = None
    average_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    z_values: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))
