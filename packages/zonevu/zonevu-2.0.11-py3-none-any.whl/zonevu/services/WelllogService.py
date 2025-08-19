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

import numpy as np
from ..datamodels.wells.Welllog import Welllog
from ..datamodels.wells.Wellbore import Wellbore
from ..datamodels.wells.Curve import Curve
from ..datamodels.wells.CurveGroup import CurveGroup
from .Client import Client
from typing import Optional


class WelllogService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_welllogs(self, wellboreId: int) -> list[Welllog]:
        url = "welllogs/%s" % wellboreId
        items = self.client.get_list(url)
        logs = [Welllog.from_dict(w) for w in items]
        return logs

    def load_welllogs(self, wellbore: Wellbore, load_curves: bool = False) -> list[Welllog]:
        logs = self.get_welllogs(wellbore.id)
        wellbore.welllogs = logs

        if load_curves:
            for log in logs:
                for curve in log.curves:
                    self.load_curve_samples(curve)

        return logs

    def get_welllog(self, welllog_id: int) -> Welllog:
        url = "welllog/%s" % welllog_id
        item = self.client.get(url)
        return Welllog.from_dict(item)

    def add_welllog(self, wellbore: Wellbore, log: Welllog) -> None:
        """
        Adds a well log to a wellbore. Updates the passed in well log with zonevu ids of newly saved log.
        @param wellbore: Zonevu wellbore to which survey will be added.
        @param log: Well log object
        @return: Throw a ZonevuError if method fails
        """
        url = "welllog/add/%s" % wellbore.id

        # Build a dictionary of curve samples. Null out curve samples, so they are not copied to server here.
        curveDict = dict(map(lambda c: (id(c), c.samples), log.curves))
        for curve in log.curves:
            curve.samples = None

        item = self.client.post(url, log.to_dict(), True, {'lookupalias': True})
        server_log = log.from_dict(item)

        # Put curve samples back on source well log curves
        for curve in log.curves:
            curve.samples = curveDict[id(curve)]

        log.copy_ids_from(server_log)   # Copy server ids of logs to client.

    def delete_welllog(self, log: Welllog, delete_code: str) -> None:
        url = "welllog/delete/%s" % log.id
        self.client.delete(url, {"deletecode": delete_code})

    def get_lasfile(self, welllog: Welllog) -> Optional[str]:
        url = "welllog/lasfile/%s" % welllog.id
        raw_ascii_text = self.client.get_text(url, 'ascii')
        if raw_ascii_text is None:
            return None
        # Fix up text
        # ascii_text = raw_ascii_text.replace('\\r', '')
        # ascii_text = ascii_text.replace('\\n', '\n')
        # N = len(ascii_text)
        # ascii_text = ascii_text[1:N - 1]
        ascii_text = raw_ascii_text.replace('\r', '')   # Remove carriage returns.
        return ascii_text

    def post_lasfile(self, welllog: Welllog, las_text: str) -> None:
        url = "welllog/lasfile/%s" % welllog.id
        txt_bytes = las_text.encode('ascii')
        self.client.post_data(url, txt_bytes)

    def create_las_file_server(self, welllog: Welllog, overwrite: bool = False):
        # Cause an LAS file to be created and saved on server from database info
        url = "welllog/lasfile/instantiate/%s" % welllog.id
        self.client.post(url, {}, False, {"overwrite": overwrite})

    def load_curve_samples(self, curve: Curve):
        url = "welllog/curvedepthdatabytes/%s" % curve.id
        curve_float_bytes = self.client.get_data(url)
        tuples = np.frombuffer(curve_float_bytes, dtype=np.float32)
        curve.depths = tuples[::2]
        curve.samples = tuples[1::2]

    def load_splice_curve_samples(self, curve_group: CurveGroup):
        url = "welllog/splicecurvedepthdatabytes/%s" % curve_group.id
        curve_float_bytes = self.client.get_data(url)
        tuples = np.frombuffer(curve_float_bytes, dtype=np.float32)
        curve_group.depths = tuples[::2]
        curve_group.samples = tuples[1::2]

    def add_curve_samples(self, curve: Curve) -> None:
        url = "welllog/curvedatabytes/%s" % curve.id
        if curve.samples is not None:
            curve_float_bytes = curve.samples.tobytes()
            self.client.post_data(url, curve_float_bytes, 'application/octet-stream')
