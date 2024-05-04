from ..third_party import plt, gpd, ox, Polygon 
from .find_area_column import find_area_column 

def landslide_area(file, place = None, tags = True, crs = 'EPSG:4326', area = None):
    """
    Return the cut_landslides which are the reduced dataframes of the landslides and roads cut down to only those that intersect each other. The landslide data is provided through the file loaded and the road data is extracted from OpenStreetMaps (OSM). It also provides a graph showing the road and landslides in that region and highlights where they are intersecting. The area of the intersepted landslides is also provided, along with the percentage of the total landslide area that this is.

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
    area: str
        this is by default = None. This augument only needs filling is the area column within the data cannot be determined and needs manually inputting.

    Returns
    -------
    cut_landslides: geopandas.geodataframe.GeoDataFrame
        this is a list of the landslides contained in the dataframe provided that are intersected by atleast one road
    
    Also returns the total area of the intersepted landslides, the percentage of the total, and a plot of all the landslides and the intersepted landslides
    
    Example: hazards.landslide_area('Japan Data/Sekiguchi_and_Sato_2006.shp')
    """
    #Load in the landslides 
    landslides = gpd.read_file(file)
    
    #Finding geometries and then working out the crs and setting a column to lat lon geometries
    landslides[landslides['geometry'].geom_type != 'Point']
    if len(landslides) == 0:
        print('WARNING: There are no geometries found in the provided landslide dataset')
        print('         The provided cut road dataset is empty') 
    else:
        if landslides.crs is None:
            current_crs = crs 
            landslides.crs = current_crs
            print('CAUTION: This uses a default crs (coordinate reference system) of ESPG:4326 (lat/lon), change if necessary')
        
    
        target_crs='EPSG:4326'
        landslides['lon/lat geometry'] = landslides['geometry'].to_crs(target_crs)
        
        
        #Load in road data
        if place == None:
            x_min, y_min, x_max, y_max = landslides['lon/lat geometry'].total_bounds
        
            boundary_box = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
            roads = ox.features_from_polygon(boundary_box, tags = {'highway': tags})
        else:
            roads = ox.features_from_place(place, tags = {'highway': tags})
        
        roads_reset = roads.reset_index()
        roads = roads_reset[roads_reset['element_type'] != 'node']#= roads[roads['element_type'] != 'node']
    
        #Find the area column of the data:
        area_column = find_area_column(landslides)
        if area_column is None:
            return None
        else:
            print('Area column identified:',area_column)
            landslides['intersept'] = 0
            for i in range(len(roads)):  #For all of the trunk roads
                b = landslides['lon/lat geometry'].intersects(roads['geometry'].iloc[i]).astype(int) #How  often road intersected
                landslides['intersept'] = landslides['intersept'] + b  #Create count for number of times that landslide has intersepted
            
            #Calculate area of landslides:
            area = landslides[landslides['intersept'] > 0][f'{area_column}'].sum()
            #percentage of the total area 
            percentage_area = 100 - ( ( landslides[f'{area_column}'].sum() - landslides[landslides['intersept'] > 0][f'{area_column}'].sum() ) / landslides[f'{area_column}'].sum() )*100
            #print values 
            print('The total area of the intersepted landslides=', area)
            print('[NOTE: The units of this area depend on dataset]')
            print('The Percentage of the total landslide area=',percentage_area,'%')
            
            #plot
            ax = landslides.plot(figsize=(10, 10), color = 'grey', alpha = 0.7)
            landslides[landslides['intersept'] > 0].plot(ax = ax, color = 'red')
            ax.set_xlabel('longitude')
            ax.set_ylabel('latitude')
            plt.savefig('landslides.png')
            
            cut_landslides = landslides[landslides['intersept'] > 0]
            return cut_landslides
        #????
