from ..third_party import np, plt, loads, gpd, ox, Point, Polygon, MultiPolygon

def earthquake_buffer(*args, lat = None, lon = None):
    """
    Return a plot of the buildings contained within a given region or lat, lon box according to OpenStreetMaps (OSM), with buffered rings of 0.01 degrees to represent simple earthquake spreading.

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
    
    lat: float, Optional
    	lat is the latitude location of the earthquake epicentre. Default= centre of the passed region.
    lon: float, Optional
    	lon is the longitude location of the earthquake epicentre. Default= centre of the passed region. 

    Returns
    -------
    None

    This returns a plot of the building distributions of an area according to OSM with buffers on top to represent the earthquake distribution as well a marker for the earthquake epicentre.

    Example: hazards.buffered_buildings('Exeter')
    """
    tags = {'waterway': 'river'}
    #Set up and producing building data
    tags = {'building': True, }
    if len(args) == 1 and isinstance(args[0], str): #If a location has been called
        name = args[0]
        print(f'Processing plot: {name}')
        buildings = ox.features_from_place(name, tags=tags)
    elif len(args) == 4:  #If a box has been called
        print('Processing lat long grid')
        buildings = ox.features_from_bbox(args[0], args[1], args[2], args[3], tags=tags) #north, south, east, west
    else:
        print('Invalid arguments passed')
        print('        6 values: lat1, lat2, lon1, lon2, lat = {lat of epicenter}, lon = {lon of epicenter}')
        print('        3 value: The name of a given area, lat = {lat of epicenter}, lon = {lon of epicenter}')
    bounds = buildings.total_bounds
    
    #If there isnt a earthquake location then set as the centre of buildings
    if lat is None:
        lat = bounds[1] + ( ( bounds[3] - bounds[1] ) / 2 )
    if lon is None:
        lon = bounds[0] + ( ( bounds[2] - bounds[0] ) / 2 )
    
    ratio = ( bounds[3] - bounds[1] ) / ( bounds[2] - bounds[0] )
    
    
    point = gpd.GeoDataFrame({'geometry': [Point(lon, lat)]}, geometry='geometry')
    
    #Create plot for buffer of eathquakes in region
    fig, ax = plt.subplots(figsize=(15* ratio, 15)) 
    
    # Plot the point
    point.plot( ax = ax, color='red', marker = 'x', markersize = 150)
    
    #point['buffer'].plot(ax=ax, color='tab:orange', alpha = 0.05, linewidth=1)
    
    for i in list(range(20)):
        buffer = point['geometry'].buffer(0.01*i)
        buffer.plot(ax=ax,color='tab:orange', alpha = 0.1, linewidth=1, edgecolor = 'tab:red')
        
        buffer_geometry = buffer.iloc[0]
        buffer_polygon = loads(str(buffer_geometry))
        
        more = False
        for j in list(range(len(buildings))):
            inside = buildings['geometry'][j].within(buffer_polygon) 
            if inside == False:
                more = True
                break
        if more == True:
            continue
        if more == False:
            break
            
    ax = buildings.plot(ax=ax)                
    plt.xlim(bounds[0] - 0.005, bounds[2] + 0.005)
    plt.ylim(bounds[1] - 0.005, bounds[3] + 0.005)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    plt.show()
