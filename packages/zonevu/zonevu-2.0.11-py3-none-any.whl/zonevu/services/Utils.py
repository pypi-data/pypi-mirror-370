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

import argparse
import re
from pathlib import Path
from typing import Union, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json


class Input:
    @staticmethod
    def get_name_from_args(title: str = '') -> str:
        # Get a name from argument list or ask user for it
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--name", type=str)  # Input well
        args, unknown = parser.parse_known_args()
        name = args.name

        # Not found in argument list so ask user
        if name is None:
            name = input("Enter %s name: " % title)  # Get name from user in console

        return name


class StringUtils:
    @staticmethod
    def is_none_or_whitespace(s: Union[str, None]) -> bool:
        return s is None or s.strip() == ''

    @staticmethod
    def has_chars(s: Union[str, None]) -> bool:
        return not StringUtils.is_none_or_whitespace(s)


class Naming:
    @staticmethod
    def slugify(name: str) -> str:
        title = name.lower()
        # Replace any non-alphanumeric character with a hyphen
        title = re.sub(r'\W+', '-', title)
        # Remove any leading or trailing hyphens
        slug = title.strip('-')
        # Assign the result to a variable named slug
        return slug

    @staticmethod
    def replace_forbidden_symbols(filename: str) -> str:
        forbidden = '\\/:*?"<>|'
        return ''.join([symbol for symbol in filename if symbol not in forbidden])

    @staticmethod
    def make_safe_name(name: str, identifier: Optional[Union[str, int]] = None) -> str:
        name_safe = Naming.replace_forbidden_symbols(name)
        name_safe = Naming.slugify(name_safe)
        if identifier is not None:
            name_safe = '%s-%s' % (name_safe, identifier)
        return name_safe

    @staticmethod
    def make_safe_name_default(name: Union[str, None], default: str, identifier: Optional[Union[str, int]] = None) -> str:
        name = name if name is not None and len(name) > 0 else default
        name_safe = Naming.replace_forbidden_symbols(name)
        name_safe = Naming.slugify(name_safe)
        if identifier is not None:
            name_safe = '%s-%s' % (name_safe, identifier)
        return name_safe

    @staticmethod
    def build_safe_entity_dir(parent_dir: Union[Path, str], entity_name: str,
                              identifier: Optional[Union[str, int]] = None) -> Path:
        entity_name_safe = Naming.make_safe_name(entity_name, identifier)
        path = Path(parent_dir, entity_name_safe)
        Naming.check_dir(path)
        return path

    @staticmethod
    def check_dir(dir_path: Path):
        if not dir_path.is_dir():
            dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def create_dir_under_home(dir_name: str) -> Path:
        # Join the home directory with the given directory name
        new_dir = Path.home() / dir_name
        Naming.check_dir(new_dir)
        return new_dir

@dataclass_json
@dataclass
class CloudBlobCredential:
    url: str  # Azure storage account base URL
    container: str  # Azure storage container name for ZoneVu data
    token: str  # Azure storage account authorization key
    path: Optional[str] = None  # Relative path below url to a blob if this is specific to a single blob

    @property
    def full_url(self) -> str:
        url = Path(self.url)
        path = self.path
        if path is None:
            return str(url / self.container)
        return str(url / self.container / path)


