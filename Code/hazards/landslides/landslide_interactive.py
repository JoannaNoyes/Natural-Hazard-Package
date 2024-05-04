from ..third_party import gpd , ox, folium, MarkerCluster, Polygon 
from .find_area_column import find_area_column

def landslide_interactive(file, place = None, tags = True, crs = 'EPSG:4326', intersept = True, area = None, n = None, total = True):
    """
    Return the 

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
    intersept: bool
        this is a toggle for whether the intersept landslides are highlighted on the end plot. Default = True, meaning that they will be highlighted.
    area: str
        this is by default = None. This augument only needs filling is the area column within the data cannot be determined and needs manually inputting.
    n: float, int
        this is the top n number of landslides that should be highlighted on the graph. Default = None, meaning this will not be shown automatically. This will appear as an outline of the otherwise coloured regions
    total: bool
        this is a toggle for whether all of the landslides should be present on the plot outside of the intersepted and largest landslides. Default = True, meaning they will appear. 
        

    Returns
    -------
    None
    
    This function returns an interactive map of the region and the associated landslides called
    
    Example: hazards.landslide_road_length('Japan Data/Sekiguchi_and_Sato_2006.shp')
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

    
    #area column 
    if area is None:
        area_column = find_area_column(landslides)
    else:
        area_column = area
        print(f'area_column manually set to {area}')
    
    if area_column is None:
        return None
    else:
        if area is not None:
            area_column = area
            print(f'Area column manually set to {area}')
        else:
            print('Area column identified:',area_column)
        
        #largest n number wanted 
        if n != None:
            landslides_size = landslides.sort_values(by = f'{area_column}', ascending=False)
            landslides_large = landslides_size.iloc[:n]
            landslides_large_min = landslides_large[f'{area_column}'].min()
            
        #Find the intersepting roads for the landslides 
        if intersept == True:
            landslides['intersept'] = 0
            for i in range(len(roads)):  #For all of the  roads
                b = landslides['lon/lat geometry'].intersects(roads['geometry'].iloc[i]).astype(int) #How  often road intersected
                landslides['intersept'] = landslides['intersept'] + b  #Create count for number of times that landslide has intersepted
        
            landslides['lon/lat geometry'] = landslides['lon/lat geometry'].apply(lambda geom: geom.__geo_interface__)
        
            cut_landslides = landslides[landslides['intersept'] > 0 ]
            
            #if you also want the n largest values coloured seperately...
            if n != None:
                landslides_large['lon/lat geometry'] = landslides_large['lon/lat geometry'].apply(lambda geom: geom.__geo_interface__)
            
            ncut_landslides = landslides[landslides['intersept'] == 0 ]
            
        else: #No intersepts wanted 
            landslides['lon/lat geometry'] = landslides['lon/lat geometry'].apply(lambda geom: geom.__geo_interface__)
            ncut_landslides = landslides
            
        #values to set for the middle of the plot 
        x_mid = x_min + ( x_max - x_min ) / 2
        y_mid = y_min + ( y_max - y_min ) / 2
        centre = y_mid,x_mid
        
        
        #plotting iteractive map 
        h = folium.Map(location = centre)
        if total == True:
            folium.GeoJson(
            ncut_landslides,
            tooltip=folium.features.GeoJsonTooltip(fields=[f'{area_column}'], label=True),
                style_function=lambda feature: {
                    'color': 'gray',  # Set the color for landslides
                    'weight': 2,
                    'fillOpacity': 0.2,
                    'Opacity' : 0.5}).add_to(h)
            print('grey = landslides')
        #Next data only needed if intersepts are wanted 
        if intersept == True:
            folium.GeoJson(cut_landslides, tooltip = folium.features.GeoJsonTooltip(fields = [f'{area_column}', 'intersept'], label = True),
                style_function=lambda feature: {
                    'color': 'red',  # Set the color for landslides_cut
                    'weight': 2,
                    'fillOpacity': 0.5}).add_to(h)
            if tags == True:
                print('red  = landslides that intersept the local road network')
            else:
                print(f'red  = landslides that intersept the local {tags} road network')
        if n != None:
            folium.GeoJson(landslides_large, tooltip = folium.features.GeoJsonTooltip(fields = [f'{area_column}'], label = True),
                style_function=lambda feature: {
                    'color': 'blue',  # Set the color for landslides_cut
                    'weight': 2,
                    'fillOpacity': 0}).add_to(h) #0 fill so the colour of the landslides can be seen underneath 
            print(f'blue = largest {n} landslides')
            
        #Set the borders of the plot so that it changes based off of the data given 
        sw = y_min, x_min
        ne = y_max, x_max
        h.fit_bounds([sw, ne]) 

        marker_cluster = MarkerCluster().add_to(h)

        display(h)
