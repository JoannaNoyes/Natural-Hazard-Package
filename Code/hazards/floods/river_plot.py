from ..third_party import plt , LineString, MultiLineString
from .river_list import river_list


def river_plot(*args, buffer = None, print_list = True):
    river, polygon, buffered_polygon = river_list(*args, buffer = buffer, print_list = print_list)
    
    fig, ax = plt.subplots(figsize =(10,10))
    
    for geom in river['new geometry']:
        if isinstance(geom, MultiLineString):
            for line in geom.geoms:
                x, y = line.coords.xy
                ax.plot(x, y, color='tab:blue')
        elif isinstance(geom, LineString):
        # If it's a LineString, plot it directly
            x, y = geom.coords.xy
            ax.plot(x, y, color='tab:blue')
    x, y = polygon.exterior.xy
    ax.fill(x, y, alpha=0.1, color='green')

    x, y = buffered_polygon.exterior.xy
    ax.plot(x, y, alpha = 0.1, color = 'green', linestyle = '-')

#   plt.title(f'Polygon of {name}, and rivers contained within {buffer} degree buffer of polygon')
    plt.title(f'Polygon of region, and rivers contained within {buffer} degree buffer of polygon')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(linestyle = '--')
    plt.gca().set_aspect('equal')

    # Show the plot
    plt.savefig('river_list.png')
    plt.show()
