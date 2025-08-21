import numpy as np
from ...datamodels.DataModel import DataModel as DataModel
from _typeshed import Incomplete
from dataclasses import dataclass, field
from dataclasses_json import config
from strenum import StrEnum
from typing import Iterator

class AppMnemonicCodeEnum(StrEnum):
    NotSet = 'NotSet'
    DEPT = 'DEPT'
    GR = 'GR'
    ROP = 'ROP'
    WOB = 'WOB'
    INCL = 'INCL'
    AZIM = 'AZIM'
    GAS = 'GAS'
    BIT = 'BIT'
    GRDEPT = 'GRDEPT'
    DENS = 'DENS'
    RESS = 'RESS'
    RESM = 'RESM'
    RESD = 'RESD'
    DTC = 'DTC'
    DTS = 'DTS'
    SP = 'SP'
    PHIN = 'PHIN'
    PHID = 'PHID'
    NMR = 'NMR'
    PE = 'PE'
    AGR = 'AGR'
    PHIE = 'PHIE'
    SW = 'SW'
    VSHL = 'VSHL'
    HCP = 'HCP'
    TIME = 'TIME'

@dataclass(eq=False)
class Curve(DataModel):
    description: str | None = ...
    mnemonic: str = ...
    system_mnemonic: AppMnemonicCodeEnum = field(default_factory=Incomplete)
    unit: str | None = ...
    depths: np.ndarray | None = field(default=None, metadata=config(encoder=Incomplete, decoder=Incomplete))
    samples: np.ndarray | None = field(default=None, metadata=config(encoder=Incomplete, decoder=Incomplete))
    def __eq__(self, other: object): ...
    def get_tuples(self) -> Iterator[tuple[float, float]]: ...
