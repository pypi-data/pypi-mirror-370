from universal_timeseries_transformer.timeseries_transformer import transform_timeseries
from typing import Optional, List, Union
import pandas as pd
import matplotlib.pyplot as plt
from .basis import *

def plot_timeseries(
    timeseries: pd.DataFrame,
    index_ref: Optional[str] = None,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    figsize: tuple = (12, 6),
    option_main: bool = True,
    option_last_value: Optional[Union[List[str], bool]] = True,
    option_last_name: Optional[Union[bool, List[str]]] = True,
    option_legend_location: str = 'outer',
    option_num_to_show: Union[int, bool] = 2,
    option_ref_area: bool = False,
    decimal_places: int = 2
) -> plt.Figure:
    
    timeseries = transform_timeseries(timeseries, 'dt').copy()

    if timeseries.empty:
        raise ValueError("DataFrame is empty")
    
    numeric_cols = timeseries.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    if option_main:
        ax = plot_main_sub_columns(ax, timeseries, numeric_cols)
    else:
        ax = plot_regular_columns(ax, timeseries, numeric_cols)
    
    ax = set_axis_labels(ax, x_label=x_label or timeseries.index.name or 'Index', y_label=y_label or 'Return')

    if len(numeric_cols) > 1:
        ax = add_legend(ax, option_legend_location=option_legend_location)

    if option_legend_location == 'outer':
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)    

    if title:
        ax = set_plot_title(ax, title)
    else:
        ax = set_plot_title(ax, f'Return (date_ref: {index_ref})')
    
    if index_ref is not None:
        ax = add_reference_lines(ax, timeseries, index_ref, numeric_cols)        
        if option_ref_area:
            ax = add_reference_area(ax, timeseries, index_ref)
    
    if option_last_value:
        if isinstance(option_last_value, bool) and option_last_value:
            base_columns = numeric_cols
        elif isinstance(option_last_value, list):
            base_columns = option_last_value
        else:
            base_columns = []
        
        if base_columns:
            ax = add_last_values(
                ax, timeseries, base_columns, decimal_places, 
                option_main, option_last_name, option_num_to_show
            )
    
    ax = add_grid(ax)
    
    return fig