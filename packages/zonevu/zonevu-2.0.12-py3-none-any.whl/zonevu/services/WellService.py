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
Well catalogue and operations service.

Provides search and retrieval of wells and related data (logs, tops,
surveys, geosteering, completions, notes). Exposes helpers to find wells by
name, ID, UWI, and by proximity, and to load aggregated well data.
"""

import time
import urllib.parse

from ..datamodels.Company import Division
from ..datamodels.strat.StratColumn import StratColumn
from ..datamodels.wells.Well import Well, WellEntry
from .Client import Client, ZonevuError
from .WelllogService import WelllogService
from .SurveyService import SurveyService
from .WelltopService import WelltopService
from .GeosteeringService import GeosteeringService
from .CompletionsService import CompletionsService
from .NoteService import NoteService
from typing import Set, List, Dict, Any, Optional, Tuple, Union
from difflib import SequenceMatcher
from .WellData import WellData, WellDataOptions
from ..datamodels.Project import ProjectEntry
from ..datamodels.geospatial.GeoLocation import GeoLocation
import copy

from ..datamodels.wells.Welllog import WellLogTypeEnum


class WellService:
    """Search/find wells and load related data (logs, tops, surveys, fracs)."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_wells(self, division: Optional[Union[Division, int]] = None) -> List[WellEntry]:
        """
        Get list of all well catalog entries.
        :return: A list of well entries (summary data structures) that match. These are not full well objects.
        """
        return self.find_by_name(division=division)

    def find_by_name(self, match_token: Optional[str] = None, exact_match: Optional[bool] = True, division: Optional[Union[Division, int]] = None,
                     page: Optional[int] = 0) -> List[WellEntry]:
        """
        Find listing entries a well or wells whose names match a name or that start with a name fragment
        @param match_token: name or name fragment to use to search for wells. If not provided, gets all wells.
        @param exact_match: whether to exactly match the well name.
        @param division: division (business unit) to search in. If None, searches all divisions user is authorized for
        @param page: page number that is used by this method to retrieve all wells since the limit is 500 per call.
        @return: A list of well entries (summary data structures) that match. These are not full well objects.
        """
        url = "wells"
        max_pages = 50     # This means that it won't do more than 50 round trips to retrieve search result pages.
        params = {"exactmatch": str(exact_match)}
        if division is not None:
            division_id = division if isinstance(division, int) else division.id
            params["divisionid"] = division_id
        all_entries: list[WellEntry] = []
        more = True
        if match_token is not None:
            params["name"] = urllib.parse.quote_plus(match_token)

        counter = 0
        while more:
            params["page"] = str(page)
            wells_response = self.client.get_dict(url, params, False)
            items = wells_response['Wells']
            more = wells_response['More']
            page = wells_response['Page']
            entries = [WellEntry.from_dict(w) for w in items]
            all_entries.extend(entries)
            counter += 1
            if counter > max_pages:
                break               # Safety check. Limits us to 500 iterations, which is 250,000 wells.
            time.sleep(0.050)       # Pause for 50 ms so as not to run into trouble with webapi throttling.

        return all_entries

    def find_by_location(self, location: GeoLocation, distance: float) -> List[WellEntry]:
        uwi = "wells/nearby"
        params = {"latitude": location.latitude, "longitude": location.longitude, "radius": distance}
        try:
            items = self.client.get_list(uwi, params, False)
            entries = [WellEntry.from_dict(w) for w in items]
            return entries
        except ZonevuError as err:
            if err.status_code == 404:
                return []
            raise err

    def find_by_id(self, well_id: int) -> Well:
        url = "well/id/%s" % well_id
        item = self.client.get(url, {}, False)
        well = Well.from_dict(item)
        return well

    def find_by_uwi(self, uwi: str) -> Optional[Well]:
        url = "well/uwi"
        params = {"uwi": urllib.parse.quote_plus(uwi)}
        try:
            item = self.client.get(url, params, False)
            well = Well.from_dict(item)
            return well
        except ZonevuError as err:
            if err.status_code == 404:
                return None
            raise err

    def find_wells_original_uwi(self, uwi: str) -> List[WellEntry]:
        # Get wells by original UWI.
        url = "wells/originaluwi"
        params = {'uwi': uwi}
        items = self.client.get_list(url, params, False)
        entries = [WellEntry.from_dict(w) for w in items]
        return entries

    def find_similar(self, name: str, location: GeoLocation, tolerance: float = 0.9, distance: float = 2) -> List[WellEntry]:
        """
        Finds wells in ZoneVu near a location with nearly or exactly the same name.
        :param name: the name to attempt to match to the full (well name + well number) well name
        :param location: the geolocation to search nearby for wells
        :param tolerance: the text similarity threshold [0, 1], where 1 is an exact match and zero is no match.
        :param distance: the radius in meters around 'location' to search.
        :return:
        """
        nearby_wells = self.find_by_location(location, distance)  # Find all wells within N meters.
        raw_output: List[Tuple[float, WellEntry]] = []
        for well in nearby_wells:
            similarity = SequenceMatcher(None, name, well.full_name).ratio()
            raw_output.append((similarity, well))
        output = [item for item in raw_output if item[0] > tolerance]
        output = sorted(output, key=lambda item: item[0], reverse=True)
        return [item[1] for item in output]

    def get_first_named(self, well_name: str, exact_match: bool = True) -> Optional[Well]:
        """
        Finds well entry for the first well named 'well_name', and retrieves the full well
        @param well_name: the exact name of the well, including well number, if any
        @param exact_match: set to True if searching for well by exact name match
        @return: A well object
        """
        well_entries = self.find_by_name(well_name, exact_match)  # Find well listing entry by name doing an exact match
        if len(well_entries) == 0:
            return None
        well = self.find_by_id(well_entries[0].id)  # Get the full well object from ZoneVu
        return well

    def load_well(self, well: Well, well_data: Optional[Set[WellData]] = None) -> None:
        """

        :param well:
        :param well_data:
        """
        options = WellDataOptions(well_data)
        loaded_well = self.find_by_id(well.id)
        well.merge_from(loaded_well)
        primary_wb = well.primary_wellbore
        if primary_wb is None:
            return

        if options.welllogs:
            try:
                log_svc = WelllogService(self.client)
                log_svc.load_welllogs(primary_wb, options.curves)
            except Exception as err:
                print('Could not load well logs because %s' % err)

        if options.surveys:
            try:
                survey_svc = SurveyService(self.client)
                survey_svc.load_surveys(primary_wb)
            except Exception as err:
                print('Could not load well surveys because %s' % err)

        if options.tops:
            try:
                top_svc = WelltopService(self.client)
                top_svc.load_welltops(primary_wb)
            except Exception as err:
                print('Could not load well tops because %s' % err)

        if options.fracs:
            try:
                frac_svc = CompletionsService(self.client)
                frac_svc.load_fracs(primary_wb)
            except Exception as err:
                print('Could not load fracs because %s' % err)

        if options.geosteering:
            try:
                primary_wb.interpretations.clear()
                geosteer_svc = GeosteeringService(self.client)
                geosteering_entries = geosteer_svc.get_interpretations(primary_wb.id)
                for interp_entry in geosteering_entries:
                    try:
                        interp = geosteer_svc.get_interpretation(interp_entry.id)
                        if interp.valid:
                            primary_wb.interpretations.append(interp)
                    except Exception as interp_err:
                        print(f'Could not retrieve wellbore "{primary_wb.name}" geosteering interpretation with id {interp_entry.id}: {interp_err}')
            except Exception as err:
                print(f'Could not load wellbore "{primary_wb.name}" geosteering interpretations: {err}')

        if options.notes:
            try:
                notes_svc = NoteService(self.client)
                notes_svc.load_notes(primary_wb)
            except Exception as err:
                print('Could not load well user notes because %s' % err)

    def get_stratcolumn(self, well: Union[Well, WellEntry, int]) -> StratColumn | None:
        """
        Get the selected strat column for the well
        """
        well_id = well if isinstance(well, int) else well.id
        if well.strat_column is None:
            return None
        url = "well/stratcolumn/%s" % well_id
        item = self.client.get(url)
        col = StratColumn.from_dict(item)
        return col

    def get_stratcolumns(self, well: Union[Well, WellEntry, int]) -> list[StratColumn]:
        """
        Get all strat columns for the well
        """
        well_id = well if isinstance(well, int) else well.id
        url = "well/stratcolumns/%s" % well_id
        items = self.client.get_list(url)
        cols = [StratColumn.from_dict(w) for w in items]
        return cols

    def create_well(self, well: Well, well_data: Optional[Set[WellData]]) -> None:
        """
        Create a well and its child data on the server
        :param well:  Well to create in ZoneVu account
        :param well_data:  Which child data on the well to also create on the newly created well.
        Note: passed in well will be altered.
        """
        options = WellDataOptions(well_data)

        # First, create the well itself.
        wellUrl = "well/create"
        trimmed_well = well.make_trimmed_copy()
        item = self.client.post(wellUrl, trimmed_well.to_dict())
        created_well = Well.from_dict(item)
        # Update ids on well and wellbores to new ids in ZoneVu
        well.id = created_well.id
        for wb, wb_copy in zip(well.wellbores, created_well.wellbores):
            wb.id = wb_copy.id

        # Exit if well has no wellbores.
        if well.primary_wellbore is None:
            return

        # Create all child data for the primary wellbore.
        wellbore = well.primary_wellbore

        # Surveys
        survey_lut: Dict[int, int] = dict()  # Need LUT for surveys to re-reference from tops that refer to them.
        if options.surveys:
            survey_svc = SurveyService(self.client)
            for survey in wellbore.surveys:
                src_id = survey.id
                survey_svc.add_survey(wellbore, survey)  # Note: updates survey ids on 'wellbore'
                survey_lut[src_id] = survey.id

        # Well tops
        if options.tops:
            top_svc = WelltopService(self.client)
            for top in wellbore.tops:
                if top.survey_id in survey_lut:
                    top.survey_id = survey_lut[top.survey_id]  # Re-reference top survey to new survey on wellbore
            top_svc.add_tops(wellbore, wellbore.tops)

        # Well logs
        if options.welllogs:
            log_svc = WelllogService(self.client)
            for log in wellbore.welllogs:
                log_svc.add_welllog(wellbore, log)

        # Well log curve samples
        if options.curves:
            log_svc = WelllogService(self.client)
            for log in wellbore.welllogs:
                for curve in log.curves:
                    log_svc.add_curve_samples(curve)
                log_svc.create_las_file_server(log)    # Create

        # Geosteering interpretations
        if options.geosteering:
            # Note: curve ids in curve defs in interpretations refer to curves that already exist on server
            geosteer_svc = GeosteeringService(self.client)
            for interp in wellbore.interpretations:
                interp._old_id = interp.id
                geosteer_svc.add_interpretation(wellbore.id, interp)

        if options.fracs:
            # Do some validation.
            # If we are loading frac data, and it refers to a geosteering interpretation, must first create the interp,
            # and update the reference in the frac to the new instances. It is illegal to create a frac in this method
            # that refers to a geosteering interpretation without creating the interpretation in this method.
            refs_to_interps = any(frac.interpretation_id is not None for frac in well.primary_wellbore.fracs)
            if refs_to_interps and not options.geosteering:
                raise ZonevuError.local('cannot create frac on wellbore without providing geosteering interps')

            frac_svc = CompletionsService(self.client)
            for frac in wellbore.fracs:
                if frac.interpretation_id is not None:
                    frac.interpretation_id = next((i for i in wellbore.interpretations
                                                   if frac.interpretation_id == i._old_id), -1)
                frac_svc.add_frac(wellbore, frac)

        # Wellbore notes
        if options.notes:
            notes_svc = NoteService(self.client)
            notes_svc.add_notes(wellbore, wellbore.notes)

    def add_tops(self, well: Well) -> None:
        """
        Updates the well tops on the server for all wellbores on the well from the tops on each wellbore
        @param well: well object
        """
        for wellbore in well.wellbores:
            top_svc = WelltopService(self.client)
            top_svc.add_tops(wellbore, wellbore.tops)

    def update_well(self, well: Well) -> None:
        """
        Updates a well. Note that only the well-level properties are updated.
        @param well: well object
        @return: Throw a ZonevuError if method fails
        """
        url = "well/update/%s" % well.id
        item = self.client.patch(url, well.to_dict(), True)

    def delete_well(self, well_id: int, delete_code: str) -> None:
        url = "well/delete/%s" % well_id
        url_params: Dict[str, Any] = {"deletecode": delete_code}
        self.client.delete(url, url_params)

    def get_well_projects(self, well_id: int) -> list[ProjectEntry]:
        # Get a list of projects that include this well.
        url = "well/projects/%s" % well_id
        items = self.client.get_list(url)
        entries = [ProjectEntry.from_dict(w) for w in items]
        return entries

    def copy_well(self, well: Well, well_copy_name: str, well_copy_number: Optional[str], well_copy_uwi: str) -> Well:
        """
        This function makes and saves a copy of a well and all of its child data.
        :param well: the well to be copied
        :param well_copy_name:  name of copied well
        :param well_copy_number:  number of copied well. If None, the well number from the source well will be used.
        :param well_copy_uwi:  UWI of copied well
        :return: the copy of the well

        NOTES:
            1.  We are copying a well and all of its constituent child data, including surveys, well logs, tops, etc. We will do a "Phase I" copy of all of this, except the geosteering interpretations.
            2.  We will also copy the geosteering interpretations -- this will be "Phase II". This is a special case because these refer to other wells, namely, type wells. We will assume that those wells are not being copied, therefore the references in the geosteering interpretations to those wells will remain valid.
            3.  The geosteering interpretations also refer to LWD well log curves on this well that is being copied. Those references need to be updated since we have copied in Phase I the well logs on this very well.
        """
        geosteer_svc = GeosteeringService(self.client)

        # Phase I - create and save a copy of the well and all its child data, except geosteering interpretations
        well_copy = copy.deepcopy(well)
        well_copy.name = well_copy_name
        well_copy.uwi = well_copy_uwi
        if well_copy_number is not None:
            well_copy.number = well_copy_number
        # Note: adjust well log types to mask out Witsml source.
        for wellbore in well_copy.wellbores:
            for log in wellbore.welllogs:
                if log.source == WellLogTypeEnum.Witsml:
                    log.source = WellLogTypeEnum.Digital

        # NOTE: create_well updates all the system ids on the well and all of its children to the new saved ids.
        #       We will use those new system ids below.
        self.create_well(well_copy, {WellData.surveys, WellData.logs, WellData.curves, WellData.tops,
                                     WellData.notes})

        # Phase II - copy the geosteering interpretations, update curve defs that refer to this wellbores logs, & save.
        # Make a lookup dict that relates the well log curves in the original well to the curves in the copied well.
        wb_orig = well.primary_wellbore
        wb_copy = well_copy.primary_wellbore
        curve_lut = {orig.id: cpy.id for orig, cpy in zip(wb_orig.well_log_curves, wb_copy.well_log_curves)}
        grp_lut = {orig.id: cpy.id for orig, cpy in zip(wb_orig.well_log_curve_groups, wb_copy.well_log_curve_groups)}

        # Update curve defs in geosteering interpretations that refer to this wellbores logs
        interp_id_lut: Dict[int, int] = {}
        for interp in wb_orig.interpretations:
            interp_copy = copy.deepcopy(interp)  # Make a copy of the interpretation
            curve_defs = [d for d in interp_copy.curve_defs if d.curve_id in curve_lut or d.curve_group_id in grp_lut]

            for d in curve_defs:  # For curve defs that refer to this well, and update them to correct system ids
                if d.curve_id is not None:
                    d.curve_id = curve_lut[d.curve_id]  # Update the curve def curve id reference
                if d.curve_group_id is not None:
                    d.curve_group_id = grp_lut[d.curve_group_id]  # Update the curve def curve id reference

            try:
                geosteer_svc.add_interpretation(wb_copy.id, interp_copy)  # Save interp onto well copy
                interp_id_lut[interp.id] = interp_copy.id
            except ZonevuError as interp_err:
                print(f'* Warning could not copy interpretation {interp_copy.name} because {interp_err.message}')

        # Do fracs last since a frac could refer to a geosteering interp
        frac_svc = CompletionsService(self.client)
        for frac in wb_orig.fracs:
            frac_copy = copy.deepcopy(frac)
            if frac.interpretation_id is not None:
                if frac.interpretation_id in interp_id_lut:
                    frac_copy.interpretation_id = interp_id_lut[frac.interpretation_id]
            frac_svc.add_frac(wb_copy.id, frac_copy)

        return well_copy


