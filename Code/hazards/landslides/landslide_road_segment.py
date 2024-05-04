from ..third_party import gpd, pd, Polygon, np, LineString, nx
from .pre_landslide_road_segment import pre_landslide_road_segment

def landslide_road_segment(file, place = None, tags = True, crs = 'EPSG:4326'):
    dataset = pre_landslide_road_segment(file, place = place, tags = tags, crs = crs)
    
    #THIS DATASET SHOULD BE THAT GENERATED BT THE ABOVE CODE
    roads_left = dataset[dataset['Intersept count'].isna()]
    
    #For the graph before:
    df = dataset
    sindex = df.sindex
    # Create a graph
    G = nx.Graph()
    # Iterate over each road segment
    for i, road1 in df.iterrows():
        # Get the bounds of the road segment
        bounds = road1['geometry'].bounds
        # Query the spatial index to find potential intersections
        candidates = list(sindex.intersection(bounds))
        # Iterate over potential intersecting road segments
        for j in candidates:
            if i >= j:
                continue  # Skip duplicate and self-intersection checks
            road2 = df.iloc[j]
            # Check for intersection
            if road1['geometry'].intersects(road2['geometry']):
                G.add_edge(i, j)
    
    # Find connected components
    connected_components = list(nx.connected_components(G))
    # Count the number of connected components
    num_connected_sections = len(connected_components) + 1
    
    df = roads_left
    sindex = df.sindex
    # Create a graph
    G = nx.Graph()
    # Iterate over each road segment
    for i, road1 in df.iterrows():
        # Get the bounds of the road segment
        bounds = road1['geometry'].bounds
        # Query the spatial index to find potential intersections
        candidates = list(sindex.intersection(bounds))
        # Iterate over potential intersecting road segments
        for j in candidates:
            if i >= j:
                continue  # Skip duplicate and self-intersection checks
            road2 = df.iloc[j]
            # Check for intersection
            if road1['geometry'].intersects(road2['geometry']):
                G.add_edge(i, j)
    
    # Find connected components
    connected_components = list(nx.connected_components(G))
    # Count the number of connected components
    num_connected_sections2 = len(connected_components) + 1
    
    
    print("Number of individual connected sections before event:", num_connected_sections)
    print("Number of individual connected sections after event:", num_connected_sections2)
