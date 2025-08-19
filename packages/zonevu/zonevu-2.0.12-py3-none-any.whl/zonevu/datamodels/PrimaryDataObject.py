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
Primary data object base class.

Defines identity, ownership, and type for top-level ZoneVu entities and
provides merge/change utilities.
"""

from typing import List
from abc import ABC, abstractmethod
from pathlib import Path
from .DataModel import DataModel, DataObjectTypeEnum
from .Document import Document


class PrimaryDataObject(DataModel, ABC):
    """
    Base class for Well, Project, Geomodel, Seimsic survey
    """
    # documents_dir: ClassVar[str] = 'documents'

    @property
    @abstractmethod
    def full_name(self) -> str:
        pass

    @property
    @abstractmethod
    def data_object_type(self) -> DataObjectTypeEnum:
        pass

    def create_doc(self, file_path: Path, file_size: int) -> Document:
        doc = Document(name=file_path.name, file_size=file_size,
                       owner_type=self.data_object_type, owner_id=self.id, path=file_path.as_posix())
        return doc






    # @property
    # @abstractmethod
    # def archive_local_dir_path(self) -> Path:
    #     pass
    #
    # @property
    # @abstractmethod
    # def archive_local_file_path(self) -> Path:
    #     pass

    def get_documents(self) -> List[Document]:
        return []

    # def save(self, storage: Storage) -> None:
    #     # Erase all files in this well folder to avoid inconsistent data
    #     self.clear_dir(storage)
    #     self.save_json(storage)  # Save primary data object json

    # region Support for saving wells to files and to cloud storage
    # @property
    # def safe_name(self) -> str:
    #     """
    #     A unique name for this data object that includes the system id, that is safe to use for file systems & cloud storage.
    #     Example: 'Smith A-1' becomes 'smith-a-1'
    #     :return:
    #     """
    #     return Naming.make_safe_name(self.full_name, self.id)
    #
    # def exists(self, storage: Storage) -> bool:
    #     obj_json_path = self.archive_local_file_path  # Local path for blob itself
    #     return storage.exists(obj_json_path)
    #
    # def tags(self, storage: Storage) -> Optional[Dict[str, str]]:
    #     obj_json_path = self.archive_local_file_path  # Local path for blob itself
    #     return storage.tags(obj_json_path)
    #
    # def version(self, storage: Storage) -> Optional[str]:
    #     obj_json_path = self.archive_local_file_path  # Local path for blob itself
    #     return storage.version(obj_json_path)
    #
    # def current(self, storage: Storage) -> bool:
    #     obj_json_path = self.archive_local_file_path  # Local path for blob itself
    #     stored_version = storage.version(obj_json_path)
    #     current = self.row_version is not None and self.row_version == stored_version
    #     return current
    #
    # def clear_dir(self, storage: Storage) -> None:
    #     # Erase all files in this data object folder to avoid inconsistent data
    #     existing_blobs = storage.list(self.archive_local_dir_path)
    #     for existing_blob in existing_blobs:
    #         storage.delete(existing_blob)
    #
    # def save_json(self, storage: Storage) -> None:
    #     json_text = json.dumps(self.to_dict())
    #     json_bytes = json_text.encode('utf-8')
    #     storage.save(self.archive_local_file_path, json_bytes, {Storage.VersionTag: self.row_version})
    #
    # @staticmethod
    # def retrieve_json(blob_path: Path, storage: Storage) -> Any:
    #     obj_bytes = storage.retrieve(blob_path)
    #     obj_json_text = obj_bytes.decode('utf-8')
    #     json_obj = json.loads(obj_json_text)
    #     return json_obj
    # endregion



