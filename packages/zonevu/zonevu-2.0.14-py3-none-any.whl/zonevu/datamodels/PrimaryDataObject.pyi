import abc
from .DataModel import DataModel as DataModel, DataObjectTypeEnum as DataObjectTypeEnum
from .Document import Document as Document
from abc import ABC, abstractmethod
from pathlib import Path

class PrimaryDataObject(DataModel, ABC, metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def full_name(self) -> str: ...
    @property
    @abstractmethod
    def data_object_type(self) -> DataObjectTypeEnum: ...
    def create_doc(self, file_path: Path, file_size: int) -> Document: ...
    def get_documents(self) -> list[Document]: ...
