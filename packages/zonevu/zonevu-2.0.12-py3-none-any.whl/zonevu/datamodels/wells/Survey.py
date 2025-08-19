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
Wellbore trajectory survey.

Defines survey metadata and stations comprising the actual or planned path of the wellbore.
"""

from typing import Optional, Union, List
from dataclasses import dataclass, field
from ...datamodels.DataModel import DataModel
from strenum import StrEnum
from ...datamodels.wells.Station import Station


class DeviationSurveyUsageEnum(StrEnum):
    """Whether a deviation survey is a plan or an actual run."""
    Plan = 'Plan'
    Actual = 'Actual'


class AzimuthReferenceEnum(StrEnum):
    """Reference for azimuth readings (true, magnetic, grid)."""
    Unknown = 'Unknown'
    TrueNorth = 'TrueNorth'
    MagneticNorth = 'MagneticNorth'
    GridNorth = 'GridNorth'


@dataclass
class Survey(DataModel):
    """
    A well deviation survey
    """
    description: Optional[str] = None
    azimuth_reference: Optional[AzimuthReferenceEnum] = AzimuthReferenceEnum.Unknown
    azimuth_offset: Optional[float] = 0
    usage: Optional[DeviationSurveyUsageEnum] = DeviationSurveyUsageEnum.Actual
    is_default: Optional[bool] = False
    stations: list[Station] = field(default_factory=list[Station])

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Survey):
            DataModel.merge_lists(self.stations, source.stations)

    @property
    def valid_stations(self) -> List[Station]:
        valid_stations = [s for s in self.stations if s.valid]
        return valid_stations

    def find_md(self, tvd: float, extrapolate: bool = False) -> Union[float, None]:
        # Search for the MD corresponding to the provided TVD in the monotonic portion of the wellbore
        try:
            stations = self.stations
            if len(stations) == 0:
                return tvd # Treat as vertical straight hole where md == tvd
            station_first = stations[0]
            station_last = stations[-1]
            if len(stations) == 1:
                if station_first.tvd == 0 and station_first.md == 0:
                    return tvd # Treat as vertical straight hole where md == tvd
            if tvd == station_last.tvd:
                return station_last.md
            for n in range(len(stations) - 1):
                s1 = stations[n]
                s2 = stations[n + 1]

                if s2.tvd <= s1.tvd:
                    return None     # We have reached the non-monotonic portion of the well bore so give up.

                if s1.tvd <= tvd < s2.tvd:
                    dtvd = s2.tvd - s1.tvd
                    dmd = s2.md - s1.md
                    md = s1.md + dmd * (tvd - s1.tvd) / dtvd
                    return md
            return None
        except Exception as err:
            return None

        # return tvd

    def find_tvd(self, md: float) -> Union[float, None]:
        """
        Search for the TVD corresponding to the provided MD
        :param md: MD to search for
        :return: TVD for the provided MD
        """
        try:
            stations = self.stations
            if len(stations) == 0:
                return md # Treat as vertical straight hole where md == tvd
            station_first = stations[0]
            station_last = stations[-1]
            if len(stations) == 1:
                if station_first.tvd == 0 and station_first.md == 0:
                    return md # Treat as vertical straight hole where md == tvd
            if md < station_first.md or md > station_last.md:
                return None
            if md == station_last.md:
                return station_last.tvd
            for n in range(len(stations) - 1):
                s1 = stations[n]
                s2 = stations[n + 1]
                if s1.md <= md < s2.md:
                    dmd = s2.md - s1.md
                    dtvd = s2.tvd - s1.tvd
                    tvd = s1.tvd + dtvd * (md - s1.md) / dmd
                    return tvd
            return None
        except Exception as err:
            return None