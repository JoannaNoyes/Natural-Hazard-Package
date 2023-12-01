from .build_step import building_setup
from ..third_party import ox, plt, np, pd, px

def building_treemap(*args, n = 9):
    """
    Return a treemap of n categories (plus other) for the top n building classifications in the chosen region. These building classifications have been extracted from OpenStreetMaps (OSM)

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region
    
    n: float, Optional
    	n is the number of categories portrayed on the piechart. This will be the largest n categories of building classifications. The pie chart will then compile an 'other' categories for the remaining building types. Default = 9

    Returns
    -------
    None
    
    This returns a treemap showing the n (Default 9) largest building classifications in a chosen region
    
    """
    tags = {'building': True, }
    if len(args) == 1 and isinstance(args[0], str):
        name = args[0]
        print(f'Processing plot: {name}')
        buildings = ox.features_from_place(name, tags=tags)
    elif len(args) == 4:
        print('Processing lat long grid')
        buildings = ox.features_from_bbox(args[0], args[1], args[2], args[3], tags=tags) #north, south, east, west
    else:
        print('Invalid arguments passed. Either -')
        print('        2 values: The name of a given area, n = number of building types in treemap')
        print('        5 values: lat1, lat2, lon1, lon2, n = number of building types in treemap')
        
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
    
    data_asc_top = data_asc[:n].set_index(0)
    data_asc_bot = data_asc[n+1:] 
    
    data_asc_top.loc[len(data_asc_top.index)] = [data_asc_bot[1].sum()] 
    data_asc_top = data_asc_top.rename(index={n: 'Other'})
    

    fig = px.treemap(data_asc_top, path = [data_asc_top.index], values = data_asc_top.columns[0], title = 'Top 10 buiding types')
    #fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.show()



    
