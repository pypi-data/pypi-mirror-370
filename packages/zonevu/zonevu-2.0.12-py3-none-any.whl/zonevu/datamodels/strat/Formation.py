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
Stratigraphic formation definition.

Defines a named formation with styling used in strat columns.
"""

from typing import Optional
from dataclasses import dataclass
from ...datamodels.DataModel import DataModel
from strenum import StrEnum, PascalCaseStrEnum


class GeoPeriodEnum(StrEnum):
    """Geological time period classification for formations."""
    Unset = 'Unset',
    Quaternary = 'Quaternary',
    Neogene = 'Neogene',
    Paleogene = 'Paleogene',
    Cretaceous = 'Cretaceous',
    Jurassic = 'Jurassic',
    Triassic = 'Triassic',
    Permian = 'Permian',
    Carboniferous = 'Carboniferous',
    Devonian = 'Devonian',
    Silurian = 'Silurian',
    Ordovician = 'Ordovician',
    Cambrian = 'Cambrian',
    Precambrian = 'Precambrian'


class LithologyTypeEnum(PascalCaseStrEnum):
    """Primary lithology type of a formation (sandstone, shale, etc.)."""
    Unset = 'Unset',
    Sandstone = 'Sandstone',
    Shale = 'Shale',
    Limestone = 'Limestone',
    Dolomite = 'Dolomite',
    Chalk = 'Chalk',
    Marl = 'Marl',
    MudstoneRich = 'MudstoneRich',
    MudstoneLean = 'MudstoneLean',
    Bentonite = 'Bentonite',
    Coal = 'Coal',
    Chert = 'Chert',
    Anhydrite = 'Anhydrite',
    Siltstone = 'Siltstone',
    ShalySand = 'ShalySand',
    SandstoneBedded = 'SandstoneBedded',
    CalcareousSandstone = 'CalcareousSandstone',
    SandyShale = 'SandyShale',
    ShalyLimestone = 'ShalyLimestone',
    SandyLimestone = 'SandyLimestone',
    ShalyDolostone = 'ShalyDolostone',
    SandyDolostone = 'SandyDolostone',
    LimestoneShale = 'LimestoneShale',
    ShaleSandstone = 'ShaleSandstone',
    SandstoneShale = 'SandstoneShale',
    ShaleLimestone = 'ShaleLimestone',
    Salt = 'Salt',
    ChertyShale = 'ChertyShale',
    Breccia = 'Breccia',
    Conglomerate = 'Conglomerate',
    Basalt = 'Basalt',
    Granite = 'Granite',
    Igneous = 'Igneous',
    Tuff = 'Tuff',
    Crosshatch = 'Crosshatch'
    SiltySandstone = 'SiltySandstone'
    SiltyShale = 'SiltyShale'
    SiltyLimestone = 'SiltyLimestone'
    SiltyDolostone = 'SiltyDolostone'
    Gypsum = 'Gypsum'


@dataclass
class Formation(DataModel):
    """
    A geologic formation
    """
    #: Formation name
    # Note: formation name is the DataModel 'name' data field
    #: Optional column member name
    member_name: Optional[str] = None
    #: Required stratigraphic order ordinal
    strat_col_order: int = -1
    #: Formation symbol (mnemonic)
    symbol: str = ''
    #: Optional default color for rendering this formation in a display
    color: Optional[str] = None
    #: Optional description of formation
    description: Optional[str] = None
    #: Optional geologic age of this formation
    period: Optional[GeoPeriodEnum] = None
    # Optional lithology of this formation
    lithology_type: Optional[LithologyTypeEnum] = None
