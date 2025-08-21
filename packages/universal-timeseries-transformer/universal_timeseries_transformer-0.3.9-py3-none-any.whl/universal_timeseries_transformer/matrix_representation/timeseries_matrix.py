import numpy as np
from functools import cached_property
from typing import List, Any, Optional, Union
import pandas as pd
from universal_timeseries_transformer.visualizer.utils import plot_timeseries
from universal_timeseries_transformer.timeseries_transformer import transform_timeseries
from universal_timeseries_transformer.timeseries_application import (
    transform_timeseries_to_cumreturns_ref_by_index,
    transform_timeseries_to_cumreturns,
    transform_timeseries_to_returns,
)

class TimeseriesMatrix:
    """
    Time series matrix wrapper with lazy-loaded transformations.
    
    Cached Properties:
        basis: Index values as numpy array
        dates: Index values as list
        date_i: First date in series
        date_f: Last date in series
        returns: Calculated returns DataFrame
        cumreturns: Calculated cumulative returns DataFrame
        datetime: DataFrame with datetime index
        unixtime: DataFrame with unix timestamp index
        string: DataFrame with string index
    
    Manual Cache Properties:
        cumreturns_ref: Reference-based cumulative returns DataFrame (needs invalidation)
    """
    
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    @cached_property
    def basis(self) -> np.ndarray:
        return self.df.index.values

    @cached_property
    def dates(self) -> List[Any]:
        return list(self.basis)

    @cached_property
    def date_i(self) -> Any:
        return self.dates[0]
    
    @cached_property
    def date_f(self) -> Any:
        return self.dates[-1]

    @cached_property
    def datetime(self) -> pd.DataFrame:
        return transform_timeseries(self.df, 'datetime')
    
    @property
    def dt(self) -> pd.DataFrame:
        return self.datetime

    @cached_property
    def timestamp(self) -> pd.DataFrame:
        return transform_timeseries(self.df, 'unix_timestamp')
    
    @cached_property
    def unixtime(self) -> pd.DataFrame:
        return self.timestamp
    
    @cached_property
    def string(self) -> pd.DataFrame:
        return transform_timeseries(self.df, 'str')

    @cached_property
    def returns(self) -> pd.DataFrame:
        return transform_timeseries_to_returns(self.df)

    @cached_property
    def cumreturns(self) -> pd.DataFrame:
        return transform_timeseries_to_cumreturns(self.df)
    
    def row(self, i: int) -> pd.DataFrame:
        return self.df.iloc[[i], :]

    def column(self, j: int) -> pd.DataFrame:
        return self.df.iloc[:, [j]]
        
    def row_by_name(self, name: str) -> pd.DataFrame:
        return self.df.loc[[name], :]

    def column_by_name(self, name: str) -> pd.DataFrame:
        return self.df.loc[:, [name]]

    def component(self, i: int, j: int) -> Any:
        return self.df.iloc[i, j]

    def component_by_name(self, name_i: str, name_j: str) -> Any:
        return self.df.loc[name_i, name_j]

    def rows(self, i_list: List[int]) -> pd.DataFrame:
        return self.df.iloc[i_list, :]
        
    def columns(self, j_list: List[int]) -> pd.DataFrame:
        return self.df.iloc[:, j_list]

    def rows_by_names(self, names: List[str]) -> pd.DataFrame:
        return self.df.loc[names, :]
        
    def columns_by_names(self, names: List[str]) -> pd.DataFrame:
        return self.df.loc[:, names]

    def get_cumreturns_ref(self, index_ref: str) -> pd.DataFrame:
        df = transform_timeseries_to_cumreturns_ref_by_index(self.string, index_ref)
        self.cumreturns_ref = df
        self.index_ref = index_ref
        return df
        
    def plot(
            self, 
            option_main: bool = True, 
            option_last_value: Optional[Union[List[str], bool]] = True, 
            option_last_name: Optional[Union[bool, List[str]]] = False, 
            option_num_to_show: Union[int, bool] = 1, 
            option_ref_area: bool = True, 
            decimal_places: int = 2, 
            title: Optional[str] = None,
            x_label: Optional[str] = None,
            y_label: Optional[str] = None,
            figsize: tuple = (12, 6),
            ):
        if not hasattr(self, 'index_ref'):
            self.get_cumreturns_ref(index_ref=self.date_i)
        
        plot_timeseries(
            timeseries=self.cumreturns_ref, 
            index_ref=self.index_ref,
            option_main=option_main, 
            option_last_value=option_last_value, 
            option_last_name=option_last_name, 
            option_num_to_show=option_num_to_show, 
            option_ref_area=option_ref_area, 
            decimal_places=decimal_places, 
            title=title,
            x_label=x_label,
            y_label=y_label,
            figsize=figsize,
            )