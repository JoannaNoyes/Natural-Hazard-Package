from .build_step import building_setup
from ..third_party import ox, plt, np, pd, px

def building_treemap_func(*args, n = 9):
    buildings = building_setup(*args)
        
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
    

    fig = px.treemap(data_asc_top, path = [data_asc_top.index], values = data_asc_top.columns[0], title = f'Top n buiding types')
    #fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    fig.show()



def building_treemap(*args, n = 9):
    tags = {'waterway': 'river'} 
    if len(args) == 1:
        name = args[0]
        try:
            buildings = ox.features_from_place(name, tags={'building': True, })
        except Exception as e:
            print(f'{e}')
            print(f'To find appropriate location names go to https://www.openstreetmap.org/')
        else:
            building_treemap_func(name, n = n)
    elif len(args) == 4:
        building_treemap_func(args[0], args[1], args[2], args[3], n = n)
    else:
        print('Invalid arguments passed. Either -')
        print('        2 values: The name of a given area, number of building types in treemap')
        print('        5 values: lat1, lat2, lon1, lon2, number of building types in treemap')
