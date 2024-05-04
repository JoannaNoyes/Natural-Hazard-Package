from ..third_party import ox,np, plt, gpd, Polygon

def landslide_map(file, place = None, tags = True, crs = 'EPSG:4326'):
    """
    Return the landslides, roads and bounding box associated with the provided landslide datafile and region of interest. The roads are extracted from OpenStreetMaps (OSM). It also provides a graph showing the road and landslides in that region

    Parameters
    ----------
    file: .shp
        this is the geotiff file of the landslide data containing geometries
    place: str
        this is the location provided for OSM to extract data. Without this augument, the extracted data will match the region provided in the landslide dataset. Default = None
    tags: str
        this specifies which roads to extract from the OSM dataset, e.g. 'trunk','primary',etc. Default = True, meaning all roads types are extracted
    crs: str
        this provides the coordinate reference system of the landslide data. This is only necessary if the dataset does not have a specified crs, and has a default setting of the lat lon crs = 'EPSG:4326'.

    Returns
    -------
    landslides: geopandas.geodataframe.GeoDataFrame
        this is a list of all the landslides contained in the dataframe provided
    roads: geopandas.geodataframe.GeoDataFrame
        this is a list of all the road contained in the dataframe extracted from OSM
    boundary_box: shapely.geometry.polygon.Polygon
        this is a shapely box representing the extent of the figure and the region containing all the landslides
    	
    This returns a plot of the road and landslide distributions of the area according to OSM.
    
    Example: hazards.basic_map('Japan Data/Sekiguchi_and_Sato_2006.shp')
    """
    #load data
    landslides = gpd.read_file(file)
    
    
    #guarentee there is a lat lon column for geometries so that it can be connected to the OSM data
    #Check is the data has an associated crs
    if landslides.crs is None:
        current_crs = crs 
        landslides.crs = current_crs
        print('CAUTION: This uses a default crs (coordinate reference system) of ESPG:4326, change if necessary')
    target_crs='EPSG:4326'
    landslides['lon/lat geometry'] = landslides['geometry'].to_crs(target_crs)
    
    #load OSM data
    x_min, y_min, x_max, y_max = landslides['lon/lat geometry'].total_bounds
    boundary_box = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
    
    if place == None:
        roads = ox.features_from_polygon(boundary_box, tags = {'highway': tags})
    else:
        roads = ox.features_from_place(place, tags = {'highway': tags})
    
    #Remove node roads so they dont muddy up the graph
    roads_reset = roads.reset_index()
    roads = roads_reset[roads_reset['element_type'] != 'node']#= roads[roads['element_type'] != 'node']
    
    #Plot
    ax = landslides['lon/lat geometry'].plot(figsize=(10, 10), alpha=0.5, color = 'darkgray')
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    roads.plot(ax = ax)
    #boundary_box.plot(ax = ax)

    # Set plot title
    if tags == True:
        plt.title('Landslide locations and regional road network')
        plt.savefig('landslides_roads.png')
    else:
        plt.title(f'Landslide locations and {tags} road network')
        plt.savefig(f'landslides_{tags}_roads.png')    
    

    # Show the plot
    plt.show()   
    
    return landslides, roads, boundary_box
