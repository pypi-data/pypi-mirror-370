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
Grouping for related well log curves.

Defines logical groupings and styling for curves.
Used to define:
1. Image logs for azimuthal gamma ray data
2. Lithology stacks for mud logs
3. Splice curves from multiple logs into a single curve (e.g. for a multi-BHA well)
"""

from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import LetterCase, DataClassJsonMixin
from dataclasses_json import config
from ...datamodels.DataModel import DataModel
import numpy as np
from strenum import StrEnum
from typing import List
from ...datamodels.geosteering.Conditioning import Conditioning
from ...datamodels.wells.Curve import AppMnemonicCodeEnum


class CurveGroupRoleEnum(StrEnum):
    """Role of the curve group in visualization (image/litho/splice)."""
    Image = "Image"
    Litho = "Litho"
    Splice = "Splice"


@dataclass
class CurveGroupParam(DataClassJsonMixin):
    """Parameter definition used to configure a curve in a group."""
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    id: int
    curve_id: int
    conditioning: Optional[Conditioning]


@dataclass
class CurveGroup(DataModel):
    """A logical group of curves."""
    role: CurveGroupRoleEnum = CurveGroupRoleEnum.Splice
    system_mnemonic: AppMnemonicCodeEnum = AppMnemonicCodeEnum.NotSet
    curve_ids: List[int] = field(default_factory=list[int])
    curve_channel_params: List[CurveGroupParam] = field(default_factory=list[CurveGroupParam])
    depths: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))
    samples: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))