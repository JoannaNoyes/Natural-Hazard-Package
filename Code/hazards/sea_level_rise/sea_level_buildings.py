from ..third_party import pd, np, ox, Polygon, rasterio, Point

def sea_level_buildings(geotiff, place = None, low = 0, high = 10, tag = 'residential'):
    """
    Return the buildings and cut_buildings which are the reduced dataframes of the buildings, all optained from OpenStreetMaps (OSM). The cut_buildings are cut based off of the chosen elevations called by the function and help to highlight which buildings are within certain regions of risk.

    Parameters
    ----------
    geotiff: .tiff
        this is the geotiff file of the DEM elevation data used to assess the chosen region
    place: str
        this is the location provided for OSM to extract data. Without this augument, the extracted data will match the region provided in the DEM dataset. Default = None
    tags: str
        this specifies which buildings to extract from the OSM dataset, e.g. 'residential','commercial',etc. Default = 'residential'
    low: int
        this is the lowest elevation of the returned cut buildings. Default = 0 m
    high: int
        this is the highest elevation of the returned cut buildings. Default = 10 m 
    Returns
    -------
    buildings: geopandas.geodataframe.GeoDataFrame
        this is a list of all the buildings within the called region
    cut_buildings: geopandas.geodataframe.GeoDataFrame
        this is a list of the buildings contained in the dataframe that falls between the low and high elevations picked
    
    
    Example: hazards.sea_level_buildings('FileName', low = 10, high = 40, tags = True)
    """
    #Extract the necessary elevation information and the subsequent lat lon information
    src = rasterio.open(geotiff)
    elevation = src.read(1)
    with rasterio.open(geotiff) as dem:
        transform = dem.transform
    b = transform[2]
    d = transform[5]
    a = transform[0]
    c = transform[4]
    
    #Create dataset of 1,2,3,4,...,n*m-2
    n,m = np.shape(elevation)
    linear_sequence = np.arange(n*m)
    result_matrix = linear_sequence.reshape((n,m))
    
    #Flatten the elevation
    flat_elevation = pd.DataFrame({'Elevation': elevation.flatten()})
    end_x = a * m + b
    end_y = c * n + d 
    polygon = Polygon([(b,d), (b,end_y), (end_x, end_y), (end_x,d)])
    
    if place == None:
        #If there is no defined area then must make a polygon to call the buildings with
        buildings = ox.features_from_polygon(polygon, tags = {'building':tag})
    else:
        buildings = ox.features_from_place(place, tags = {'building':tag})
        
        
    buildings['centroid'] = (buildings['geometry'].to_crs(crs = 3857).centroid).to_crs(crs = 4326)
    
    if place != None:
    	build_points = buildings['centroid'].apply(Point)
    	buildings = buildings[polygon.contains(build_points)]
    
    
    buildings['p'] = (( buildings['centroid'].y - d ) / c - 1).astype(int) * m + (( buildings['centroid'].x - b ) / a - 1).astype(int)
    buildings = buildings[buildings['p'] >= 0]
    
    p_values = result_matrix[(elevation < high) & (elevation > low)]
    buildings_covered = buildings[buildings['p'].isin(p_values)]
    
    return buildings, buildings_covered
