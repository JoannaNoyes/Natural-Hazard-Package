def find_area_column(df):
    #function to find the area column of a dataset
    area_columns = [col for col in df.columns if 'area' in col.lower()]
    
    if len(area_columns) == 0:
        print('FAILURE: No area column found, please enter manually with the area argument')
        return None
    elif len(area_columns) > 1:
        print("FAILURE: Multiple 'area' columns detected, please enter manually with the area argument")
        return None
    else:
        return area_columns[0]
