from ..third_party import pd, np, LineString, MultiLineString 
from .river_list import river_list
from ..conversion import conversion


def river_data(*args, buffer=None, print_list = True):
    """
    Returns the river node locations for a given location on the globe determined from OpenStreetMap (OSM) data. This should include the river name, OSM node, lat/lon locations, the lat/lon locations that fall in the chosen buffer region, and the km distances of each location with respect to lat, lon 0,0.

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
    	The positional arguments. This accepts either a single string 'location' value, which must be recognised as a region in OSM. Otherwise 4 float arguements are accepted as 'north, south, east, west', defining a box for the chosen region
    	
    buffer: float, optional
    	Description of the buffer. If provided, it represents the degree distance buffer at which to remove additional river data. Default to None.
    		
    Returns 
    -------
    riv: geopandas.geodataframe.GeoDataFrame
    	This is a list of the rivers contained within the region: their node id from OSM, their lat,lon node locations, the river name, and the reduced river lat, lon value if a buffer if applied and the km distances of the reduced lat, lon values with respect to a reference lat,lon of 0,0
    	
    polygon: shapely.geometry.polygon.Polygon
    	A polygon of the given region
    	
    buffered_polygon: shapely.geometry.polygon.Polygon, Optional
    	If a buffer is given, this will return the buffered polygon at the given lat, lon distance
    """
    if buffer is None:
        river, polygon = river_list(*args, print_list = print_list)
    else:
        river, polygon, buffer_polygon = river_list(*args, buffer=buffer, print_list = print_list)
        
    river['km distances'] = None

	#Extract the geometries of the river locations. 
    for j in range(len(river)):
        if buffer is None:
            geom = river.loc[river.index[j], 'geometry']
        else:
            geom = river.loc[river.index[j], 'new geometry']
	#Create x,y locations to find the km distances from some reference point.
        if isinstance(geom, LineString):
            x, y = geom.xy
        elif isinstance(geom, MultiLineString):
            x, y = [], []
            for line in geom.geoms:  # Use geoms 
                xx, yy = line.xy
                x.extend(xx)
                y.extend(yy)

	#Calculates km distances. (Place holder)
        distances_km = []
        for i in range(len(x)):
            dis = conversion(x[i], y[i])
            distances_km = np.append(distances_km, dis)
        coordinates = [(distances_km[i], distances_km[i + 1]) for i in range(0, len(distances_km), 2)]
 
        line = LineString(coordinates)
        river.at[river.index[j], 'km distances'] = line

    if buffer is None:
        return river, polygon
    else:
        return river, polygon, buffer_polygon
