from ..third_party import plt, gpd, pd, ox, Polygon

def landslide_road_length(file, place = None, tags = True, crs = 'EPSG:4326'):
    """
    Return the cut_landslides, and cut road dataframes which are both the reduced dataframes of the landslides and roads cut down to only those that intersect each other. The landslide data is provided through the file loaded and the road data is extracted from OpenStreetMaps (OSM). It also provides a graph showing the road and landslides in that region and highlights where they are intersecting 

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
    cut_landslides: geopandas.geodataframe.GeoDataFrame
        this is a list of the landslides contained in the dataframe provided that are intersected by atleast one road
    cut_roads: geopandas.geodataframe.GeoDataFrame
        this is a list of the road contained in the dataframe extracted from OSM that are intersepted by a landslide
    
    Example: hazards.landslide_road_length('Japan Data/Sekiguchi_and_Sato_2006.shp')
    """
    #Load files 
    landslides = gpd.read_file(file)
    
    #Check if there are geometry polygons in the dataset
    landslides[landslides['geometry'].geom_type != 'Point']
    
    if len(landslides) == 0:
        print('WARNING: There are no geometries found in the provided landslide dataset')
        print('         The provided cut road dataset is empty') 
    else:
        #Set the crs to be the correct thing and mention if dataset does not have an associated crs
        if landslides.crs is None:
            current_crs = crs 
            landslides.crs = current_crs
            print('CAUTION: The dataset does not include coordinate reference system (crs) information')
            print('         This uses a default crs of ESPG:4326 (lat/lon), change if necessary')
        
        #Ensure lat lon column of the geomtries
        target_crs='EPSG:4326'
        landslides['lon/lat geometry'] = landslides['geometry'].to_crs(target_crs)
        
        #Extract road data from OSM
        if place == None:
            x_min, y_min, x_max, y_max = landslides['lon/lat geometry'].total_bounds
        
            boundary_box = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
            roads = ox.features_from_polygon(boundary_box, tags = {'highway': tags})
        else:
            roads = ox.features_from_place(place, tags = {'highway': tags})
        
        #ensure that there is no node values in the road dataset
        roads_reset = roads.reset_index()
        roads = roads_reset[roads_reset['element_type'] != 'node']#= roads[roads['element_type'] != 'node']
        
        #Interseption code:
        landslides['intersept'] = 0 #will be a count of the number of roads an landslide has intersepted
        cut_roads = gpd.GeoDataFrame(roads.iloc[0]).T
        
        for i in range(len(roads)):  #For all of the roads
            b = landslides['lon/lat geometry'].intersects(roads['geometry'].iloc[i]).astype(int) #How  often road intersected
            landslides['intersept'] = landslides['intersept'] + b  #Create count for number of times that landslide has intersepted
            c = pd.Series(b).sum() #how many intersepts?
            if c !=0:
                # Update this line to use .loc instead of directly modifying the GeoDataFrame
                roads.loc[roads.index[i], 'Intersept count'] = c #If not 0 then add that road to list of intersected roads showing freq of interseption
                c1 = gpd.GeoDataFrame(roads.loc[roads.index[i]]).T
                cut_roads =  pd.concat([cut_roads,c1])
        cut_roads = cut_roads.iloc[1:]        #Remove first filler row on list of effected trunk roads
        
        
        #Calculations of road lengths and percentages:
        total_road_area = roads.to_crs('EPSG:3857').length.sum(0) #set to m based crs
        road_distance = 0
        for i in range(len(landslides)):
            b = roads[roads['geometry'].intersects(landslides['lon/lat geometry'].iloc[i])].intersection(landslides['lon/lat geometry'].iloc[i])
            if len(b) > 0:
                road_distance  = road_distance + b.to_crs('EPSG:3857').length.values[0]
        
        #percentage calucalation
        percentage_distance = 100 - ( total_road_area - road_distance ) / total_road_area * 100
        
        #prints and graph plot 
        print('Length of road effected by landslides (m) =', road_distance)
        if tags == True:
            print('Percentage of road network impacted =', percentage_distance,'%')
        else:
            print(f'Percentage of {tags} road network impacted =', percentage_distance,'%')
        if road_distance != 0:
            ax = roads['geometry'].plot(figsize=(10, 10), alpha = 0.3, color = 'tab:green')
            cut_roads['geometry'].plot(ax = ax, label = '')
            landslides['lon/lat geometry'].plot(ax = ax, color = 'grey', alpha = 0.7)
            landslides[landslides['intersept'] > 0]['lon/lat geometry'].plot(ax = ax, color = 'red')
            ax.set_xlabel('longitude')
            ax.set_ylabel('latitude')
            
            plt.savefig('landslides_roads_cut.png')
            
            
            cut_landslides = landslides[landslides['intersept'] > 0]
            return cut_landslides, cut_roads
        else:
            print('Failure: There is no intersept between the two datasets provided')
