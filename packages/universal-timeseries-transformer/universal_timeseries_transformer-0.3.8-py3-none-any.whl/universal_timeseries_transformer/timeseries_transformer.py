"""Timeseries transformation utilities for converting between different index formats."""

from enum import Enum
from typing import Union
import pandas as pd

from .index_transformer import (
   map_dates_str_to_datetimes,
   map_datetimes_to_dates_str,
   map_datetimes_to_unix_timestamps,
   map_dates_str_to_unix_timestamps,
   map_unix_timestamps_to_datetimes
)
from .index_validator import (
   is_valid_dataframe,
   is_datetime_index,
   is_string_index,
   is_unix_timestamp_index,
   validate_index_type
)


class TypeFormat(Enum):
   """Supported timeseries index formats."""
   STRING = "string"
   DATETIME = "datetime"
   UNIX_TIMESTAMP = "unix_timestamp"


# Alias mappings for backward compatibility
FORMAT_ALIASES = {
   'str': TypeFormat.STRING,
   'dt': TypeFormat.DATETIME,
   'timestamp': TypeFormat.UNIX_TIMESTAMP,
}


def transform_to_timeseries_with_str(timeseries: pd.DataFrame) -> pd.DataFrame:
   """Transform timeseries index to string format."""
   is_valid_dataframe(timeseries)
   df = timeseries.copy()
   
   if is_datetime_index(df.index):
       df.index = map_datetimes_to_dates_str(df.index)
   elif is_unix_timestamp_index(df.index):
       df.index = map_datetimes_to_dates_str(map_unix_timestamps_to_datetimes(df.index))
   elif not is_string_index(df.index):
       validate_index_type(df.index)
   
   return df


def transform_to_timeseries_with_datetime(timeseries: pd.DataFrame) -> pd.DataFrame:
   """Transform timeseries index to datetime format."""
   is_valid_dataframe(timeseries)
   df = timeseries.copy()
   
   if is_datetime_index(df.index):
       return df
   elif is_string_index(df.index):
       try:
           df.index = map_dates_str_to_datetimes(df.index)
       except Exception as e:
           raise ValueError(f"Failed to convert string index to datetime: {str(e)}")
   elif is_unix_timestamp_index(df.index):
       try:
           df.index = map_unix_timestamps_to_datetimes(df.index)
       except Exception as e:
           raise ValueError(f"Failed to convert unix timestamp to datetime: {str(e)}")
   else:
       validate_index_type(df.index)
   
   return df


def transform_to_timeseries_with_unixtime(timeseries: pd.DataFrame) -> pd.DataFrame:
   """Transform timeseries index to unix timestamp format."""
   is_valid_dataframe(timeseries)
   df = timeseries.copy()
   
   if is_datetime_index(df.index):
       df.index = map_datetimes_to_unix_timestamps(df.index)
   elif is_string_index(df.index):
       try:
           df.index = map_dates_str_to_unix_timestamps(df.index)
       except Exception as e:
           raise ValueError(f"Failed to convert string index to unix time: {str(e)}")
   elif not is_unix_timestamp_index(df.index):
       validate_index_type(df.index)
   
   return df


def transform_timeseries(
   timeseries: pd.DataFrame, 
   option_type: Union[str, TypeFormat]
) -> pd.DataFrame:
   """
   Transform timeseries index to specified format.
   
   Args:
       timeseries: Input DataFrame with time-based index
       option_type: Target format ('string', 'datetime', 'unix_timestamp', 'dt', 'str', 'timestamp') or TimeseriesFormat enum
       
   Returns:
       DataFrame with transformed index
       
   Raises:
       TypeError: If input is not a pandas DataFrame
       ValueError: If option_type is invalid
   """
   if not isinstance(timeseries, pd.DataFrame):
       raise TypeError("Input must be a pandas DataFrame")
   
   # Normalize input to enum
   if isinstance(option_type, str):
       if option_type in FORMAT_ALIASES:
           target_format = FORMAT_ALIASES[option_type]
       else:
           try:
               target_format = TypeFormat(option_type)
           except ValueError:
               valid_options = list(FORMAT_ALIASES.keys()) + [e.value for e in TypeFormat]
               raise ValueError(f"Invalid option_type: '{option_type}'. Valid options: {valid_options}")
   else:
       target_format = option_type
   
   mapping_transformers = {
       TypeFormat.STRING: transform_to_timeseries_with_str,
       TypeFormat.DATETIME: transform_to_timeseries_with_datetime,
       TypeFormat.UNIX_TIMESTAMP: transform_to_timeseries_with_unixtime,
   }
   MAPPING_INDEX_NAMES = {
    TypeFormat.STRING: 'date',
    TypeFormat.DATETIME: 'datetime',
    TypeFormat.UNIX_TIMESTAMP: 'timestamp',
   }
   
   transformer = mapping_transformers[target_format]
   transformed_df = transformer(timeseries).rename_axis(MAPPING_INDEX_NAMES[target_format])
   
   print(f"Transformed timeseries to {type(transformed_df.index[0])} index")
   return transformed_df