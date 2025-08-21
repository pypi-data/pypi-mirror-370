from string_date_controller import get_all_dates_between_dates
from logging import getLogger

logger = getLogger(__name__)

def get_date_pair_of_timeseries(timeseries, start_date=None, end_date=None):
    initial_date, final_date = timeseries.index[0], timeseries.index[-1] 
    if start_date:
        initial_date = start_date if initial_date < start_date else initial_date
    if end_date:
        final_date = end_date if final_date > end_date else final_date
    return initial_date, final_date

def get_all_dates_between_timeseries_period(timeseries, start_date=None, end_date=None):
    initial_date, final_date = get_date_pair_of_timeseries(timeseries, start_date, end_date)
    all_dates = get_all_dates_between_dates(initial_date, final_date)
    return all_dates
