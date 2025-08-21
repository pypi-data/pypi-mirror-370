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
Project listing and retrieval service.

Search projects by name, list projects per division, and fetch complete project
objects with optional related data (map layers, wells, geomodels, seismic).
Also includes utilities to locate a project by name and populate it.
"""

import time
import urllib.parse

from .CompanyService import CompanyService
from ..datamodels.Project import Project
from ..datamodels.Project import ProjectEntry
from ..datamodels.wells.Well import Well, WellEntry
from ..datamodels.Company import Division
from ..datamodels.wells.Survey import Survey
from ..datamodels.geomodels.Geomodel import Geomodel, GeomodelEntry
from ..datamodels.seismic.SeismicSurvey import SeismicSurvey, SeismicSurveyEntry
from ..services.MapService import MapService
from .Client import Client
from typing import Tuple, Union, Dict, Optional, Any, List, Set
from strenum import StrEnum


class ProjectData(StrEnum):
    """Flags for which project-related data to load (e.g., layer data)."""
    default = 'default'     # Default behavior is to not load anything extra
    layer_data = 'layer_data'
    all = 'all'             # If specified, load all data, as long as 'default' flag not present


class ProjectDataOptions:
    """Helper to interpret ProjectData flags for loading related data."""
    project_data: Set[ProjectData]

    def __init__(self, project_data: Optional[Set[ProjectData]]):
        self.project_data = project_data or set()

    def _calc_option(self, project_data: ProjectData) -> bool:
        return (project_data in self.project_data or self.all) and self.some

    @property
    def all(self):
        return ProjectData.all in self.project_data

    @property
    def some(self) -> bool:
        return ProjectData.default not in self.project_data

    @property
    def layer_data(self) -> bool:
        return self._calc_option(ProjectData.layer_data)


class ProjectService:
    """Search and fetch projects; optionally populate related domain data."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_projects(self, name: Optional[str] = None, division: Optional[Union[Division, int, str]] = None) -> List[ProjectEntry]:
        """
        Get list of project catalog entries.
        :param name: Optional project name to match. Can be partial.
        :param division:  Optional division identifier (division object or system id or division name)
        :return:  A list of project catalog entries that match. These are not full project objects.
        NOTE: if no search parameters provided, all projects in this zonevu account returned.
        """
        return self.find_by_name(match_token = name, exact_match=False, division = division)

    def get(self, identifier: Optional[Union[ProjectEntry, int, str]], project_data: Optional[Set[ProjectData]] = None) -> Optional[Project]:
        """
        Get a project based on its project catalog entry, its name, or its system id.
        :param identifier:  a project catalog entry, a name, or a system id
        :param project_data: optional directives to preload the project with child data such as map layers.
        :return: return a project object or None
        NOTE: the project object has a list of wells in the project and other information.
        """
        project: Optional[Project] = None
        if isinstance(identifier, ProjectEntry):
            project = self.find_project(identifier.id)
        elif isinstance(identifier, int):
            project =  self.find_project(identifier)
        elif isinstance(identifier, str):
            project =  self.get_first_named(identifier)
        else:
            return None

        if project is None:
            return None

        if project_data is not None:
            self.load_project(project, project_data)
        return project

    def find_by_name(self, match_token: Optional[str] = None, exact_match: Optional[bool] = True, division: Optional[Union[Division, int, str]] = None,
                     page: Optional[int] = 0) -> List[ProjectEntry]:
        """
        Find listing entries a project or projects whose names match a name or that start with a name fragment
        @param match_token: name or name fragment to use to search for projects. If not provided, gets all projects.
        @param exact_match: whether to exactly match the project name.
        @param division: Optional division identifier (division object or system id or division name)
        @param page: page number that is used by this method to retrieve all projects since the limit is 500 per call.
        @return: A list of project entries (summary data structures) that match. These are not full project objects.
        """
        url = "projects"
        max_pages = 50     # This means that it won't do more than 50 round trips to retrieve search result pages.
        params = {"exactmatch": str(exact_match)}
        all_entries: list[ProjectEntry] = []
        more = True
        if match_token is not None:
            params["name"] = urllib.parse.quote_plus(match_token)


        if division is not None:
            division_id = -1
            if isinstance(division, str):
                divisions = CompanyService(self.client).get_divisions()
                division_obj = next((d for d in divisions if d.name.lower() == division.lower()), None)
                if division_obj is None:
                    raise Exception(f'no such division "{division}"')
                division_id = division_obj.id
            elif isinstance(division, Division):
                division_id = division.id
            elif isinstance(division, int):
                division_id = division
            else:
                raise Exception(f'illegal division type encountered')
            params["divisionid"] = division_id

        counter = 0
        while more:
            params["page"] = str(page)
            wells_response = self.client.get_dict(url, params, False)
            items = wells_response['Projects']
            more = wells_response['More']
            page = wells_response['Page']
            entries = [ProjectEntry.from_dict(w) for w in items]
            all_entries.extend(entries)
            counter += 1
            if counter > max_pages:
                break               # Safety check. Limits us to 500 iterations, which is 250,000 wells.
            time.sleep(0.050)       # Pause for 50 ms so as not to run into trouble with webapi throttling.

        return all_entries

    def get_first_named(self, name: str) -> Optional[Project]:
        """
        Get first project with the specified name, populate it, and return it.
        :param name: name of project to get
        :return:
        """
        project_entries = self.find_by_name(name)
        if len(project_entries) == 0:
            return None
        entry = project_entries[0]
        project = self.find_project(entry.id)
        return project

    def project_exists(self, name: str) -> Tuple[bool, int]:
        projects = self.find_by_name(name)
        exists = len(projects) > 0
        project_id = projects[0].id if exists else -1
        return exists, project_id

    def exists(self, identifier: Union[str, int]) -> bool:
        if isinstance(identifier, int):
            project = self.find_project(identifier)
            return project is not None
        elif isinstance(identifier, str):
            projects = self.find_by_name(identifier)
            exists = len(projects) > 0
            return exists

    def find_project(self, project_id: int) -> Optional[Project]:
        url = "project/%s" % project_id
        item = self.client.get(url)
        if item is None:
            return None
        project = Project.from_dict(item)
        return project

    def load_project(self, project: Project, project_data: Optional[Set[ProjectData]]) -> None:
        options = ProjectDataOptions(project_data)
        loaded_project = self.find_project(project.id)
        project.merge_from(loaded_project)

        if options.layer_data:
            try:
                map_svc = MapService(self.client)
                for layer in project.layers:
                    map_svc.load_user_layer(layer)
            except Exception as err:
                print('Could not load project layers because %s' % err)

    def create_project(self, project: Project) -> None:
        """
        Create a project.
        @param project: project object to be added.
        @return: Throw a ZonevuError if method fails
        """
        url = "project/create"
        item = self.client.post(url, project.to_dict())
        server_project = Survey.from_dict(item)
        project.copy_ids_from(server_project)

    def delete_project(self, identifier: Union[int, ProjectEntry, Project], delete_code: str) -> None:
        project_id: int = identifier.id if isinstance(identifier, ProjectEntry) or isinstance(identifier, Project) else int(identifier)
        url = "project/delete/%s" % project_id
        url_params: Dict[str, Any] = {"deletecode": delete_code}
        self.client.delete(url, url_params)

    def add_well(self, project: Union[Project, ProjectEntry, int], well: Union[Well, WellEntry, int]) -> None:
        """
        Add a well to a project
        @param project:
        @param well:
        @return:
        """
        project_id = project if isinstance(project, int) else project.id
        well_id = well if isinstance(well, int) else well.id
        url = "project/%s/addwell/%s" % (project_id, well_id)
        # params = [project.id, well.id]
        self.client.post(url, {}, False)

    def add_wells(self, project: Union[Project, ProjectEntry, int], wells: List[Union[Well, WellEntry, int]], update_boundary: bool = True) -> None:
        """
        Add a well to a project
        @param project:
        @param wells:
        @:param update_boundary: if True, adjust project boundary to include wells
        @return:
        """
        project_id = project if isinstance(project, int) else project.id
        well_ids: List[int] = [well if isinstance(well, int) else well.id for well in wells]
        url = f'project/addwells/{project_id}'
        self.client.post(url, well_ids, False, {"updateboundary": update_boundary})

    def remove_well(self, project: Union[Project, ProjectEntry], well: Union[Well, WellEntry]) -> None:
        """
        Remove a well from a project
        @param project:
        @param well:
        @return:
        """
        url = "project/%s/removewell/%s" % (project.id, well.id)
        self.client.post(url, {}, False)

    def add_geomodel(self, project: Union[Project, ProjectEntry], geomodel: Union[Geomodel, GeomodelEntry]) -> None:
        """
        Associate a geomodel with a project
        @param project:
        @param geomodel:
        @return:
        """
        url = "project/%s/linkgeomodel/%s" % (project.id, geomodel.id)
        self.client.post(url, {}, False)

    def remove_geomodel(self, project: Union[Project, ProjectEntry], geomodel: Union[Geomodel, GeomodelEntry]) -> None:
        """
        Remove the association of a geomodel with a project
        @param project:
        @param geomodel:
        @return:
        """
        url = "project/%s/unlinkgeomodel/%s" % (project.id, geomodel.id)
        self.client.post(url, {}, False)

    def add_seismicsurvey(self, project: Union[Project, ProjectEntry], survey: Union[SeismicSurvey, SeismicSurveyEntry]) -> None:
        """
        Associate a geomodel with a project
        @param project:
        @param survey:
        @return:
        """
        url = "project/%s/linkseismic/%s" % (project.id, survey.id)
        self.client.post(url, {}, False)

    def remove_seismicsurvey(self, project: Union[Project, ProjectEntry], survey: Union[SeismicSurvey, SeismicSurveyEntry]) -> None:
        """
        Remove the association of a geomodel with a project
        @param project:
        @param survey:
        @return:
        """
        url = "project/%s/unlinkseismic/%s" % (project.id, survey.id)
        self.client.post(url, {}, False)

    # TODO: add method for setting the strat column on the project.