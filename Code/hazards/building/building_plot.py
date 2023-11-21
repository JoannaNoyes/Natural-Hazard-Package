from ..third_party import ox, plt

from typing import Union, Tuple

def building_func(*args):
    tags = {'building': True}
    if len(args) == 1 and isinstance(args[0], str):  # If a location has been called
        name = args[0]
        print(f'Processing plot: {name}')
        buildings = ox.features_from_place(name, tags=tags)
        buildings.plot()
        plt.show()
    elif len(args) == 4:  # If a box has been called
        print('Processing lat long grid')
        buildings = ox.features_from_bbox(args[0], args[1], args[2], args[3], tags=tags)  # north, south, east, west
        buildings.plot()
        plt.show()
    else:
        print('Invalid arguments passed')
        print('        4 values: lat1, lat2, lon1, lon2')
        print('        1 value: The name of a given area')

def building_plot(*args):
    """
    Return a plot of the buildings contained within a given region or lat, lon box according to OpenStreetMaps (OSM).

    Parameters
    ----------
    *args: Union[str, Tuple[float, float, float, float]]
        The positional arguments. This accepts either a single string 'location' value, which must be recognized as a region in OSM. Otherwise, 4 float arguments are accepted as 'north, south, east, west', defining a box for the chosen region

    Returns
    -------
    None

    This returns a plot of the building distributions of an area according to OSM.

    Example: hazards.building_plot('Exeter')
    """
    tags = {'waterway': 'river'}
    if len(args) == 1:
        name = args[0]
        try:
            buildings = ox.features_from_place(name, tags={'building': True})
        except Exception as e:
            print(f'{e}')
            print('To find appropriate location names go to https://www.openstreetmap.org/')
        else:
            building_func(name)
    else:
        building_func(args[0], args[1], args[2], args[3])
