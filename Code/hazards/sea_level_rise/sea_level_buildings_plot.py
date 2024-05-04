from ..third_party import pd, np, ox, rasterio, Polygon, folium, plt, Point #, classify

def sea_level_buildings_plot(geotiff, place = None, low = 0, high = 50, tag = 'residential'):
    """
    This is a plot of the buildings that fall between the low and high elevation values provided, to visualise the sea level rise risk in a given region. The geotiff data will be used to extract information from OpenStreetMaps (OSM), or an additional place will be required. 

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
    None
    
    This function returned an interactive plot of the buildings and there elevations within the chosen range provided. This is to help visualise the risk within the chosen region
    
    
    Example: hazards.sea_level_buildings_plot('FileName', low = 10, high = 40, tags = True)
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
    
    buildings['elevation (m)'] = flat_elevation.loc[buildings['p'], 'Elevation'].values
    builings_cut = buildings[(buildings['elevation (m)'] < high) & (buildings['elevation (m)'] > low)]
    
    b = builings_cut.dropna(axis=1)

    column_to_color = 'elevation (m)'

    # Define the colormap
    color_map = 'viridis'  # You can choose any colormap available in Matplotlib
    
    return b.explore(column=column_to_color, cmap=color_map)
