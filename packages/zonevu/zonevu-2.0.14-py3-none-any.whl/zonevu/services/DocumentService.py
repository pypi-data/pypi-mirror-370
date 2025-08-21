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
Document management service.

Create document catalog entries and obtain time-limited credentials for
uploading and downloading document blobs stored by ZoneVu.
"""

from .Client import Client
from ..datamodels.Document import Document
from ..services.Utils import CloudBlobCredential
from ..services.Client import ZonevuError


class DocumentService:
    """Create document entries and retrieve upload/download credentials."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def create_document(self, doc: Document) -> None:
        """
        Create document in ZoneVu document index
        :param doc: Document catalog entry
        :return:
        """
        if not doc.is_valid():
            raise ZonevuError.local('The document entry for "%s" is not valid' % doc.name)

        url = 'document/add'
        item = self.client.post(url, doc.to_dict(), False)
        server_doc = Document.from_dict(item)
        doc.id = server_doc.id

    def get_doc_download_credential(self, doc: Document) -> CloudBlobCredential:
        url = 'document/download/credential/%s' % doc.id
        item = self.client.get(url)
        cred = CloudBlobCredential.from_dict(item)
        return cred

    def get_doc_upload_credential(self, doc: Document) -> CloudBlobCredential:
        url = 'document/upload/credential/%s' % doc.id
        item = self.client.get(url)
        cred = CloudBlobCredential.from_dict(item)
        return cred

    def copy_doc(self, src_doc: Document, dst_doc: Document) -> None:
        """
        Copies document data bytes from a source document (catalog entry) to a destination document (catalog entry).
        Note that a Document defines the data entity and relative path within the documents folder on that data entity.
        :param src_doc: The document index entry from which to get the data bytes.
        :param dst_doc: The document index entry into which to copy the data bytes.
        :return:
        """
        try:
            url = 'document/copy'
            self.client.post(url, {}, False, {
                "srcid": src_doc.id,
                "dstid": dst_doc.id
            })
        except ZonevuError as err:
            print('Copy of the requested document "%s" failed because.' % err.message)
            raise err

        pass


