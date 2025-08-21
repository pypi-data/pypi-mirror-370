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

"""
HTTP client wrapper with retry/backoff and auth header management.
"""

import json
import requests
import urllib.parse
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
from typing import Union, Dict, Optional, Any, List
from pathlib import Path
from .EndPoint import EndPoint
from strenum import StrEnum
from .Error import ZonevuError
import importlib.metadata as meta

from ..datamodels.geospatial.Enums import DistanceUnitsEnum, DepthUnitsEnum, UnitsSystemEnum


class Client:
    """HTTP client handling auth, base URL, headers, and JSON requests."""

    # private
    _headers: Dict[str, str] = {}     # Custom HTTP headers (including Auth header)
    _verify = True      # Whether to check SSL certificate
    _baseurl: str = ''       # ZoneVu instance to call
    _units_system: UnitsSystemEnum    # Units system to use when requesting data
    _distance_units: Optional[DistanceUnitsEnum] = None  # Overrides distance units in _units_system
    _depth_units: Optional[DepthUnitsEnum] = None  # Overrides depth units in _units_system
    _session: Session
    host: str
    version: str
    row_version_key: str = "rowversion"
    key_path: Union[str, Path] | None = None # Path to the key file, if any

    def __init__(self, endPoint: EndPoint, units: UnitsSystemEnum = UnitsSystemEnum.US):
        # Access version number of this script
        try:
            self.version = meta.version("zonevu")
        except meta.PackageNotFoundError as file_err:
            self.version = '(Unable to access)'

        self.apikey = endPoint.apikey
        self.host = host = endPoint.base_url
        self._verify = endPoint.verify
        self.key_path = endPoint.key_path
        if not self._verify:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # type: ignore

        self._baseurl = "https://%s/api/v1.1" % host
        agent = f"ZonevuPythonSDK/{self.version}"
        self._headers = {'authorization': 'bearer ' + endPoint.apikey, 'user-agent': agent}
        self._units_system = units

        # Setup backoff strategy
        self._session = requests.Session()
        # Define the retry strategy  status_forcelist=[429, 500, 502, 503, 504]
        retry_strategy = Retry(
            total=5,                 # Total number of retries status_forcelist=[429, 500, 502, 503, 504] to allow
            status_forcelist=[429],  # List of status codes to retry on
            allowed_methods=["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"],  # List of methods to retry on
            backoff_factor=1  # A factor to multiply the delay between retries
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

    @property
    def distance_units(self) -> DistanceUnitsEnum:
        if self._distance_units is None:
            return DistanceUnitsEnum.Feet if self._units_system == UnitsSystemEnum.US else DistanceUnitsEnum.Meters
        else:
            return self._distance_units

    @distance_units.setter
    def distance_units(self, new_value: DistanceUnitsEnum):
        self._distance_units = new_value

    @property
    def depth_units(self) -> DepthUnitsEnum:
        if self._depth_units is None:
            return DepthUnitsEnum.Feet if self._units_system == UnitsSystemEnum.US else DepthUnitsEnum.Meters
        else:
            return self._depth_units

    @depth_units.setter
    def depth_units(self, new_value: DepthUnitsEnum):
        self._depth_units = new_value

    def append_header(self, key: str, value: str) -> None:
        self._headers[key] = value

    def make_url(self, relativeUrl: str, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True):
        if query_params is None:
            query_params = {}
        url = "%s/%s" % (self._baseurl, relativeUrl)
        if include_units:
            query_params['options.distanceunits'] = str(self.distance_units)
            query_params['options.depthunits'] = str(self.depth_units)

        for index, (key, value) in enumerate(query_params.items()):
            separator = '?' if index == 0 else '&'

            # If this is a row version string, URL encode it.
            # Note: the server will still be able to decode it since .NET can auto-handle decoding url safe base 64 strings.
            if key == self.row_version_key:
                value = value.replace('+', '-').replace('/', '_')
                value = urllib.parse.quote(value)

            fragment = "%s%s=%s" % (separator, key, value)
            url += fragment

        return url

    def call_api_get(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> Response:
        if query_params is None:
            query_params = {}
        url = self.make_url(relativeUrl, query_params, include_units)

        # r = requests.get(url, headers=self._headers, verify=self._verify)
        r = self._session.get(url, headers=self._headers, verify=self._verify)
        try:
            textJson = json.loads(r.text)
            textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        except Exception as err:
            pass
        return r

    def get(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> Union[Dict, List, None]:
        r = self.call_api_get(relativeUrl, query_params, include_units)
        self.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def get_list(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> List:
        json_obj = self.get(relativeUrl, query_params, include_units)
        if json_obj is None:
            return []
        if not isinstance(json_obj, List):
            raise ZonevuError.local('Did not get expected json list structure from server')
        return json_obj

    def get_float(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> float:
        json_obj = self.get(relativeUrl, query_params, include_units)
        if json_obj is None:
            raise ZonevuError.local('Did not get a float from the server, rather got a None')
        if not isinstance(json_obj, float):
            raise ZonevuError.local('Did not get expected float from server')
        return float(json_obj)

    def get_dict(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> Dict:
        json_obj = self.get(relativeUrl, query_params, include_units)
        if json_obj is None:
            return {}
        if not isinstance(json_obj, Dict):
            raise ZonevuError.local('Did not get expected json dict structure from server')
        return json_obj

    def get_text(self, relativeUrl: str, encoding: str = 'utf-8', query_params: Optional[Dict[str, Any]] = None) -> str:
        if query_params is None:
            query_params = {}
        url = self.make_url(relativeUrl, query_params)
        r = self._session.get(url, headers=self._headers, verify=self._verify)
        self.assert_ok(r)
        r.encoding = encoding  # We do this because python assumes strings are utf-8 encoded.
        ascii_text = r.text

        # Test
        r.encoding = 'utf-8'
        utf8_text = r.text

        same = ascii_text == utf8_text

        return ascii_text

    def get_data(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None) -> bytes:
        r = self.call_api_get(relativeUrl, query_params)
        self.assert_ok(r)
        return r.content

    def call_api_post(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                      query_params: Optional[Dict[str, Any]] = None) -> Response:
        url = self.make_url(relativeUrl, query_params, include_units)
        r = self._session.post(url, headers=self._headers, verify=self._verify, json=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def post(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
             query_params: Optional[Dict[str, Any]] = None) -> Union[Dict, List, None]:
        r = self.call_api_post(relativeUrl, data, include_units, query_params)
        self.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def post_return_list(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                         query_params: Optional[Dict[str, Any]] = None) -> List:
        json_obj = self.post(relativeUrl, data, include_units, query_params)
        if json_obj is None:
            return []
        if not isinstance(json_obj, List):
            raise ZonevuError.local('Did not get expected json list structure from server')
        return json_obj

    def post_return_dict(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                         query_params: Optional[Dict[str, Any]] = None) -> Dict:
        json_obj = self.post(relativeUrl, data, include_units, query_params)
        if json_obj is None:
            return {}
        if not isinstance(json_obj, Dict):
            raise ZonevuError.local('Did not get expected json list structure from server')
        return json_obj

    def call_api_post_data(self, relativeUrl: str, data: Union[bytes, str, Dict],
                           content_type: Optional[str] = None) -> Response:
        url = self.make_url(relativeUrl, None)
        the_headers = self._headers.copy()
        if content_type is not None:
            the_headers["content-type"] = content_type
        r = self._session.post(url, headers=the_headers, verify=self._verify, data=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def post_data(self, relativeUrl, data: Union[bytes, str, dict], content_type: Optional[str] = None) -> None:
        r = self.call_api_post_data(relativeUrl, data, content_type)
        self.assert_ok(r)

    def call_api_delete(self, relativeUrl: str, query_params: Optional[Dict[str, Any]] = None) -> Response:
        url = self.make_url(relativeUrl, query_params)
        r = self._session.delete(url, headers=self._headers, verify=self._verify)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def delete(self, relativeUrl: str, query_params: Optional[Dict[str, Any]] = None) -> None:
        r = self.call_api_delete(relativeUrl, query_params)
        self.assert_ok(r)

    def call_api_patch(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                       query_params: Optional[Dict[str, Any]] = None) -> Response:
        url = self.make_url(relativeUrl, query_params, include_units)
        r = self._session.patch(url, headers=self._headers, verify=self._verify, json=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def patch(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
              query_params: Optional[Dict[str, Any]] = None) -> Union[Dict, List, None]:
        r = self.call_api_patch(relativeUrl, data, include_units, query_params)
        self.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def assert_ok(self, r: Response):
        if not r.ok:
            add_info = None
            if r.status_code == 403:
                if self.key_path is not None:
                    add_info = f'Check your API key in {self.key_path}'
            # raise ResponseError(r)
            raise ZonevuError.server(r, add_info)
