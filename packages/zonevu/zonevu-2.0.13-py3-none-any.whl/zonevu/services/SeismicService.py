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
#
#


"""
Seismic data service.

Search, retrieve, and create seismic surveys and horizons, manage related
datasets and registrations, and obtain credentials for volume upload/download.
"""

from ..datamodels.seismic.Fault import Fault, FaultEntry
from ..datamodels.geospatial.GridGeometry import GridValue
from ..datamodels.seismic.SeisHorizon import SeisHorizon
from ..datamodels.seismic.SeismicSurvey import SeismicSurveyEntry, SeismicSurvey, SeismicDataset
from ..datamodels.seismic.SeismicRegistration import SeismicRegistration
from ..datamodels.Company import Division
from .Client import Client, ZonevuError
from typing import Tuple, Optional, List, Union
from ..services.Utils import CloudBlobCredential
from numpy import ndarray, dtype


class SeismicService:
    """Search, retrieve, and create seismic surveys and horizons."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_surveys(self, match_token: Optional[str] = None, division: Optional[Union[Division, int]] = None) -> List[SeismicSurveyEntry]:
        """
        Gets a list of seismic surveys whose names start with the provided string token.
        :param match_token: If not provided, all surveys from this zonevu account will be retrieved.
        :param division: division (business unit) to search in. If None, searches all divisions user is authorized for
        :return: a list of partially loaded seismic surveys
        """
        url = "seismic/surveys"
        if match_token is not None:
            url += "/%s" % match_token
        query_params = {}
        if division is not None:
            division_id = division if isinstance(division, int) else division.id
            query_params["divisionid"] = division_id
        items = self.client.get_list(url, query_params)
        entries = [SeismicSurveyEntry.from_dict(w) for w in items]
        return entries

    def get_first_named(self, name: str) -> Optional[SeismicSurvey]:
        """
        Get first seismic survey with the specified name, populate it, and return it.
        :param name: name or project to get
        :return: a fully loaded seismic survey
        """
        entries = self.get_surveys(name)
        if len(entries) == 0:
            return None
        surveyEntry = entries[0]
        survey = self.get_survey(surveyEntry.id)
        return survey

    def survey_exists(self, name: str) -> Tuple[bool, int]:
        """
        Determine if a seismic survey with the provided name exists in the users zonevu account.
        :param name:
        :return:
        """
        surveys = self.get_surveys(name)
        exists = len(surveys) > 0
        project_id = surveys[0].id if exists else -1
        return exists, project_id

    def get_survey(self, survey_id: int) -> Optional[SeismicSurvey]:
        """
        Get the seismic survey with the provided system survey id
        :param survey_id:
        :return: a fully loaded seismic survey
        """
        url = "seismic/survey/%s" % survey_id
        item = self.client.get(url)
        project = SeismicSurvey.from_dict(item)
        return project

    def load_survey(self, survey: SeismicSurvey) -> None:
        """
        Fully load the provided partially loaded seismic survey.
        :param survey:
        :return:
        """
        loaded_survey = self.get_survey(survey.id)
        survey.merge_from(loaded_survey)

    def get_registration(self, dataset_id: int) -> SeismicRegistration:
        """
        Get the Segy, coordinate system, and datum for a specified seismic dataset
        :param dataset_id:
        :return: an info data structure
        """
        url = "seismic/registration/%s" % dataset_id
        item = self.client.get(url)
        info = None if item is None else SeismicRegistration.from_dict(item)
        return info

    def get_download_credential(self, dataset: SeismicDataset | int) -> CloudBlobCredential:
        """
        Get a temporary download token for a seismic dataset
        :param dataset: the specified seismic dataset
        :return: A temporary download token
        """
        dataset_id = dataset if isinstance(dataset, int) else dataset.id
        url = f'seismic/dataset/downloadtoken/{dataset_id}'
        item = self.client.get(url, None, False)
        cred = CloudBlobCredential.from_dict(item)
        return cred

    def get_faults(self, survey: SeismicSurvey | SeismicSurveyEntry) -> List[Fault]:
        """
        Get a list of faults for a seismic survey.
        :param survey:
        :return:
        """
        url = f'seismic/faults/{survey.id}'
        items = self.client.get_list(url)
        surveys = [Fault.from_dict(w) for w in items]
        return surveys

    def get_faults_text(self, survey: SeismicSurvey | SeismicSurveyEntry) -> str:
        url = "seismic/faults/%s/text/%s" % ('depth', survey.id)
        text = self.client.get_text(url)
        return text

    def get_fault(self, fault: int | FaultEntry) -> Optional[Fault]:
        """
        Get a list of faults for a seismic survey.
        :param fault: fault system id or fault entry
        :return:
        """
        fault_id = fault.id if isinstance(fault, FaultEntry) else fault
        url = f'seismic/fault/{fault_id}'
        item = self.client.get(url, None, True)
        instance = Fault.from_dict(item)
        return instance

    # Obsolete
    # def get_fault_text(self, fault: int | FaultEntry) -> str:
    #     fault_id = fault.id if isinstance(fault, FaultEntry) else fault
    #     url = "seismic/fault/%s/text/%s" % ('depth', fault_id)
    #     text = self.client.get_text(url)
    #     return text

    def get_horizon_depths(self, horizon: SeisHorizon) -> Optional[ndarray[Tuple[int, int], dtype[float]]]:
        """
        Get the z-values for this seismic horizon
        :param horizon: The seismic horizon for which z-values are desired.
        :return: A floating point array in row-major order of the z-values of the grid.
        """
        url = "seismic/horizon/%s/zvalues/%s" % ('depth', horizon.id)
        if horizon.geometry is not None:
            float_bytes = self.client.get_data(url)
            horizon.z_values = horizon.geometry.grid_info.load_z_values(float_bytes)
            return horizon.z_values
        else:
            return None

    def get_horizon_values(self, horizon: SeisHorizon) -> List[GridValue]:
        """
        Get the z (depth) values of the indicated horizon and convert to an exhaustive list of values
        :param horizon: The SeisHorizon in question
        :return: A list of inline, crossline, x, y, z (in a coordinate data structure) values for every value in the horizon.
        :note: Null values will be -infinity floating point values.
        :note: The x,y coordinates will be in the projected x,y crs of the horizon.geometry
        """
        depths = self.get_horizon_depths(horizon)
        if depths is None:
            return []
        grid_info = horizon.geometry.grid_info
        inlines = grid_info.inline_range
        crosslines = grid_info.crossline_range
        values: List[GridValue] = []
        for inline in range(inlines.start, inlines.stop):
            for crossline in range(crosslines.start, crosslines.stop):
                c = horizon.geometry.get_xyz(inline, crossline, depths)
                value = GridValue(inline, crossline, c)
                values.append(value)
        return values

    def get_horizon_text(self, horizon: SeisHorizon) -> str:
        url = "seismic/horizon/%s/text/%s" % ('depth', horizon.id)
        text = self.client.get_text(url)
        return text




