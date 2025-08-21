from _typeshed import Incomplete
from datetime import datetime
from strenum import StrEnum as StrEnum

def iso_to_datetime(value: str | None) -> datetime | None: ...
def date_time_to_iso(value: datetime | None) -> str | None: ...

isodateFieldConfig: Incomplete
isodateFieldConfigHide: Incomplete
isodateOptional: Incomplete

def MakeIsodateOptionalField(): ...
