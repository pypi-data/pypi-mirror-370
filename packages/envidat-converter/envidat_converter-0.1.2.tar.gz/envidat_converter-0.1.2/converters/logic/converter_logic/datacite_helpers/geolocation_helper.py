"""
Helper methods for geolocation conversion.
"""

import collections


def _geometrycollection_to_dc_geolocations(self, spatial: dict):
    """Returns spatial data in DataCite "geoLocations" format.

    Assumption: input spatial dictionary has a "type" value of "geometrycollection".
    """
    dc_geolocations = []

    geometries = spatial.get(self.geometries)
    if geometries:
        for geometry in geometries:
            spatial_type = geometry.get(self.type_tag, "")

            if spatial_type:
                dc_geolocation = _get_dc_geolocations(self, geometry, spatial_type)

                if dc_geolocation:
                    dc_geolocations += dc_geolocation

    return dc_geolocations


def _get_dc_geolocations(self, spatial: dict, spatial_type: str = ""):
    """Returns spatial data in DataCite "geoLocations" format.

    For list of required attributes for each type of GeoLocation see DataCite documentation.
    """
    dc_geolocations = []

    spatial_type = spatial_type.lower()
    coordinates = spatial.get(self.coordinates)

    if coordinates and spatial_type:
        match spatial_type:
            case self.polygon:
                dc_geolocation = _get_dc_geolocation_polygon(self, coordinates)
                if dc_geolocation:
                    dc_geolocations += [dc_geolocation]

            case self.point:
                dc_geolocation = _get_dc_geolocation_point(self, coordinates)
                if dc_geolocation:
                    dc_geolocations += [dc_geolocation]

            case self.multipoint:
                for coordinates_pair in coordinates:
                    dc_geolocation = _get_dc_geolocation_point(self, coordinates_pair)
                    if dc_geolocation:
                        dc_geolocations += [dc_geolocation]

    return dc_geolocations


def _get_dc_geolocation_polygon(self, coordinates: list):
    """Returns spatial data in DataCite "geoLocationPolygon" format.

    Returns None if coordinates invalid or < 4 coordinates_pairs obtained

    Limitation: Only can process first list in coordinates list from parsed geojson.
                This means that polygons with "holes" are not supported.
    """
    # Log warning if coordinates has more than one element (i.e. polygon with "hole")

    # Assign polygon_coordinates to first element of coordinates list
    polygon_coordinates = coordinates[0]

    # Validate polygon_coordinates
    if len(polygon_coordinates) < 4:
        return None
    if polygon_coordinates[0] != polygon_coordinates[-1]:
        return None

    # Convert input coordinates to DataCite format
    dc_geolocation = collections.OrderedDict()
    dc_geolocation[self.geolocation_polygon_tag] = {self.polygon_point: []}

    for coordinates_pair in polygon_coordinates:
        if len(coordinates_pair) == 2:
            geolocation_point = collections.OrderedDict()
            geolocation_point[self.point_longitude_tag] = coordinates_pair[0]
            geolocation_point[self.point_latitude_tag] = coordinates_pair[1]
            dc_geolocation[self.geolocation_polygon_tag][self.polygon_point] += [
                geolocation_point
            ]

    if dc_geolocation:
        return dc_geolocation

    return None


def _get_dc_geolocation_point(self, coordinates_pair: list[float]):
    """Returns spatial data in DataCite's "geoLocationPoint" format.

    If coordinates_pair list does not have a length of two then returns None.
    """
    if len(coordinates_pair) == 2:
        dc_geolocation = collections.OrderedDict()
        dc_geolocation_point_tag = self.polygon_point_tag
        dc_geolocation[dc_geolocation_point_tag] = collections.OrderedDict()

        dc_geolocation[dc_geolocation_point_tag][self.point_longitude_tag] = (
            coordinates_pair[0]
        )
        dc_geolocation[dc_geolocation_point_tag][self.point_latitude_tag] = (
            coordinates_pair[1]
        )

        return dc_geolocation

    return None
