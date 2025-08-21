from functools import partial

def get_benchmark_index(timeseries, index_benchmark=1, name_benchmark=None):
    return (timeseries.T.index.get_loc(name_benchmark) 
            if name_benchmark 
            else index_benchmark)

def create_two_column_df(timeseries, benchmark_index, column_index):
    return timeseries.iloc[:, [column_index, benchmark_index]]

# def split_timeseries_to_two_columned_timeseries(timeseries, index_benchmark=1, name_benchmark=None):
#     df = timeseries.copy()
#     benchmark_index = get_benchmark_index(df, index_benchmark, name_benchmark)
#     create_df_with_benchmark = partial(create_two_column_df, df, benchmark_index)
#     return list(map(create_df_with_benchmark, range(len(df.columns))))

def filter_prefix_of_timeseries_column_name(name_benchmark, prefix):
    name_benchmark = name_benchmark.replace(prefix,'')
    name_benchmark = f'{prefix}{name_benchmark}'
    return name_benchmark

def split_timeseries_to_pair_timeseries(timeseries, index_benchmark=1, name_benchmark=None, prefix=None):
    df = timeseries.copy()
    if name_benchmark and prefix:
        name_benchmark = filter_prefix_of_timeseries_column_name(name_benchmark, prefix)
    benchmark_index = get_benchmark_index(df, index_benchmark, name_benchmark)
    create_df_with_benchmark = partial(create_two_column_df, df, benchmark_index)
    return list(map(create_df_with_benchmark, range(len(df.columns))))

split_prices_to_pair_timeseries = partial(split_timeseries_to_pair_timeseries, prefix=None)
split_returns_to_pair_timeseries = partial(split_timeseries_to_pair_timeseries, prefix='return: ')
split_cumreturns_to_pair_timeseries = partial(split_timeseries_to_pair_timeseries, prefix='cumreturn: ')