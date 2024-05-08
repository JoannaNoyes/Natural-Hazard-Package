from .buffer_river import river_buffer
from .build_step import building_setup
from ..third_party import Polygon, gpd, np, ox, pd, plt

def buffered_piechart(*args, buffer_distance=0.003, inner_distance = None, river_cutoff=0.005, n = 9, m = 20, print_list = True):
    """
    Return a pie plot of n categories (plus other) and a bar chart of m categories for the top n+m building classifications in the chosen region. These building classifications have been extracted from OpenStreetMaps (OSM).
    This pieplot specifically returns the buildings classifications within the degree buffer_distance from the river profile. 

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
        
    buffer_distance: float, Optional
    	buffer_distance is the degree distance from the river in which the buildings are counted. Buildings outside this distance are rejected. Default = 0.003 degrees.
    	
    inner_distance: float, Optional 
    	inner_distance is the degree distance from the river that is cut out of the buffer_distance. This would allow for regions between x and y degrees from the river, not just all buildings up to some value of y. Default = None. 
     
    
    river_cutoff: float, Optional
    	river_cutoff is the degree distance outside of the polygon/region chosen after which the river points are not included in creating buffer. Default = 0.005 degrees. 
    
    n: float, Optional
    	n is the number of categories portrayed on the piechart. This will be the largest n categories of building classifications. The pie chart will then compile an 'other' categories for the remaining building types. Default = 9
    m: float, Optional
    	m is the number of categories displayed on the bar chart. This is the m largest classifications contained within the 'other' category. Default = 20. 

    Returns
    -------
    shape: Polygon
    	Shape is the buffer region in which the buildings are being counted from 
    
    This also returns a pie plot and a bar chart collectively showing the m+n (Default 29) largest building classifications within the given buffer of the rivers within that region
    """
    #Pull River data from .river_buffer()
    riv, pol, buf = river_buffer(*args, buffer_distance= buffer_distance , river_cutoff= river_cutoff, print_list = print_list)
    if inner_distance is not None:
        riv2, pol2, buf2 = river_buffer(*args, buffer_distance=inner_distance, river_cutoff=river_cutoff, print_list = False)
    buildings = building_setup(*args)

	#Find only the buildings within the given buffer region buf and buf2.
    buildings['intersects_buff'] = buildings['geometry'].apply(lambda poly: poly.intersects(buf))
    
    buildings = buildings[buildings['intersects_buff']]
    shape = buf
    if inner_distance is not None:
    	buildings['intersects_buff'] = buildings['geometry'].apply(lambda poly: poly.disjoint(buf2))
    	buildings = buildings[buildings['intersects_buff']]
    	shape = buf.difference(buf2)
    
    #Piechart with the new truncated dataset
    b = buildings['building'].dropna(how='all')
    pie = [[],[]]
    for i in range(len(b.unique())):
        s = b.str.contains(b.unique()[i]).sum()
        pie[0] = np.append(pie[0], b.unique()[i]) #This is creating the pie chart dataset for each 
        pie[1] = np.append(pie[1], s) 
    data = pd.DataFrame(pie).T
    data_asc = data[1:].sort_values([1], ascending=[False])
    #print('number of yes', data_asc[data_asc[0] == 'yes'].count())
    data_asc = data_asc[data_asc[0] != 'yes']  #Remove 'yes' and 'no' column from piechart plot. 
    data_asc = data_asc[data_asc[0] != 'no']
    
    data_asc_top = data_asc[:n].set_index(0)
    data_asc_bot = data_asc[n+1:n+1+m]  #Seperating the values on the piechart and barchart 
    
    data_asc_top.loc[len(data_asc_top.index)] = [data_asc_bot[1].sum()] 
    data_asc_top = data_asc_top.rename(index={n: 'Other'})
  
    
    #Plot
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))

    plt.subplot(1, 2, 1) 
    plt.pie(data_asc_top[1], labels =data_asc_top.index, colors = plt.cm.tab10(np.arange(10)))
    plt.title(f'10 Key Building Types found within buffer {buffer_distance} and {inner_distance}')
    
    plt.subplot(1, 2, 2) 
    plt.bar(data_asc_bot[0], data_asc_bot[1], color=plt.cm.tab10(n))
    plt.xticks(rotation=90)
    plt.grid(linestyle = "dashed" , alpha = 0.5)
    plt.title('Other Building Types')
    
    
    plt.savefig(f'buffered_piechart_{inner_distance}_{buffer_distance}.png')
    
    return shape
