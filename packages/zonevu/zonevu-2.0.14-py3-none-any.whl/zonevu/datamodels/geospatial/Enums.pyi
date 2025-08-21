from strenum import StrEnum

class UnitsSystemEnum(StrEnum):
    Metric = 'Metric'
    US = 'US'

class DistanceUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    FeetUS = 'FeetUS'
    @classmethod
    def units_system(cls, units: DistanceUnitsEnum) -> UnitsSystemEnum: ...

class DepthUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    @classmethod
    def units_system(cls, units: DepthUnitsEnum) -> UnitsSystemEnum: ...
