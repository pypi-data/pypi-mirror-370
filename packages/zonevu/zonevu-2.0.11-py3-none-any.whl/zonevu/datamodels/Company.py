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

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, config
from typing import Optional


@dataclass
class Company(DataClassJsonMixin):
    #: API Version
    Version: str = ''
    #: ZoneVu server runtime version
    RuntimeVersion: str = '?'
    #: Company name associated with this ZoneVu account
    CompanyName: str = ''
    #: ZoneVu username accessing this ZoneVu accounts
    UserName: str = ''
    #: ZoneVu corporate notice
    Notice: str = ''

    def printNotice(self):
        print()
        print("Zonevu Web API Version %s. Zonevu Server Version %s." % (self.Version, self.RuntimeVersion))
        print(self.Notice)
        print("%s accessing ZoneVu account '%s'" % (self.UserName, self.CompanyName))
        print()


@dataclass
class Division(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    id: int
    name: Optional[str] = None
    parent: Optional['Division'] = None


