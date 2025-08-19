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
Geospatial enumeration types.

Common enumerations for units, directions, and CRS-related values.
"""

from strenum import StrEnum


class UnitsSystemEnum(StrEnum):
    """Unit system grouping (Metric or US)."""
    Metric = 'Metric'
    US = 'US'

class DistanceUnitsEnum(StrEnum):
    """Linear distance units, with helper to map to a unit system."""
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    FeetUS = 'FeetUS'

    @classmethod
    def units_system(cls, units: 'DistanceUnitsEnum') -> UnitsSystemEnum:
        return UnitsSystemEnum.Metric if units == DistanceUnitsEnum.Meters else UnitsSystemEnum.US


class DepthUnitsEnum(StrEnum):
    """
    Enum of ZoneVu depth units
    """
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'

    @classmethod
    def units_system(cls, units: 'DepthUnitsEnum') -> UnitsSystemEnum:
        return UnitsSystemEnum.Metric if units == DepthUnitsEnum.Meters else UnitsSystemEnum.US