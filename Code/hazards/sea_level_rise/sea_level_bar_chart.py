from ..third_party import np, pd, ox, rasterio, Polygon, plt

def sea_level_bar_chart(geotiff, place = None, low = 0, step_size = 10, count = 5, tag_list = None, chart_type = 'linear', split = True, size = 10, title = True):
    """
    A bar chart of the distribution of building types with different sea level elevations, as well as a DataFrame of the values shown in this plot (the building types, elevations and counts per layer). 

    Parameters
    ----------
    geotiff: .tiff
        this is the geotiff file of the DEM elevation data used to assess the chosen region
    place: str
        this is the location provided for OSM to extract data. Without this augument, the extracted data will match the region provided in the DEM dataset. Default = None
    low: int
        this is the lowest elevation of the returned cut buildings. Default = 0 m
    step_size: int
        the elevation steps that will be used to work out the building density. Default = 10 m
    count: int
        this is the number of steps that will be used. Therefore count*stepsize + low will be the maximum elevation used in this function.  Default = 5.
    tags: str list
        this specifies which buildings to extract from the OSM dataset, e.g. 'residential','commercial',etc. Default tag_list = ['residential', 'retail', 'commercial', 'hospital', 'school'] This should be a list of building types to be able to add to the barchart. This should include 'residential'.  
    chart_type: str
        This can be 'log' or 'linear', which specifies whether you want the information to be shown on a log or linear scale. Default = 'linear'.
    split = bool
        This specifies whether to show the residential information on a seperate log scale from the other information, if that information is of linear scale. This can help with visualisation of this information. Default = True. 
    size = int            
        This is the size of the figure produced. Default = 10
    title = bool        
        Toggle for the title on the Figure. Default = True
        
    Returns
    -------
    bar_chart: dataframe
        This is a dataframe of the building types, elevations and the corresponding count for each of these categories. This allows for additional interpretations to be made with these results if that is desired. 
        
    
    This function returned a stacked bar chart of the buidling types with each bar representing the building type, the stacks representing each new elevation step and the bar heights the count of that building type at the elevation for the given area. 
    
    
    Example: hazards.sea_level_bar_chart('FileName', low = 10)
    """

    #Extract the necessary elevation information and the subsequent lat lon information
        
    src = rasterio.open(geotiff)
    elevation = src.read(1)
    with rasterio.open(geotiff) as dem:
        transform = dem.transform
    b = transform[2]
    d = transform[5]
    a = transform[0]
    c = transform[4]
    
    #Create dataset of 1,2,3,4,...,n*m-2
    n,m = np.shape(elevation)
    linear_sequence = np.arange(n*m)
    result_matrix = linear_sequence.reshape((n,m))
    
    #Flatten the elevation
    flat_elevation = pd.DataFrame({'Elevation': elevation.flatten()})
    
    if tag_list == None:
        tag_list = ['residential', 'retail', 'commercial', 'hospital', 'school']
    else:
        tag_list = tag_list 
    
    
    if split == True:
        if 'residential' not in tag_list:
            print('Split = True requires a residential tag to be passed within the tag_list augement')
            return    
        
    column_names = [f'Column{i}' for i in range(1, count + 1)]
    bar_chart = pd.DataFrame(index = tag_list, columns = column_names)         
    column = ['Nan']
    
    j = 0 
    for i in list(range(1, count + 1)):
        j = j + 1
        maxim = low + i * step_size
        minim = low + (i - 1) * step_size
        p_values = result_matrix[(elevation < maxim) & (elevation > minim)]
        column = np.append(column, f'{minim}-{maxim}m')
        
        for tag in tag_list: 
            if place == None:
                #If there is no defined area then must make a polygon to call the buildings with
                end_x = a * m + b
                end_y = c * n + d 
                polygon = Polygon([(b,d), (b,end_y), (end_x, end_y), (end_x,d)])
                buildings = ox.features_from_polygon(polygon, tags = {'building':tag})
            else:
                buildings = ox.features_from_place(place, tags = {'building':tag})
            
            if len(buildings) == 0:
                
                bar_chart[f'Column{j}'][tag] = 0
            else:
                buildings['centroid'] = (buildings['geometry'].to_crs(crs = 3857).centroid).to_crs(crs = 4326)
                
                buildings['p'] = (( buildings['centroid'].y - d ) / c - 1).astype(int) * m + (( buildings['centroid'].x - b ) / a - 1).astype(int)
                buildings = buildings[buildings['p'] >= 0]
                
                bar_chart[f'Column{j}'][tag] = buildings[buildings['p'].isin(p_values)]['p'].count()

                
    column = column[1:]
    bar_chart.columns= column
    
    
    #residential = bar_chart.loc['residential']
    #other = bar_chart[bar_chart.index != 'residential']
    
    #PLOT
    #ALL BELOW IS PLOT BASED OFF WHETHER IT IS A SPLIT OR NOT
    if split == False:
        fig, ax = plt.subplots(figsize=(size, size*0.6))
    
        # Set the index as the x-axis ticks
        x = np.arange(len(bar_chart.index))
        
        # Initialize bottom for the stacked bar
        bottom = np.zeros(len(bar_chart.index))
        
        # Plot each column as a stacked bar
        for column in bar_chart.columns:
            ax.bar(x, bar_chart[column], bottom=bottom, label=column)
            bottom += bar_chart[column]
        
            
        min_value = 0.9  # Adjust this value as needed
        ax.set_ylim(bottom=min_value)    
        
        # Set labels and title
        ax.set_xlabel('Building Types')
        ax.set_yscale(chart_type)
        ax.set_ylabel('Building Count')
        ax.set_title('Stacked Bar Chart of Building Types Impacted by Sea Level Rise')
        ax.set_xticks(x)
        ax.set_xticklabels(bar_chart.index)
        ax.legend()
        
        plt.show()
    
    else:
        if 'residential' not in tag_list:
            print('Split = True requires a residential tag to be passed within the tag_list augement')
        else:
                #residential = pd.DataFrame(bar_chart.loc['residential']).T
            other = bar_chart[bar_chart.index != 'residential']
            
            #PLOT
            
            width_ratios = [ other.count().values[0], 1]
        
            # Create subplots with different widths
            fig, (ax1, ax2)  = plt.subplots(1, 2, figsize=(size, size*0.8), gridspec_kw={'width_ratios': width_ratios}, sharey=False)
        
            # Set the index as the x-axis ticks
            x = np.arange(len(other.index))
            
            # Initialize bottom for the stacked bar
            bottom = np.zeros(len(other.index))
            
            # Plot each column as a stacked bar
            for column in other.columns:
                ax1.bar(x, other[column], bottom=bottom, label=column)
                bottom += other[column]
            
            #ax.bar(x, residential, bottom=bottom, label='residential')
                
            min_value = 0.9  # Adjust this value as needed
            ax1.set_ylim(bottom=min_value)    
            
            # Set labels and title
            ax1.set_xlabel('Building Types')
            ax1.set_yscale(chart_type)
            ax1.set_ylabel('Building Count')
            if title == True:
            	ax1.set_title('Stacked Bar Chart of Building Types Impacted by Sea Level Rise')
            ax1.set_xticks(x)
            ax1.set_xticklabels(other.index)
            ax1.legend()
            
            #Residential log plot:
            #residential_data = pd.Series(bar_chart.loc['residential'])
            residential_data = bar_chart.loc['residential'].squeeze()
            
            
            
            # Plot
            bottom = 0
            for label, height in residential_data.items():
                ax2.bar(0, height, bottom=bottom, label=label)
                bottom += height
            
            ax2.set_xlabel('residential', color = 'red')
            ax2.set_ylabel('Building Count (log)', color = 'red')
            ax2.set_yscale('log')
            ax2.yaxis.tick_right()
            ax2.yaxis.set_label_position("right")
            ax2.set_xticks([])
            ax2.set_ylim(bottom=min_value)  
            ax2.spines['left'].set_linewidth(2)
            
            # Remove space between subplots
            plt.subplots_adjust(wspace=0)
            
            plt.savefig('bar_chart_SLR.png')
            plt.show()
                    
        
    return bar_chart
