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
Coordinate systems and conversion service.

Convert between EPSG codes and CRS specs, transform coordinates and geolocations,
query grid convergence, and fetch CRS entries/projections/zones.
"""

from typing import List, Optional
from .Client import Client
from .Error import ZonevuError
from ..datamodels.geospatial.Crs import CrsSpec, CrsEntry
from ..datamodels.geospatial.Coordinate import Coordinate
from ..datamodels.geospatial.GeoLocation import GeoLocation
from ..datamodels.geospatial.GridGeometry import GridGeometry
from ..datamodels.geomodels.SimpleGrid import SimpleGrid
from ..datamodels.geospatial.CrsDescriptor import StatePlaneDescriptor, UtmDescriptor


class CoordinatesService:
    """CRS and coordinate conversion utilities."""

    client: Client

    __projections: list[CrsEntry] = None
    __zones: dict[str, list[CrsEntry]] = {}

    def __init__(self, c: Client):
        self.client = c

    def convert_epsg(self, epsg: int) -> CrsSpec:
        try:
            item = self.client.get('coordinates/epsg/%s' % epsg, None, False)
            return CrsSpec.from_dict(item)
        except ZonevuError as err:
            raise ZonevuError.local('could not find coordinate reference system for EPSG code %s because %s' %
                                    (epsg, err.message))

    def get_geolocation(self, c: Coordinate, crs: CrsSpec) -> GeoLocation:
        item = self.client.get('coordinates/geolocation', {"x": c.x, "y": c.y, "epsgcode": crs.epsg_code,
                                                           "projection": crs.projection, "zone": crs.zone,
                                                           "units": '' if crs.units is None else crs.units}, False)
        return GeoLocation.from_dict(item)

    def get_geolocations(self, xys: List[Coordinate], crs: CrsSpec) -> List[GeoLocation]:
        xy_json_array = [c.to_dict() for c in xys]
        items = self.client.post_return_list('coordinates/geolocations', xy_json_array, False, {"epsgcode": crs.epsg_code,
                                "projection": crs.projection, "zone": crs.zone,
                                "units": '' if crs.units is None else crs.units})
        locations = [GeoLocation.from_dict(item) for item in items]
        return locations

    def get_coordinate(self, loc: GeoLocation, crs: CrsSpec) -> Coordinate:
        item = self.client.get('coordinates/coordinate', {"latitude": loc.latitude, "longitude": loc.longitude,
                                                          "epsgcode": crs.epsg_code,
                                                          "projection": crs.projection, "zone": crs.zone,
                                                          "units": '' if crs.units is None else crs.units}, False)
        return Coordinate.from_dict(item)

    def get_grid_convergence(self, loc: GeoLocation, crs: CrsSpec) -> float:
        item = self.client.get_float('coordinates/gridconvergence',
                               {"latitude": loc.latitude, "longitude": loc.longitude, "epsgcode": crs.epsg_code,
                                "projection": crs.projection, "zone": crs.zone,
                                "units": '' if crs.units is None else crs.units}, False)
        return item

    def get_projections(self) -> list[CrsEntry]:
        if CoordinatesService.__projections is None:
            items: list[str] = self.client.get_list('coordinates/projections', None, False)
            CoordinatesService.__projections = [CrsEntry.from_dict(w) for w in items]
        return CoordinatesService.__projections

    def get_zones(self, projection: str) -> list[CrsEntry]:
        entries = CoordinatesService.__zones.get(projection)
        if entries is None:
            items: list[str] = self.client.get_list('coordinates/zones', {"projection": projection}, False)
            entries = [CrsEntry.from_dict(w) for w in items]
            CoordinatesService.__zones[projection] = entries
        return entries

    def get_stateplane_crs(self, descr: StatePlaneDescriptor) -> Optional[CrsSpec]:
        """
        Attempts to find the state plane CRS by name
        """
        state_str = str(descr.code)
        state_plane_projection = str('StatePlane%s' % descr.datum)
        zone_str = str(descr.zone)
        zone_name_fragment = ('%sStatePlane%s%s' % (descr.datum, state_str, zone_str)).lower().replace(" ", "")

        projections = self.get_projections()
        projection = next((p for p in projections if p.id == state_plane_projection), None)
        if projection is None:
            return None
        zones = self.get_zones(projection.id)
        zone: Optional[CrsEntry] = None
        for entry in zones:
            index = entry.id.find('FIPS')
            zone_option = entry.id[:index].lower()
            if zone_option == zone_name_fragment:
                zone = entry
                break

        # zone = next((z for z in zones if z.name.lower().startswith(zone_name_fragment)), None)
        if zone is None:
            return None

        return CrsSpec(None, projection.id, zone.id, descr.units)

    def get_utm_crs(self, descr: UtmDescriptor) -> Optional[CrsSpec]:
        projection_str = descr.get_projection_str()
        zone_str = descr.get_zone_str()

        projections = self.get_projections()
        projection = next((p for p in projections if p.id == projection_str), None)
        if projection is None:
            return None

        zones = self.get_zones(projection.id)
        zone = next((z for z in zones if z.id.lower() == zone_str), None)
        if zone is None:
            return None

        return CrsSpec(None, projection.id, zone.id, descr.units)

    def simple_to_grid_geometry(self, grid: SimpleGrid) -> GridGeometry:
        g = GridGeometry.from_simple_grid(grid)
        g.corner1.lat_long = self.get_geolocation(g.corner1.p, grid.crs)
        g.corner2.lat_long = self.get_geolocation(g.corner2.p, grid.crs)
        g.corner3.lat_long = self.get_geolocation(g.corner3.p, grid.crs)
        g.corner4.lat_long = self.get_geolocation(g.corner4.p, grid.crs)
        g.geo_inclination = GeoLocation.bearing(g.corner1.lat_long, g.corner4.lat_long)
        return g