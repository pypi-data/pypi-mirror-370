import pandas as pd

def map_timeseries_with_str_index_to_timeseries_with_datetime_index(timeseries):
    if not isinstance(timeseries, pd.DataFrame):
         raise TypeError("Input must be a pandas DataFrame")
         
    if not all(isinstance(idx, str) for idx in timeseries.index):
         raise TypeError("All index elements must be strings")
    
    df = timeseries.copy()
    try:
         df.index = pd.to_datetime(df.index)
         return df
    except Exception as e:
         raise ValueError(f"Failed to convert index: {str(e)}")

def map_timeseries_with_datetime_index_to_timeseries_with_str_index(timeseries):
    if not isinstance(timeseries, pd.DataFrame):
         raise TypeError("Input must be a pandas DataFrame")
         
    if not isinstance(timeseries.index, pd.DatetimeIndex):
         raise TypeError("DataFrame must have DatetimeIndex")
    
    df = timeseries.copy()
    df.index = df.index.strftime('%Y-%m-%d')
    return df
