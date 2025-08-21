from requests import Response as Response
from strenum import StrEnum
from typing import Any

class ZonevuErrorKinds(StrEnum):
    Server = 'Server'
    Client = 'Client'

class ResponseError(BaseException):
    response: Response
    message: str
    def __init__(self, r: Response) -> None: ...

class ZonevuError(BaseException):
    source: Any
    message: str
    kind: ZonevuErrorKinds
    status_code: int
    def __init__(self, msg: str, kind: ZonevuErrorKinds = ..., src: Any = None) -> None: ...
    @staticmethod
    def server(r: Response, add_info: str | None = None) -> ZonevuError: ...
    @staticmethod
    def local(msg: str) -> ZonevuError: ...
