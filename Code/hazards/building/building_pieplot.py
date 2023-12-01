from ..third_party import np, ox, pd, plt
from .build_step import building_setup


def building_pie_func(*args, n = 9, m = 20):
    """
    Return a pie plot of n categories (plus other) and a bar chart of m categories for the top n+m building classifications in the chosen region. These building classifications have been extracted from OpenStreetMaps (OSM)

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
    
    n: float, Optional
    	n is the number of categories portrayed on the piechart. This will be the largest n categories of building classifications. The pie chart will then compile an 'other' categories for the remaining building types. Default = 9
    m: float, Optional
    	m is the number of categories displayed on the bar chart. This is the m largest classifications contained within the 'other' category. Default = 20. 

    Returns
    -------
    None
    
    This returns a pie plot and a bar chart collectively showing the m+n (Default 29) largest building classifications in a chosen region

    
    """
    #Extract building information
    buildings = building_setup(*args)
       
    #remove nan values, and seperate values into pieplot and bar chart
    b = buildings['building'].dropna(how='all')
    pie = [[],[]]
    for i in range(len(b.unique())):
        s = b.str.contains(b.unique()[i]).sum()
        pie[0] = np.append(pie[0], b.unique()[i]) #This is creating the pie chart dataset for each 
        pie[1] = np.append(pie[1], s) 
    data = pd.DataFrame(pie).T
    data_asc = data[1:].sort_values([1], ascending=[False])
    print('number of yes', data_asc[data_asc[0] == 'yes'].count())
    data_asc = data_asc[data_asc[0] != 'yes']
    data_asc = data_asc[data_asc[0] != 'no']
    
    data_asc_top = data_asc[:n].set_index(0)
    data_asc_bot = data_asc[n+1:n+1+m] #Set the no. of values in piechart and barchart
    
    data_asc_top.loc[len(data_asc_top.index)] = [data_asc_bot[1].sum()] 
    data_asc_top = data_asc_top.rename(index={n: 'Other'})
    
    
    #Plot the figure:
    fig, ax = plt.subplots(1, 2, figsize=(15, 8))

    plt.subplot(1, 2, 1) 
    plt.pie(data_asc_top[1], labels =data_asc_top.index, colors = plt.cm.tab10(np.arange(10)))
    plt.title('10 Key Building Types')
    
    plt.subplot(1, 2, 2) 
    plt.bar(data_asc_bot[0], data_asc_bot[1], color=plt.cm.tab10(np.arange(10)))
    plt.xticks(rotation=90)
    plt.grid(linestyle = "dashed" , alpha = 0.5)
    plt.title('Other Building Types')




def building_pieplot(*args, n = 9, m = 20):
    tags = {'waterway': 'river'} 
    if len(args) == 1:
        name = args[0]
        try:
            buildings = ox.features_from_place(name, tags={'building': True, })
        except Exception as e:
            print(f'{e}')
            print(f'To find appropriate location names go to https://www.openstreetmap.org/')
        else:
            building_pie_func(name, n = n)
    elif len(args) == 4:
        building_pie_func(args[0], args[1], args[2], args[3], n = n, m = m)
    else:
        print('Invalid arguments passed. Either -')
        print('        2 values: The name of a given area, number of building types in pie chart')
        print('        5 values: lat1, lat2, lon1, lon2, number of building types in pie chart')
