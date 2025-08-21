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
Seismic dataset description.

Represents a volume or attribute dataset associated with a seismic survey.
"""

from typing import Optional
from dataclasses import dataclass
from ..DataModel import DataModel
from strenum import StrEnum

class ZDomainEnum(StrEnum):
    """Vertical domain of the dataset (time, depth, velocity, amplitude)."""
    Time = 'Time'
    Depth = 'Depth'
    Velocity = 'Velocity'
    Amplitude = 'Amplitude'

class DatasetType(StrEnum):
    """Dataset form (volume or line)."""
    Unknown = 'Unknown'
    Volume = 'Volume'
    Line = 'Line'

@dataclass
class SeismicDataset(DataModel):
    """
    A ZoneVu seismic dataset (usually a stack) in a seismic survey
    """
    dataset_type: DatasetType = DatasetType.Unknown
    description: Optional[str] = None
    vintage: Optional[str] = None   # Processing vintage
    domain: ZDomainEnum = ZDomainEnum.Depth  # Domain of seismic data (Time, Depth, or Velocity)
    size: int = 0   # Size of seismic volume in megabytes
    segy_filename: Optional[str] = None
    is_registered: bool = False
