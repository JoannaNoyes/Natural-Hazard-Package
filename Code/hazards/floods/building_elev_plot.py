from ..third_party import plt, np
from .building_elev import building_elev

def building_elev_plot(geotiff_path,*args):
    buildings = building_elev(geotiff_path,*args)
    
    colourmap = np.arange(buildings['relative elevation'].min(), buildings['relative elevation'].max(), 1)
    cmap = plt.get_cmap('rainbow_r')
    x_min, y_min, x_max, y_max = buildings['geometry'].total_bounds
    difference = ( x_max - x_min ) / ( y_max - y_min )
    fig, ax = plt.subplots(figsize=(12*difference, 12))

    buildings.plot(column='relative elevation', cmap=cmap, ax=ax)
    
# Set axis labels and title
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Buildings Colored by Elevation')

    sm = plt.cm.ScalarMappable(cmap=cmap)
    sm.set_array(colourmap)  
    cbar = plt.colorbar(sm, ax=ax, label='relative Elevation to River /m')


# Display the plot
    plt.savefig('building_elevation_graph.png')
    plt.show()
    
