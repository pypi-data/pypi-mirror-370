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
Geosteering curve conditioning settings.

Parameters controlling filtering, scaling, and smoothing of modeled curves.
"""

from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Conditioning:
    """
    Represents a ZoneVu geosteering curve conditioning parameter set
    """
    # Amplitude Range filter
    AmplClip: bool = False
    AmplClipRangeMin: Optional[float] = None
    AmplClipRangeMax: Optional[float] = None
    AmplClipInclusiveNotExclusive: Optional[bool] = None

    # MD Range filter
    MDClip: bool = False
    MDClipRangeMin: Optional[float] = None
    MDClipRangeMax: Optional[float] = None
    MDClipInclusiveNotExclusive: Optional[bool] = None

    # Despiking filter.
    Despike: bool = False
    VarianceThreshold: Optional[
        float] = None  # Absolute variance that is acceptable as a number in the units of the curve data.
    DespikeLen: Optional[int] = None  # Should be an odd number. Number of pts in despiking filter.

    # Interpolation filter.
    Interpolate: bool = False
    MaxGap: Optional[int] = None

    # SmoothingFilter filter.
    Smooth: bool = False
    SmoothingLen: Optional[int] = None  # Number of points in smoothing filter.

    # Amplitude normalization filter.
    Normalize: bool = False
    Bias: Optional[float] = None  # Amplitude shift
    Scalar: Optional[float] = None  # Amplitude multiplier
