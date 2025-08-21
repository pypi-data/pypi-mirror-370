
def slice_timeseries_by_dates(timeseries, start_date=None, end_date=None):
    df = timeseries.copy()
    if start_date:
        existing_start_date = df.loc[:start_date].index[-1]
        if end_date:
            df = df.loc[existing_start_date:end_date]
        else:
            df = df.loc[start_date:]
    elif end_date:
        df = df.loc[:end_date]
    return df

def slice_timeseries_around_index(timeseries, index_ref, index_start=None, index_end=None):
    ref_position = timeseries.index.get_loc(index_ref)
    start_pos = 0 if index_start is None else max(0, ref_position + index_start)
    end_pos = len(timeseries) if index_end is None else min(len(timeseries), ref_position + index_end + 1)
    return timeseries.iloc[start_pos:end_pos]