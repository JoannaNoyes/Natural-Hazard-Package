from ..third_party import Point, np, ox, rasterio
from .elevation import river_elevation
from .build_step import building_setup

def building_elev(geotiff_path,*args):
    """
    Returns building information for each building in a given region. This includes the geometries, centroid locations, absolute elevation and relative elevation. This building information has been extracted from OpenStreetMaps (OSM).

    Parameters
    ----------
    geotiff_path : str
        This should be the str name of a downloaded geotiff of elevation data that covers the chosen region.
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
        
        
    Returns
    -------
    buildings: geopandas.geodataframe.GeoDataFrame
    	Geodataframe containing building information including location, geometreis, absolute and relative elevations and OSMid for each building
    
    This also returns a pie plot and a bar chart collectively showing the m+n (Default 29) largest building classifications within the given buffer of the rivers within that region
    """
    #River data loaded from other hazard module 
    r = river_elevation(geotiff_path, *args, buffer = 0.005)
    
    #building information from .build_step
    buildings = building_setup(*args)

    #Centroid building to allow for elevtation to be calculated
    buildings['centroid'] = (buildings['geometry'].to_crs(crs=3857).centroid).to_crs(crs=4326) 
    coords_list = [(point.x, point.y) for point in buildings['centroid']] 
    
    #Devermine elevation of buildings
    elev = []
    
    with rasterio.open(geotiff_path) as src:
        vals = src.sample(coords_list)
        for val in vals:
            elev.append(val[0])
    buildings['elevation'] = elev
    
    
    #Building location info 
    building_loc = buildings['centroid'] 
    building_points = []
    for i in list(range(len(building_loc))):
        x, y = building_loc.iloc[i].xy
        points = [Point(x, y) for x, y in zip(x, y)]
        building_points = np.append(building_points, points)

    #river location and elevation info
    riv_points = []
    riv_elev = []
    for i in list(range(len(r['new geometry']))):
        rx, ry  = r['new geometry'].iloc[i].xy
        elev = r['elevations'].iloc[i]
        points = [Point(x, y) for x, y in zip(rx, ry)]
        riv_points = np.append(riv_points, points)
        riv_elev = np.append(riv_elev, elev)
        
    #Calculating relative elevation of the buildings 
    buildings['relative elevation'] = None

    for i in range(len(building_points)):
        p_index = building_points[i].distance(riv_points).argmin()
        elevation = riv_elev[p_index]
        rel_elev = buildings['elevation'].iloc[i] - elevation
        buildings['relative elevation'].iloc[i] = rel_elev         
    
    buildings = buildings[['geometry','centroid' ,'building', 'elevation', 'relative elevation']]
    
    #Removes anomalies which return as ~-30,000 30,000 elevation. 
    buildings = buildings[(buildings['relative elevation'] >= -100) & (buildings['relative elevation'] <= 1000)]
    
    return buildings
    
