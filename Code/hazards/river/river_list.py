from ..third_party import np, Polygon, ox
from .river import river

def river_list(*args, buffer = None):
    """
    Get rivers within the given region (box or area) through OpenStreetMaps (OSM), returning the rivers within the given buffer, the polygon of the given region and the polygon of the buffered region.
    
    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
    	The positional arguments. This accepts either a single string 'location' value, which must be recognised as a region in OSM. Otherwise 4 float arguements are accepted as 'north, south, east, west', defining a box for the chosen region
    	
    buffer: float, optional
    	Description of the buffer. If provided, it represents the degree distance buffer at which to remove additional river data. Default to None.
    		
    Returns 
    -------
    riv: geopandas.geodataframe.GeoDataFrame
    	This is a list of the rivers contained within the region: their node id from OSM, their lat,lon node locations, the river name, and the reduced river lat, lon value if a buffer if applied
    	
    polygon: shapely.geometry.polygon.Polygon
    	A polygon of the given region
    	
    buffered_polygon: shapely.geometry.polygon.Polygon, Optional
    	If a buffer is given, this will return the buffered polygon at the given lat, lon distance
    """
    
    #Takes info from rivers and extracts the additional buffer information. This is used in other modules.
    riv , polygon = river(*args)
    if buffer is None:
        return riv, polygon
    else:
        riv['new geometry'] = None
        buffered_polygon = polygon.buffer(buffer)
        
        for i in range(len(riv)):
            river_loc = riv.loc[riv.index[i], 'geometry']
            k = river_loc.intersection(buffered_polygon)
            riv.at[riv.index[i], 'new geometry'] = k
        return riv, polygon, buffered_polygon  
