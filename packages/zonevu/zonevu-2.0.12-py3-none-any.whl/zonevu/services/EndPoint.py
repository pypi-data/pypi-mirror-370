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
Endpoint configuration and API key handling.

Defines :class:`EndPoint` for storing API key, base URL, and SSL verification
settings, with helpers to load credentials from CLI-provided or standard
keyfiles.
"""

from dataclasses import  dataclass
from dataclasses_json import DataClassJsonMixin
import argparse
from .Error import ZonevuError
import os
from pathlib import Path
from typing import ClassVar, Union, Dict


# @dataclass_json
@dataclass
class EndPoint(DataClassJsonMixin):
    """API endpoint configuration including API key, base URL, and verify flag."""
    apikey: str
    verify: bool = False
    base_url: str = 'zonevu.ubiterra.com'
    std_keyfile_name: ClassVar[str] = 'zonevu_keyfile.json'
    key_path: Union[str, Path] | None = None # Path to the key file, if any

    @classmethod
    def from_key(cls, apiKey: str) -> 'EndPoint':
        return cls(apiKey)

    @classmethod
    def from_keyfile(cls) -> 'EndPoint':
        """
        Creates an EndPoint instance from a json file whose path is provided in the command line.
        User either -k or --keyfile to pass in as an argument the path to the key json file.

        Here is an example key json file:

        .. code-block:: json

            {
                "apikey": "xxxx-xxxxx-xxxxx-xxxx"
            }

        :return: An Endpoint instance
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-k", "--keyfile", type=str)  # Path/Filename to key file
        args, unknown = parser.parse_known_args()
        key_path = args.keyfile
        if key_path is None:
            raise ZonevuError.local('the parameter --keyfile must be specified in the command line')

        return cls.from_keyfile_path(key_path)

    @classmethod
    def from_json_dict(cls, json_dict: Dict) -> 'EndPoint':
        return EndPoint.from_dict(json_dict)

    @classmethod
    def from_keyfile_path(cls, key_path: Union[str, Path]) -> 'EndPoint':
        if not os.path.exists(key_path):
            raise ZonevuError.local('keyfile "%s" not found' % key_path)
        with open(key_path, 'r') as file:
            args_json = file.read()
            instance = cls.from_json(args_json)
            instance.key_path = key_path
            return instance

    @classmethod
    def from_std_keyfile(cls) -> 'EndPoint':
        """
        Creates an EndPoint instance from a json file named 'zonevu_keyfile.json, stored in the OS user directory.'

        Here is an example key json file:

        .. code-block:: json

            {
                "apikey": "xxxx-xxxxx-xxxxx-xxxx"
            }

        :return: An Endpoint instance
        """
        std_keyfile_path = Path(Path.home(), cls.std_keyfile_name)
        return cls.from_keyfile_path(std_keyfile_path)