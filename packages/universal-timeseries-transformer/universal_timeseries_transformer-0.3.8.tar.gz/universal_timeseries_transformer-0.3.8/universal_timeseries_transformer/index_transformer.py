from datetime import datetime
import pandas as pd
import numpy as np

def map_dates_str_to_datetimes(dates):
    if not isinstance(dates, (list, pd.Series, pd.Index)):  
        raise TypeError("Input must be a list, pandas Series, or Index")
       
    if not all(isinstance(date, str) for date in dates):
         raise TypeError("All elements must be strings")
         
    try:
         return pd.to_datetime(dates)
    except Exception as e:
         raise ValueError(f"Failed to convert dates: {str(e)}")


def map_datetimes_to_dates_str(dates):
    if not isinstance(dates, (list, pd.Series, pd.DatetimeIndex, pd.Index)):  # pd.Index 추가
        raise TypeError("Input must be a list, pandas Series, DatetimeIndex, or Index")
    
    if isinstance(dates, (list, pd.Series)):
        if not all(isinstance(date, (datetime, pd.Timestamp)) for date in dates):
            raise TypeError("All elements must be datetime objects")
    
    return pd.Series(dates).dt.strftime('%Y-%m-%d')


def map_datetimes_to_unix_timestamps(dates):
    if not isinstance(dates, (list, pd.Series, pd.DatetimeIndex, pd.Index)):  # pd.Index 추가
        raise TypeError("Input must be a list, pandas Series, DatetimeIndex, or Index")
    
    if isinstance(dates, (list, pd.Series)):
        if not all(isinstance(date, (datetime, pd.Timestamp)) for date in dates):
            raise TypeError("All elements must be datetime objects")
    
    return pd.Series(dates).astype('int64') // 10**9


def map_dates_str_to_unix_timestamps(dates):
    if not isinstance(dates, (list, pd.Series, pd.Index)):  # pd.Index 추가
        raise TypeError("Input must be a list, pandas Series, or Index")
    
    if not all(isinstance(date, str) for date in dates):
        raise TypeError("All elements must be strings")
        
    try:
        return pd.to_datetime(dates).astype('int64') // 10**9  # 직접 변환
    except Exception as e:
        raise ValueError(f"Failed to convert dates: {str(e)}")
    

def map_unix_timestamps_to_datetimes(timestamps):
    if not isinstance(timestamps, (list, pd.Series, pd.Index)):
        raise TypeError("Input must be a list, pandas Series, or Index")
    
    if not timestamps:
        raise ValueError("Input cannot be empty")
    
    if not all(isinstance(ts, (int, np.int64, float, np.float64)) for ts in timestamps):
        raise TypeError("All elements must be numeric (int or float)")
    
    sample_ts = timestamps[0]
    
    if sample_ts < 1e9:
        unit = 's'
    elif sample_ts < 1e12:
        unit = 'ms'
    else:
        unit = 'ns'
    
    try:
        return pd.to_datetime(timestamps, unit=unit)
    except Exception as e:
        raise ValueError(f"Failed to convert timestamps with unit '{unit}': {str(e)}")