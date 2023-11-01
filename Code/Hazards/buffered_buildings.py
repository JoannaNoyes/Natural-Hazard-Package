from .buffer_river import river_buffer
from .build_step import building_setup
from .third_party import Polygon, gpd, np, ox, pd, plt

def buffered_buildings(*args, buffer_distance=0.003, river_cutoff=0.005, n = 9, m = 20):
    """
    Return a pie plot of n categories (plus other) and a bar chart of m categories for the top n+m building classifications in the chosen region. These building classifications have been extracted from OpenStreetMaps (OSM).
    This pieplot specifically returns the buildings classifications within the degree buffer_distance from the river profile. 

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
    buffer_distance: float, Optional
    	buffer_distance is the degree distance from the river in which the buildings are counted. Buildings outside this distance are rejected. Default = 0.003 degrees.
    
    river_cutoff: float, Optional
    	river_cutoff is the degree distance outside of the polygon/region chosen after which the river points are not included in creating buffer. Default = 0.005 degrees. 
    
    n: float, Optional
    	n is the number of categories portrayed on the piechart. This will be the largest n categories of building classifications. The pie chart will then compile an 'other' categories for the remaining building types. Default = 9
    m: float, Optional
    	m is the number of categories displayed on the bar chart. This is the m largest classifications contained within the 'other' category. Default = 20. 

    Returns
    -------
    None
    
    This returns a pie plot and a bar chart collectively showing the m+n (Default 29) largest building classifications within the given buffer of the rivers within that region
    """
    riv, pol, buf = river_buffer(*args) #, buffer_distance=0.003, river_cutoff=0.005)
    buildings = building_setup(*args)

    buildings['intersects_buff'] = buildings['geometry'].apply(lambda poly: poly.intersects(buf))


    buildings = buildings[buildings['intersects_buff']]
    
    b = buildings['building'].dropna(how='all')
    pie = [[],[]]
    for i in range(len(b.unique())):
        s = b.str.contains(b.unique()[i]).sum()
        pie[0] = np.append(pie[0], b.unique()[i]) #This is creating the pie chart dataset for each 
        pie[1] = np.append(pie[1], s) 
    data = pd.DataFrame(pie).T
    data_asc = data[1:].sort_values([1], ascending=[False])
    #print('number of yes', data_asc[data_asc[0] == 'yes'].count())
    data_asc = data_asc[data_asc[0] != 'yes']
    
    data_asc_top = data_asc[:n].set_index(0)
    data_asc_bot = data_asc[n+1:n+1+m] 
    
    data_asc_top.loc[len(data_asc_top.index)] = [data_asc_bot[1].sum()] 
    data_asc_top = data_asc_top.rename(index={n: 'Other'})
    
#    if len(data_asc_bot)>= m:
        
#    if len(data_asc_bot)>= m:
#        data_asc_bot = data_asc_bot[data_asc_bot[1] >= 3]
    
    
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))

    plt.subplot(1, 2, 1) 
    plt.pie(data_asc_top[1], labels =data_asc_top.index, colors = plt.cm.tab10(np.arange(10)))
    plt.title(f'10 Key Building Types found within buffer {buffer_distance}')
    
    plt.subplot(1, 2, 2) 
    plt.bar(data_asc_bot[0], data_asc_bot[1], color=plt.cm.tab10(np.arange(10)))
    plt.xticks(rotation=90)
    plt.grid(linestyle = "dashed" , alpha = 0.5)
    plt.title('Other Building Types')
