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
Stratigraphic columns service.

Find stratigraphic columns by name and retrieve full column definitions and
entries. Provides helpers to get the first matching column by name.
"""

from ..datamodels.strat.StratColumn import StratColumn, StratColumnEntry
from .Client import Client
from typing import Optional, Union


class StratService:
    """Find and retrieve stratigraphic columns, or get the first matching name."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_stratcolumns(self, match_token: Optional[str] = None, exact_match: bool = False) -> list[StratColumnEntry]:
        url = "stratcolumns"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get_list(url, {"exactmatch": exact_match})
        cols = [StratColumnEntry.from_dict(w) for w in items]
        return cols

    def get_first_named(self, name: str) -> Optional[StratColumn]:
        """
        Get first project with the specified name, populate it, and return it.
        :param name: name of strat column to get
        :return:
        """
        strat_col_entries = self.get_stratcolumns(name, True)
        if len(strat_col_entries) == 0:
            return None
        strat_col_entry = strat_col_entries[0]
        strat_col = self.find_stratcolumn(strat_col_entry.id)
        return strat_col

    def find_stratcolumn(self, strat_column: Union[StratColumnEntry, int]) -> StratColumn:
        strat_column_id = strat_column if isinstance(strat_column, int) else strat_column.id
        url = "stratcolumn/%s" % strat_column_id
        item = self.client.get(url)
        col = StratColumn.from_dict(item)
        return col

    def add_stratcolumn(self, col: StratColumn) -> None:
        url = "stratcolumn/add"
        item = self.client.post(url, col.to_dict())
        server_survey = StratColumn.from_dict(item)
        col.copy_ids_from(server_survey)

