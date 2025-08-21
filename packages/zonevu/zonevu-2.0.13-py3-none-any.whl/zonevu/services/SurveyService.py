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
Wellbore survey service.

List, retrieve, and load wellbore trajectory surveys and their stations for a
given wellbore. Supports adding new surveys to a wellbore.
"""

from ..datamodels.wells.Survey import Survey
from ..datamodels.wells.Station import Station
from ..datamodels.wells.Wellbore import Wellbore
from .Client import Client
from typing import List


class SurveyService:
    """List, find, and load deviation surveys and stations for a wellbore."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_surveys(self, wellbore_id: int) -> list[Survey]:
        url = "surveys/%s" % wellbore_id
        items = self.client.get_list(url)
        surveys = [Survey.from_dict(w) for w in items]
        return surveys

    def find_survey(self, survey_id: int) -> Survey:
        url = "survey/%s" % survey_id
        item = self.client.get(url)
        survey = Survey.from_dict(item)
        return survey

    def load_survey(self, survey: Survey) -> Survey:
        full_survey = self.find_survey(survey.id)
        for field, value in vars(full_survey).items():
            setattr(survey, field, value)
        return survey

    def load_surveys(self, wellbore: Wellbore) -> list[Survey]:
        surveys = self.get_surveys(wellbore.id)
        wellbore.surveys = []
        for survey in surveys:
            complete_survey = self.find_survey(survey.id)
            wellbore.surveys.append(complete_survey)
        return surveys

    def add_survey(self, wellbore: Wellbore, survey: Survey) -> None:
        """
        Adds a survey to a wellbore. Updates the passed in survey with zonevu ids.
        @param wellbore: Zonevu id of wellbore to which survey will be added.
        @param survey: Survey object
        @return: Throw a ZonevuError if method fails
        """
        url = "survey/add/%s" % wellbore.id
        item = self.client.post(url, survey.to_dict())
        server_survey = Survey.from_dict(item)
        survey.copy_ids_from(server_survey)

    def delete_survey(self, survey: Survey, delete_code: str) -> None:
        url = "survey/delete/%s" % survey.id
        self.client.delete(url, {"deletecode": delete_code})

    def add_stations(self, survey: Survey, stations: List[Station]) -> List[Station]:
        url = "survey/add-stations/%s" % survey.id
        data = [s.to_dict() for s in stations]
        items = self.client.post(url, data)
        if isinstance(items, List):
            surveys_server = [Station.from_dict(w) for w in items]
            return surveys_server
        return []

    def update_survey(self, survey: Survey) -> None:
        """
        Updates a survey. Updates the passed in survey with zonevu ids.
        @param survey: Survey object
        @return: Throw a ZonevuError if method fails
        """
        url = "survey/update"
        item = self.client.post(url, survey.to_dict())
        server_survey = Survey.from_dict(item)
        survey.copy_ids_from(server_survey)



