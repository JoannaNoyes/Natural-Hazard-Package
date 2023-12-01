from ..third_party import ox, np, Polygon

def river(*args): #, buffer = None):
    """
    Get rivers within the given region (box or area) through OpenStreetMaps (OSM), returning all rivers that intersect the chosen region as well as the Polygon of the region chosen
    
    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
    	The positional arguments. This accepts either a single string 'location' value, which must be recognised as a region in OSM. Otherwise 4 float arguements are accepted as 'north, south, east, west', defining a box for the chosen region
    		
    Returns 
    -------
    river: geopandas.geodataframe.GeoDataFrame
    	This is a list of the rivers contained within the region: their node id from OSM, their lat,lon node locations and the river name
    polygon: shapely.geometry.polygon.Polygon
    	A polygon of the given region
    """

    tags = {'waterway': 'river'} #Only want river waterways 
    river_data = []
    #The following print the geometries ('geometries') and the geometry that is interested as a Polygon ('polygon'). 
    #If no rivers are present in the location, the code will stop and not print out results
    if len(args) == 1 and isinstance(args[0], str):
        name = args[0]
        print(f'Processing rivers in: {name}')
        geometries = ox.features_from_place(name, tags=tags)
        
        shape = ox.features_from_place(name, tags={'name': name})
        polygon = shape.unary_union #Calculate polygon on the region. 
                
        if len(geometries) == 0:
            print(f'No rivers found in {name}')
            exit
        else:
            river_data.append((name, geometries))
    elif len(args) == 4:
        print('Processing rivers in lat long grid')
        geometries = ox.features_from_bbox(args[0], args[1], args[2], args[3], tags=tags)
        
        polygon= Polygon([(args[3],args[1]),(args[3],args[0]),(args[2],args[0]),(args[2],args[1])])
        
        if len(geometries) == 0:
            print('No rivers found in grid')
            exit
        else:
            river_data.append(('LatLongGrid', geometries))
            
    #This is for when the wrong number of arguments is passed
    else:
        print('Argument is not callable. Either-')
        print('        4 values: lat1, lat2, lon1, lon2')
        print('        1 value: The name of a given area')
        
    #This will print every unique river name within the given region. This will be printed as the code is run. 
    unique_names = river_data[0][1]['name'].dropna().unique()
    
    print(river_data[0][1]['name'].nunique(), 'Unique Rivers Extracted:')
    for value in unique_names:
        print('      ', value)
    return river_data[0][1][['geometry', 'name']], polygon

   
