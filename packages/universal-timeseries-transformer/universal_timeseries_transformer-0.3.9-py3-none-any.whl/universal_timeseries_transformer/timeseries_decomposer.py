import pandas as pd

def decompose_timeserieses_to_list_of_timeserieses(timeseries: pd.DataFrame, option_dropna=True) -> list[pd.DataFrame]:
    def dropna_in_df(df: pd.DataFrame, option_dropna: bool) -> pd.DataFrame:
        return df.dropna() if option_dropna else df
    return [dropna_in_df(timeseries[[col]], option_dropna) for col in timeseries.columns]

def concatenate_timeserieses(list_of_timeseries: list[pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(list_of_timeseries, axis=1)

map_timeserieses_to_list_of_timeserieses = decompose_timeserieses_to_list_of_timeserieses
map_list_of_timeserieses_to_timeserieses = concatenate_timeserieses
