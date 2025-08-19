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
#
#
#
#
#
#

"""
This module contains the Zonevu class, which is the main entry point for interacting with the ZoneVu API.
"""

import sys
from .datamodels.Company import Company
from .datamodels.geospatial.Enums import DistanceUnitsEnum, DepthUnitsEnum, UnitsSystemEnum
from .services.Error import ZonevuError
from .services.EndPoint import EndPoint
from .services.WellService import WellService
from .services.SurveyService import SurveyService
from .services.Client import Client
from .services.CompanyService import CompanyService
from .services.WelllogService import WelllogService
from .services.GeosteeringService import GeosteeringService
from .services.ProjectService import ProjectService
from .services.CoordinatesService import CoordinatesService
from .services.GeomodelService import GeomodelService
from .services.MapService import MapService
from .services.DocumentService import DocumentService
from .services.StratService import StratService
from .services.SeismicService import SeismicService
from .services.CompletionsService import CompletionsService
from .services.Utils import Naming
from pathlib import Path
from .services.WelltopService import WelltopService


class Zonevu:
    """
    The main entry point for interacting with the ZoneVu API.

    This class provides access to all the available services (wells, surveys, etc.)
    and handles authentication and configuration. It should be instantiated using one
    of the class methods like `init_from_apikey` or `init_from_keyfile`.
    """

    # Represents the ZoneVu version 1.1 API
    # private
    _client: Client
    company: Company

    def __init__(self, end_point: EndPoint, units_system: UnitsSystemEnum = UnitsSystemEnum.US):
        # Make sure we are running in python 3.11 or later
        correct_python = sys.version_info.major >= 3 and sys.version_info.minor >= 10
        if not correct_python:
            raise ZonevuError.local("Python version is too old. The ZoneVu python library requires python "
                                    "version 3.10 or later.")
        self._client = Client(end_point, units_system)

    @classmethod
    def init_from_apikey(cls, api_key: str, units_system: UnitsSystemEnum = UnitsSystemEnum.US) -> 'Zonevu':
        """Initializes the Zonevu client using a direct API key.

        :param api_key: The API key for authenticating with the ZoneVu service.
        :type api_key: str
        :param units_system: The system of units to use (US or Metric). Defaults to US.
        :type units_system: UnitsSystemEnum
        :return: An initialized Zonevu client instance.
        :rtype: Zonevu
        """
        endpoint = EndPoint(api_key)
        zonevu = cls(endpoint, units_system)  # Get zonevu python client
        zonevu.print_notice()  # Check that we can talk to ZoneVu server and print notice.
        return zonevu

    @classmethod
    def init_from_keyfile(cls, units_system: UnitsSystemEnum = UnitsSystemEnum.US) -> 'Zonevu':
        """
        Instantiates Zonevu from a keyfile path specified as a script argument.

        See EndPoint.from_keyfile() for details on how to set up a keyfile.

        :param units_system: The system of units to use (US or Metric). Defaults to US.
        :type units_system: UnitsSystemEnum
        :return: A reference to the initialized Zonevu instance.
        :rtype: Zonevu
        """
        endpoint = EndPoint.from_keyfile()
        zonevu = cls(endpoint, units_system)  # Get zonevu python client
        zonevu.print_notice()       # Check that we can talk to ZoneVu server and print notice.
        return zonevu

    @classmethod
    def init_from_std_keyfile(cls, units_system: UnitsSystemEnum = UnitsSystemEnum.US) -> 'Zonevu':
        """Initializes Zonevu from a standard keyfile in the user's home directory.

        This method looks for a file named 'zonevu_keyfile.json' in the user's
        home directory.

        Example keyfile format:

        .. code-block:: json

           {
               "apikey": "xxxx-xxxxx-xxxxx-xxxx"
           }

        :param units_system: The system of units to use (US or Metric). Defaults to US.
        :type units_system: UnitsSystemEnum
        :return: An initialized Zonevu client instance.
        :rtype: Zonevu
        """
        endpoint = EndPoint.from_std_keyfile()
        zonevu = cls(endpoint, units_system)  # Get zonevu python client
        zonevu.print_notice()  # Check that we can talk to ZoneVu server and print notice.
        return zonevu

    def append_header(self, key: str, value: str) -> None:
        self._client.append_header(key, value)

    # Services -- use these properties to get an instance of a particular zonevu web api service.
    @property
    def company_service(self) -> CompanyService:
        return CompanyService(self._client)

    @property
    def well_service(self) -> WellService:
        return WellService(self._client)

    @property
    def welllog_service(self) -> WelllogService:
        return WelllogService(self._client)

    @property
    def welltop_service(self) -> WelltopService:
        return WelltopService(self._client)

    @property
    def survey_service(self) -> SurveyService:
        return SurveyService(self._client)

    @property
    def distance_units(self) -> DistanceUnitsEnum:
        return self._client.distance_units

    @distance_units.setter
    def distance_units(self, new_value: DistanceUnitsEnum):
        self._client._distance_units = new_value

    @property
    def depth_units(self) -> DepthUnitsEnum:
        return self._client.depth_units

    @depth_units.setter
    def depth_units(self, new_value: DepthUnitsEnum):
        self._client._depth_units = new_value

    def units_system(self) -> UnitsSystemEnum:
        return self._client._units_system

    @property
    def geosteering_service(self) -> GeosteeringService:
        return GeosteeringService(self._client)

    @property
    def project_service(self) -> ProjectService:
        return ProjectService(self._client)

    @property
    def coordinates_service(self) -> CoordinatesService:
        return CoordinatesService(self._client)

    @property
    def formation_service(self) -> StratService:
        return StratService(self._client)

    @property
    def geomodel_service(self) -> GeomodelService:
        return GeomodelService(self._client)

    @property
    def map_service(self) -> MapService:
        return MapService(self._client)

    @property
    def document_service(self) -> DocumentService:
        return DocumentService(self._client)

    @property
    def strat_service(self) -> StratService:
        return StratService(self._client)

    @property
    def seismic_service(self) -> SeismicService:
        return SeismicService(self._client)

    @property
    def completions_service(self) -> CompletionsService:
        return CompletionsService(self._client)

    # High level API
    # Company
    def get_info(self) -> Company:
        """
        Gets information about the company, user, and ZoneVu server version.

        :return: An object containing company, user, and version information.
        :rtype: ~zonevu.datamodels.Company.Company
        """
        self.company = self.company_service.get_info()
        return self.company

    def print_notice(self) -> None:
        info = self.get_info()
        print()
        print("Zonevu Python SDK Version %s" % self._client.version)
        print("Zonevu Web API Version %s" % info.Version)
        print("Zonevu Server Version %s." % info.RuntimeVersion)

        print(info.Notice)
        print("%s accessing ZoneVu account '%s' at %s" % (info.UserName, info.CompanyName, self._client.host))
        print()

    @property
    def archive_directory(self) -> Path:
        host = self._client.host
        qualifier = 'dev' if host.startswith('dev') else 'local' if host.startswith('local') else ''
        zonevu_name = 'zonevu%s' % qualifier
        root = Naming.create_dir_under_home(zonevu_name) / Naming.make_safe_name(self.company.CompanyName) / 'archive'
        return root

    @property
    def wells_directory(self) -> Path:
        wells_dir = self.archive_directory / 'wells'
        return wells_dir