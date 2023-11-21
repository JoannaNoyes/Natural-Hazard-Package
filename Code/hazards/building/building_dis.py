from ..third_party import Point, np, ox, rasterio, gpd, wkt, plt
from ..river.river_list import river_list

def building_dis(*args):
    """
    Returns building information for each building in a given region. This includes the geometries, centroid locations and distance in m from the rivers in the chosen area. This building information has been extracted from OpenStreetMaps (OSM).

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
        
        
    Returns
    -------
    buildings: geopandas.geodataframe.GeoDataFrame
    	Geodataframe containing building information including location, geometreis, distance from river (m) and OSMid for each building

    This also returns a plot of the cumulative river plot with respect to distance. 
    
    """
    #River data loaded from other hazard module 
    r, p, bp = river_list(*args, buffer = 0.005)
    
    #Absolute elevation of buildings
    if len(args) == 4:
        buildings = ox.features_from_bbox(*args, tags={'building' : True})
    elif len(args) == 1:
        buildings = ox.features_from_place(*args, tags={'building' : True})
    else:
        print(f'Incorrect number of arguments. Got {len(args)+1}, expected:')
        print('         1: name of location recognised by OSM')
        print('         4: north, south, east, west points of area')
    
    
    buildings['centroid'] = (buildings['geometry'].to_crs(crs=3857).centroid).to_crs(crs=4326) 
    coords_list = [(point.x, point.y) for point in buildings['centroid']] 
    
    
    #Building location info 
    
    building_loc = buildings['centroid'] 
    building_points = []
    for i in list(range(len(building_loc))):
        x, y = building_loc.iloc[i].xy
        points = [Point(x, y) for x, y in zip(x, y)]
        building_points = np.append(building_points, points)

    #river location info
    riv_points = []
    for i in list(range(len(r['new geometry']))):
        rx, ry  = r['new geometry'].iloc[i].xy
        points = [Point(x, y) for x, y in zip(rx, ry)]
        riv_points = np.append(riv_points, points)
         
    #Calculating the distances. 
    
    distance = []
    
    for i in range(len(building_points)):
        p_index = building_points[i].distance(riv_points).argmin()
        distance = np.append(distance, building_points[i].distance(riv_points[p_index]))
    
    buildings['distance degrees'] = distance

    max_dis = buildings['distance degrees'].max()
    #distance_bins = range(0, math.ceil(max_dis) + 1, 30)
    distance_bins = np.linspace(0, max_dis, 200)

    building_count = []

    for i in range(len(distance_bins) - 1):
        count = len(buildings[(buildings['distance degrees'] >= distance_bins[i]) & 
                                  (buildings['distance degrees'] < distance_bins[i + 1])]) #binning 
        building_count.append(count)

    
    cum_building_count = np.cumsum(building_count)

    plt.figure(figsize = (10,6))
    plt.plot(distance_bins[:-1], cum_building_count, linewidth = 3)
    plt.xlabel('distance in degrees from River')
    plt.ylabel('cumulative building count')
    plt.ylim(0, max(cum_building_count) + 100)
    plt.xlim(0, buildings['distance degrees'].max())
    plt.grid()

    
    
    return buildings[['geometry','centroid' ,'building', 'distance degrees']]
    
    
    
    
    
    
    
    
