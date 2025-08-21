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
Helper utilities for datamodels.

Factory helpers and field encoders/decoders used across dataclasses.
"""

from datetime import datetime
from strenum import StrEnum
from typing import Union
from dataclasses import field
from dataclasses_json import config
from marshmallow import fields


def iso_to_datetime(value: Union[str, None]) -> Union[datetime, None]:
    """
    Parser for parsing ISO times strings to python datetime
    :param value:
    :return:
    """
    if value is None:
        return None
    try:
        date = datetime.fromisoformat(value)
        return date
    except TypeError:
        return None
    except ValueError:
        return None


def date_time_to_iso(value: Union[datetime, None]) -> Union[str, None]:
    """
    Converts python datetime to ISO string
    :param value:
    :return:
    """
    if value is None:
        return None
    return value.isoformat()


isodateFieldConfig = config(
    encoder=date_time_to_iso,
    decoder=iso_to_datetime,
    mm_field=fields.DateTime(format='iso')
)
isodateFieldConfigHide = {
    "encoder": lambda dt: dt.isoformat(),
    "decoder": lambda dt_str: datetime.fromisoformat(dt_str),
}
isodateOptional = field(default=None, metadata=isodateFieldConfig)


def MakeIsodateOptionalField():
    return field(default=None, metadata=isodateFieldConfig)





