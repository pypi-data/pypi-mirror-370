import numpy as np
from ...datamodels.DataModel import DataModel as DataModel
from ...datamodels.geosteering.Conditioning import Conditioning as Conditioning
from ...datamodels.wells.Curve import AppMnemonicCodeEnum as AppMnemonicCodeEnum
from _typeshed import Incomplete
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, config
from strenum import StrEnum

class CurveGroupRoleEnum(StrEnum):
    Image = 'Image'
    Litho = 'Litho'
    Splice = 'Splice'

@dataclass
class CurveGroupParam(DataClassJsonMixin):
    dataclass_json_config = ...
    id: int
    curve_id: int
    conditioning: Conditioning | None

@dataclass
class CurveGroup(DataModel):
    role: CurveGroupRoleEnum = ...
    system_mnemonic: AppMnemonicCodeEnum = ...
    curve_ids: list[int] = field(default_factory=list[int])
    curve_channel_params: list[CurveGroupParam] = field(default_factory=list[CurveGroupParam])
    depths: np.ndarray | None = field(default=None, metadata=config(encoder=Incomplete, decoder=Incomplete))
    samples: np.ndarray | None = field(default=None, metadata=config(encoder=Incomplete, decoder=Incomplete))
