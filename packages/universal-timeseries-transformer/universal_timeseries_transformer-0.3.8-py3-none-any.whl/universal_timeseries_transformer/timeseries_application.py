def get_df_returns_from_prices(df_prices):
    df_returns = df_prices.pct_change().fillna(0) * 100
    df_returns.columns = [f"return: {col}" for col in df_returns.columns]
    return df_returns

def get_df_cumreturns_from_prices(df_prices):
    df_cumreturns = (df_prices / df_prices.iloc[0] - 1) * 100
    df_cumreturns.columns = [f"cumreturn: {col}" for col in df_cumreturns.columns]
    return df_cumreturns

map_prices_to_returns = get_df_returns_from_prices
map_prices_to_cumreturns = get_df_cumreturns_from_prices

transform_prices_to_returns = map_prices_to_returns
transform_prices_to_cumreturns = map_prices_to_cumreturns

def transform_timeseries_to_returns(timeseries):
    df_returns = timeseries.pct_change().fillna(0) * 100
    df_returns.columns = [f"return: {col}" for col in df_returns.columns]
    return df_returns

def transform_timeseries_to_cumreturns(timeseries):
    df_cumreturns = (timeseries / timeseries.iloc[0] - 1) * 100
    df_cumreturns.columns = [f"cumreturn: {col}" for col in df_cumreturns.columns]
    return df_cumreturns

def transform_timeseries_to_cumreturns_ref_by_series(timeseries, srs_ref):
    cumreturns_ref = (timeseries / srs_ref - 1) * 100
    cumreturns_ref.columns = [f"cumreturn: {col}" for col in cumreturns_ref.columns]
    return cumreturns_ref

def transform_timeseries_to_cumreturns_ref_by_series_ref_date(timeseries, date_ref):
    srs_row_ref = timeseries.loc[date_ref]
    cumreturns_ref = transform_timeseries_to_cumreturns_ref_by_series(timeseries, srs_row_ref)
    return cumreturns_ref

def transform_timeseries_to_cumreturns_ref_by_index(timeseries, index_ref):
    srs_row_ref = timeseries.loc[index_ref]
    cumreturns_ref = transform_timeseries_to_cumreturns_ref_by_series(timeseries, srs_row_ref)
    return cumreturns_ref

map_timeseries_to_returns = transform_timeseries_to_returns
map_timeseries_to_cumreturns = transform_timeseries_to_cumreturns
map_timeseries_to_cumreturns_ref_by_index = transform_timeseries_to_cumreturns_ref_by_index
map_timeseries_to_cumreturns_ref_by_series = transform_timeseries_to_cumreturns_ref_by_series