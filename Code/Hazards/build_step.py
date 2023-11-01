from .third_party import ox 

def building_setup(*args):
    """
    Return the building data for a chosen region. The returned dataframe contains the building amenity, geometry, building classification and type extracted from OpenStreetMaps (OSM). This function is used in many of the other functions that produce building related plots

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region

    Returns
    -------
    buildings: geopandas.geodataframe.GeoDataFrame
    	This is a geodataframe of the important building information extracted from OSM including the building classification, amenity, geometry and type

    
    """
    tags = {'building': True, }
    if len(args) == 1 and isinstance(args[0], str):
        name = args[0]
        print(f'Processing plot: {name}')
        buildings = ox.geometries_from_place(name, tags=tags)
    elif len(args) == 4:
        print('Processing lat long grid')
        buildings = ox.geometries_from_bbox(args[0], args[1], args[2], args[3], tags=tags) #north, south, east, west
    else:
        print('Invalid arguments passed. Either -')
        print('        1 values: The name of a given area, number of building types in pie chart, number of values of bar plot')
        print('        4 values: lat1, lat2, lon1, lon2, number of building types in pie chart, number of values of bar plot')

    return buildings[['amenity', 'geometry', 'building', 'type']]
