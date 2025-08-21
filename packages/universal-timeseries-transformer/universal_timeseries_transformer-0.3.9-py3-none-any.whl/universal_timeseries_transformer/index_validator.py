import pandas as pd
import numpy as np

def is_valid_dataframe(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    return True

def is_datetime_index(index):
    return isinstance(index, pd.DatetimeIndex)

def is_string_index(index):
    return all(isinstance(idx, str) for idx in index)

def is_unix_timestamp_index(index):
    return all(isinstance(idx, (int, np.int64, float, np.float64)) for idx in index)

def validate_index_type(index):
    if not any([
        is_datetime_index(index),
        is_string_index(index),
        is_unix_timestamp_index(index)
    ]):
        raise TypeError("Index must be datetime, unix timestamp, or string type")
