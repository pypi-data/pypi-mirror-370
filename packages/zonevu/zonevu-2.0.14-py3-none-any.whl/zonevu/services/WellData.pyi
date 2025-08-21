from strenum import StrEnum

class WellData(StrEnum):
    default = 'default'
    logs = 'logs'
    curves = 'curves'
    surveys = 'surveys'
    tops = 'tops'
    fracs = 'fracs'
    geosteering = 'geosteering'
    notes = 'notes'
    all = 'all'

class WellDataOptions:
    well_data: set[WellData]
    def __init__(self, well_data: set[WellData] | None) -> None: ...
    @property
    def all(self): ...
    @property
    def some(self) -> bool: ...
    @property
    def welllogs(self) -> bool: ...
    @property
    def surveys(self) -> bool: ...
    @property
    def curves(self) -> bool: ...
    @property
    def tops(self) -> bool: ...
    @property
    def fracs(self) -> bool: ...
    @property
    def geosteering(self) -> bool: ...
    @property
    def notes(self) -> bool: ...
