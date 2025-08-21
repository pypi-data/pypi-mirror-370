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
SDK exception hierarchy for server/client errors.
"""

from requests import Response
from strenum import StrEnum
from typing import Any


class ZonevuErrorKinds(StrEnum):
    """Categorizes errors raised by the SDK or returned by the server."""
    Server = 'Server'
    Client = 'Client'


class ResponseError(BaseException):
    """Wraps an HTTP response error for convenience."""
    response: Response
    message: str

    def __init__(self, r: Response):
        self.response = r
        self.message = r.reason


class ZonevuError(BaseException):
    """SDK base exception including message, source, kind, and status code."""
    source: Any
    message: str
    kind: ZonevuErrorKinds
    status_code: int = 0        # Http code

    def __init__(self, msg: str, kind: ZonevuErrorKinds = ZonevuErrorKinds.Client, src: Any = None):
        self.message = msg
        self.kind = kind
        self.source = src

    @staticmethod
    def server(r: Response, add_info: str | None = None) -> 'ZonevuError':
        clean_text = r.text
        msg = f"{r.reason} - {clean_text}" if clean_text else r.reason
        if add_info:
            msg += f"\n{add_info}"
        error = ZonevuError(msg, ZonevuErrorKinds.Server, r)
        error.status_code = r.status_code
        return error

    @staticmethod
    def local(msg: str) -> 'ZonevuError':
        error = ZonevuError(msg, ZonevuErrorKinds.Client)
        return error