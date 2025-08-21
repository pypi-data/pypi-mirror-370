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
Notes service.

List, retrieve, and add user notes and categories for wells and related
entities.
"""

from ..datamodels.wells.NoteCategory import NoteCategory
from ..datamodels.wells.Note import Note
from ..datamodels.wells.Wellbore import Wellbore
from .Client import Client


class NoteService:
    """List, retrieve, load, and add notes and categories for a wellbore."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_notes(self, wellbore: Wellbore) -> list[Note]:
        url = "notes/%s" % wellbore.id
        items = self.client.get_list(url)
        notes = [Note.from_dict(w) for w in items]
        return notes

    def load_notes(self, wellbore: Wellbore) -> list[Note]:
        notes = self.get_notes(wellbore)
        wellbore.notes = []
        for note in notes:
            wellbore.notes.append(note)
        return notes

    def add_notes(self, wellbore: Wellbore, notes: list[Note]) -> None:
        url = "notes/add/%s" % wellbore.id
        data = [s.to_dict() for s in notes]
        saved_notes_json = self.client.post_return_list(url, data)
        saved_notes = [Note.from_dict(w) for w in saved_notes_json]
        for (note, saved_note) in zip(notes, saved_notes):
            note.copy_ids_from(saved_note)

    def delete_notes(self, wellbore: Wellbore) -> None:
        # Deletes all notes for a specified wellbore
        url = "notes/delete/%s" % wellbore.id
        self.client.delete(url)
        # TODO: test this method

    def get_categories(self) -> list[NoteCategory]:
        url = "notes/categories"
        items = self.client.get_list(url)
        categories = [NoteCategory.from_dict(w) for w in items]
        return categories

