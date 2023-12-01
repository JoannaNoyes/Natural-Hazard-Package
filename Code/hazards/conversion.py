from .third_party import np 

def conversion(*args):
#Temperary place holder to calculate km distances in the river_data package. 



    radius = 6371.0
    if len(args) == 4:
        lat1, long1, ref_lat, ref_lon = args

        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(ref_lat)
        lon1_rad = np.radians(long1)
        lon2_rad = np.radians(ref_lon)
        
    #   for lat distance: 
        dlon = 0 - 0
        dlat = lat2_rad - lat1_rad
        
        lat = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        lat = 2 * np.arctan2(np.sqrt(lat), np.sqrt(1 - lat))
        lat_distance = radius * lat 
        
    #    for long distance:
        dlon = lon2_rad - lon1_rad
        dlat = 0
        
        lon = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        lon = 2 * np.arctan2(np.sqrt(lon), np.sqrt(1 - lon))
        lon_distance = radius * lon 
        return lat_distance, lon_distance
    
    if len(args) == 2:
        lat1, long1 = args
        ref_lat, ref_lon = 0, 0 
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(ref_lat)
        lon1_rad = np.radians(long1)
        lon2_rad = np.radians(ref_lon)
        
    #   for lat distance: 
        dlon = 0 - 0
        dlat = lat2_rad - lat1_rad
        
        lat = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        lat = 2 * np.arctan2(np.sqrt(lat), np.sqrt(1 - lat))
        lat_distance = radius * lat 
        
    #    for long distance:
        dlon = lon2_rad - lon1_rad
        dlat = 0
        
        lon = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        lon = 2 * np.arctan2(np.sqrt(lon), np.sqrt(1 - lon))
        lon_distance = radius * lon 
        
        return lat_distance, lon_distance
    
    else:
        print('Invalid arguments passed')
        print('        4 values: lat, lon, reference lat, reference lon')
        print('        2 value: lat, lon, the reference location will be assumed to be 0,0') 
