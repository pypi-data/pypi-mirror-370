from ...datamodels.DataModel import DataModel as DataModel
from dataclasses import dataclass
from strenum import PascalCaseStrEnum, StrEnum

class GeoPeriodEnum(StrEnum):
    Unset = ('Unset',)
    Quaternary = ('Quaternary',)
    Neogene = ('Neogene',)
    Paleogene = ('Paleogene',)
    Cretaceous = ('Cretaceous',)
    Jurassic = ('Jurassic',)
    Triassic = ('Triassic',)
    Permian = ('Permian',)
    Carboniferous = ('Carboniferous',)
    Devonian = ('Devonian',)
    Silurian = ('Silurian',)
    Ordovician = ('Ordovician',)
    Cambrian = ('Cambrian',)
    Precambrian = 'Precambrian'

class LithologyTypeEnum(PascalCaseStrEnum):
    Unset = ('Unset',)
    Sandstone = ('Sandstone',)
    Shale = ('Shale',)
    Limestone = ('Limestone',)
    Dolomite = ('Dolomite',)
    Chalk = ('Chalk',)
    Marl = ('Marl',)
    MudstoneRich = ('MudstoneRich',)
    MudstoneLean = ('MudstoneLean',)
    Bentonite = ('Bentonite',)
    Coal = ('Coal',)
    Chert = ('Chert',)
    Anhydrite = ('Anhydrite',)
    Siltstone = ('Siltstone',)
    ShalySand = ('ShalySand',)
    SandstoneBedded = ('SandstoneBedded',)
    CalcareousSandstone = ('CalcareousSandstone',)
    SandyShale = ('SandyShale',)
    ShalyLimestone = ('ShalyLimestone',)
    SandyLimestone = ('SandyLimestone',)
    ShalyDolostone = ('ShalyDolostone',)
    SandyDolostone = ('SandyDolostone',)
    LimestoneShale = ('LimestoneShale',)
    ShaleSandstone = ('ShaleSandstone',)
    SandstoneShale = ('SandstoneShale',)
    ShaleLimestone = ('ShaleLimestone',)
    Salt = ('Salt',)
    ChertyShale = ('ChertyShale',)
    Breccia = ('Breccia',)
    Conglomerate = ('Conglomerate',)
    Basalt = ('Basalt',)
    Granite = ('Granite',)
    Igneous = ('Igneous',)
    Tuff = ('Tuff',)
    Crosshatch = 'Crosshatch'
    SiltySandstone = 'SiltySandstone'
    SiltyShale = 'SiltyShale'
    SiltyLimestone = 'SiltyLimestone'
    SiltyDolostone = 'SiltyDolostone'
    Gypsum = 'Gypsum'

@dataclass
class Formation(DataModel):
    member_name: str | None = ...
    strat_col_order: int = ...
    symbol: str = ...
    color: str | None = ...
    description: str | None = ...
    period: GeoPeriodEnum | None = ...
    lithology_type: LithologyTypeEnum | None = ...
