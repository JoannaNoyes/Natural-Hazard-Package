from .river_list import river_list
from ..third_party import Point, pd

def river_buffer(*args, buffer_distance=0.003, river_cutoff=0.005):
    """
    Returns the river plot, polygon of an area and the river buffer for a chosen region. 
    
    Parameters:
    -----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
    buffer_distance: float, Optional
    	The buffer given to the river. This is in degrees. Default = 0.003 degrees.
    river_cutoff: float, Optional
    	The buffer given to the polygon of the chosen region outside of which river coordinates are dropped to provide a smaller dataset for the chosen region
    	
    Returns:
    --------
    river: geopandas.geodataframe.GeoDataFrame
    	the geodataframe of the river profile, containing the geometry, name and new geometry
    
    polygon: shapely.geometry.polygon.Polygon
    	polygon of the chosen region determined by args
    
    buffer_total: shapely.geometry.multipolygon.MultiPolygon
    	polygon or multipolygon of the river buffers
    
    
    """
    
    #Pull info from river list for the river and polygons.
    river, polygon, buffered_polygon = river_list(*args, buffer=river_cutoff)
    buffer_total = Point(0, 0).buffer(0)

	#Cut the river data to just points inside of the given buffere region. 
    for i in range(len(river)):
        riv = river.loc[river.index[i], 'new geometry']
        buffer = riv.buffer(buffer_distance)
        buffer_total = buffer_total.union(buffer)

    return river, polygon, buffer_total
