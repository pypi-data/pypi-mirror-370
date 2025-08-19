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
Stratigraphic tops service.

List and fetch well tops for a well or wellbore and manage their retrieval.
"""

from ..datamodels.wells.Welltop import Welltop
from ..datamodels.wells.Wellbore import Wellbore
from typing import Union
from .Client import Client
from .Error import ZonevuError


class WelltopService:
    """Retrieve and manage stratigraphic tops for a wellbore."""
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_welltops(self, wellbore: Wellbore) -> list[Welltop]:
        url = "welltops/%s" % wellbore.id
        items = self.client.get_list(url)
        tops = [Welltop.from_dict(w) for w in items]
        return tops

    def load_welltops(self, wellbore: Wellbore) -> list[Welltop]:
        tops = self.get_welltops(wellbore)
        wellbore.tops = []
        for top in tops:
            wellbore.tops.append(top)
        return tops

    def add_top(self, wellbore: Wellbore, top: Welltop):
        raise ZonevuError.local('add_top not implemented')
        # url = "welltop/add/%s" % wellbore.id
        # saved_top = self.client.post(url, top.to_dict())
        # top.copy_ids_from(saved_top)

    def add_tops(self, wellbore: Wellbore, tops: list[Welltop], reset: bool = False) -> None:
        # Copy survey ids
        for top in tops:
            if top.survey:
                top.survey_id = top.survey.id

        url = "welltops/add/%s" % wellbore.id
        data = [s.to_dict() for s in tops]
        items = self.client.post_return_list(url, data, True, {'reset': reset})
        saved_tops = [Welltop.from_dict(w) for w in items]
        for (top, saved_top) in zip(tops, saved_tops):
            top.copy_ids_from(saved_top)

    def delete_tops(self, wellbore: Wellbore, tops: Union[list[Welltop], None] = None) -> None:
        url = "welltops/delete/%s" % wellbore.id
        data = [] if tops is None else [s.id for s in tops]
        self.client.post(url, data, False)


    # def delete_top(self, top: Welltop) -> None:
    #     url = "welltop/delete/%s" % top.id
    #     self.client.delete(url)
    #     # TODO: implement this method on SERVER - deletes a specified top
    #
    # def delete_tops(self, wellbore: Wellbore) -> None:
    #     url = "welltops/delete/%s" % wellbore.id
    #     self.client.delete(url)
    #     # TODO: implement this method on SERVER - deletes all tops on a specified wellbore
