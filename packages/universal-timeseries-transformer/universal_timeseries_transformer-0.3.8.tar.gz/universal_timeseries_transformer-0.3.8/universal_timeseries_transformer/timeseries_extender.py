from .timeseries_basis import get_all_dates_between_timeseries_period
from logging import getLogger
logger = getLogger(__name__)

def extend_timeseries_by_all_dates(timeseries, start_date=None, end_date=None, option_verbose=False):
    df = timeseries.copy()
    if option_verbose:
        logger.info(f'(original) {df.index[0]} ~ {df.index[-1]}, {len(df)} days')
    all_dates = get_all_dates_between_timeseries_period(df, start_date, end_date)
    df_extended = df.reindex(all_dates).ffill()
    if option_verbose:
        logger.info(f'(extended) {df_extended.index[0]} ~ {df_extended.index[-1]}, {len(df_extended)} days')
    return df_extended
