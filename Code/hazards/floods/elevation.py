from ..third_party import rasterio, pd, MultiLineString, LineString
from .river_data import river_data


def river_elevation(geotiff_path, *args, buffer=None, print_list = True):
    """
    Get rivers within the given region (box or area) through OpenStreetMaps (OSM), their names, geometries,
    reduced geometries based on the size of the buffer for the region, km distances for the reduced geometries
    with respect to lat, lon location 0,0, and the elevation data for each point.

    Parameters
    ----------
    geotiff_path : str
        This should be the str name of a downloaded geotiff of elevation data that covers the chosen region.

    *args : Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as
        a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for
        the chosen region.

    buffer : float, optional
        Description of the buffer. If provided, it represents the degree distance buffer at which to remove
        additional river data. Default is None.

    Returns
    -------
    river : geopandas.geodataframe.GeoDataFrame
        This is a list of the rivers contained within the region: their node id from OSM, their lat, lon node locations
        (geometry), the river name, the new reduced geometries due to the buffer, the km distances with respect to lat,
        lon location 0,0 for these reduced geometries, and the elevations.
    """
    
    #Take river info and calculate elevation from the geotiff file 
    if buffer is None:
        r, polygon = river_data(*args, print_list = print_list)
        r['elevations'] = None
        for i in range(len(r)):
            riv = r.loc[r.index[i], 'geometry']
            if isinstance(riv, LineString):
                coords_list = list(riv.coords)
            elif isinstance(riv, MultiLineString):
                coords_list = [list(line.coords) for line in riv.geoms]

		#Calculate elevation
            elev = []
            
            with rasterio.open(geotiff_path) as src:
                vals = src.sample(coords_list)
                for val in vals:
                    elev.append(val[0])

            r.at[r.index[i], 'elevations'] = elev

        return r
    else:
        r, polygon, buffered_polygon = river_data(*args, buffer=buffer, print_list = print_list)
        r['elevations'] = None

        # This uses cut rivers instead of non cut one. Calculates same as above. 
        for i in range(len(r)):
            riv = r.loc[r.index[i], 'new geometry']
            if isinstance(riv, LineString):
                coords_list = list(riv.coords)
            elif isinstance(riv, MultiLineString):
                coords_list = [list(line.coords) for line in riv.geoms]


            elev = []

            with rasterio.open(geotiff_path) as src:
                vals = src.sample(coords_list)
                for val in vals:
                    elev.append(val[0])

            r.at[r.index[i], 'elevations'] = elev

        return r
