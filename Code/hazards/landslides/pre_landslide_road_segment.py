from ..third_party import gpd, pd, ox, Polygon, plt

def pre_landslide_road_segment(file, place = None, tags = True, crs = 'EPSG:4326'):
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
        
        ax = roads['geometry'].plot(figsize=(6, 6), alpha = 0.3, color = 'tab:green')
        cut_roads['geometry'].plot(ax = ax, label = '')
        ax.set_xlabel('longitude')
        ax.set_ylabel('latitude')
        if tags == True:
            	plt.savefig('road_cut.png')
        else:
        	plt.savefig(f'road_{tags}_cut.png')
            
        return roads
