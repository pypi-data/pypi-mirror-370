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
Geosteering curve definition.

Defines synthetic curve parameters used in geosteering modeling.
Also serves as the primary method of linking type or reference wells to a 
geosteering interpretation.
"""

from dataclasses import dataclass
from typing import Optional
from ..DataModel import DataModel
from .Conditioning import Conditioning
from strenum import StrEnum


class CurveDefWellboreRoleEnum(StrEnum):
    """Whether a curve definition is for target or type wellbore."""
    TargetWellbore = 'TargetWellbore'
    TypeWellbore = 'TypeWellbore'


class CurveGroupRoleEnum(StrEnum):
    """Grouping role of the curve (image, litho, splice)."""
    Image = 'Image'
    Litho = 'Litho'
    Splice = 'Splice'


@dataclass
class CurveDef(DataModel):
    """
    Represents a ZoneVu geosteering curve definition

    Also serves as the primary method of linking type or reference wells to a 
    geosteering interpretation.
    """
    #: Name of well from which this well log curve comes
    well_name: Optional[str] = None
    #: Id of Well from which this well log curve comes
    well_id: Optional[int] = None
    #: Id of Wellbore from which this well log curve comes
    wellbore_id: Optional[int] = None
    #: Role of wellbore from which this well log curve comes
    wellbore_role: Optional[CurveDefWellboreRoleEnum] = None
    #: Id of Well log from which this well log curve comes
    well_log_id: Optional[int] = None
    #: Well log curve system id. Note either this or curve_group_id will be populated
    curve_id: Optional[int] = None
    #: Well log curve group id. Note either this or curve_group_id will be populated
    curve_group_id: Optional[int] = None
    #: If this def is using a curve group, specifies type of curve def
    role: Optional[CurveGroupRoleEnum] = None
    #: Whether this curve is the active one in the interpretation workflow
    active: bool = False
    #: Curve conditioning applied to this curve
    conditioning: Optional[Conditioning] = None
