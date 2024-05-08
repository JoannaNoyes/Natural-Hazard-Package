from ..third_party import np, pd, ox, rasterio, Polygon, plt

def sea_level_building_density(geotiff, place = None, low = 0, step_size = 10, count = 10, high = None , tag = 'residential', size = 10, title = True):
    """
    This is a plot of the buildings that fall between the low and high elevation values provided, to visualise the sea level rise risk in a given region. The geotiff data will be used to extract information from OpenStreetMaps (OSM), or an additional place will be required. 

    Parameters
    ----------
    geotiff: .tiff
        this is the geotiff file of the DEM elevation data used to assess the chosen region
    place: str
        this is the location provided for OSM to extract data. Without this augument, the extracted data will match the region provided in the DEM dataset. Default = None
    low: int
        this is the lowest elevation of the returned cut buildings. Default = 0 m
    step_size: int
        the elevation steps that will be used to work out the building density. Default = 10 m
    count: int
        this is the number of steps that will be used. Therefore count*stepsize + low will be the maximum elevation used in this function.  Default = 10.
    high: int
        this is the highest elevation of the returned cut buildings. Default = None. This will override the step_size if the elevation calculated from the count and step_size would be higher than this value
    tags: str
        this specifies which buildings to extract from the OSM dataset, e.g. 'residential','commercial',etc. Default = 'residential' 
    size = int            
        This is the size of the figure produced. Default = 10
    title = bool        
        Toggle for the title on the Figure. Default = True   
        
    Returns
    -------
    None
    
    This function returned a plot of the building count as a function of elevation, both relaitve and cumulative.
    
    
    Example: hazards.sea_level_buildings_density('FileName', low = 10, high = 40, tags = True)
    """
    
    count = count + 2
    
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
    
    if place == None:
        #If there is no defined area then must make a polygon to call the buildings with
        end_x = a * m + b
        end_y = c * n + d 
        polygon = Polygon([(b,d), (b,end_y), (end_x, end_y), (end_x,d)])
        buildings = ox.features_from_polygon(polygon, tags = {'building':tag})
    else:
        buildings = ox.features_from_place(place, tags = {'building':tag})
        
    buildings['centroid'] = (buildings['geometry'].to_crs(crs = 3857).centroid).to_crs(crs = 4326)
    
    buildings['p'] = (( buildings['centroid'].y - d ) / c ).astype(int) * m + (( buildings['centroid'].x - b ) / a).astype(int)
    buildings = buildings[buildings['p'] >= 0]
    
    numbers = []
    cum_num = []
    cumulative = 0
    
    if high != None:
        count = int((high - low) / step_size) + 2
    
    
    for i in list(range(1,count)):
        maxim = low + i * step_size
        minim = low + (i - 1) * step_size
        p_values = result_matrix[(elevation < maxim) & (elevation > minim)]
        buildings_covered = buildings[buildings['p'].isin(p_values)]
        number = np.shape(buildings_covered)[0]
        numbers = np.append(numbers, number)
        cumulative = cumulative + number
        cum_num = np.append(cum_num, cumulative)
    x = list(range(low,(low + (count -1) * step_size), step_size))
    fig, ax1 = plt.subplots(figsize = (size, size*0.7))
    
    # Plot the first dataset with the left y-axis
    ax1.plot(x, numbers, color='tab:blue')
    ax1.set_xlabel('elevation (m)')
    ax1.set_ylabel('Building Count', color='tab:blue')
    
    # Create a twin Axes object
    ax2 = ax1.twinx()
    
    # Plot the second dataset with the right y-axis
    ax2.plot(x, cum_num, color='tab:orange')
    ax2.set_ylabel(f'Cumulative Building Count', color='tab:orange')
    if title == True:
    	plt.title(f'{tag} building count with increasing elevation')
    
    plt.savefig(f'Sea_Level_Exposure_{step_size}m.png')
    plt.show()
