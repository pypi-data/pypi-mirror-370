from ...datamodels.DataModel import DataModel as DataModel
from dataclasses import dataclass

@dataclass
class NoteCategory(DataModel):
    description: str | None = ...
