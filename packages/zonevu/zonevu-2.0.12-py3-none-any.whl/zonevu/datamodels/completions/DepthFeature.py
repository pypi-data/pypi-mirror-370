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
Completions depth-delimited feature model.

Defines :class:`DepthFeature` to represent a plug, perforation, or similar
feature bounded by measured-depth (MD) top/bottom, along with optional shot
parameters. Includes :class:`DepthFeatureKindEnum` to classify the feature.
"""

from ..DataModel import DataModel
from dataclasses import dataclass
from typing import Optional
from strenum import StrEnum


class DepthFeatureKindEnum(StrEnum):
    """Type of depth-delimited feature (plug, perforation, etc.)."""
    Undefined = 'Undefined'
    Plug = 'Plug'
    Perforation = 'Perforation'


@dataclass
class DepthFeature(DataModel):
    """A feature bounded by MD top/bottom with optional shot parameters."""
    stage_name: int = -1
    kind: DepthFeatureKindEnum = DepthFeatureKindEnum.Undefined
    top_md: float = 0
    bottom_md: float = 0
    shot_density: Optional[int] = None
    shot_count: Optional[int] = None
    phasing: Optional[float] = None
    orientation: Optional[float] = None