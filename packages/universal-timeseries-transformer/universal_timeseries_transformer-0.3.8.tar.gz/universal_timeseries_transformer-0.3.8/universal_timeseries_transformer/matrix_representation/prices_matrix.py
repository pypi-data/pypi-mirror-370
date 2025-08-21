from string_date_controller import (
    get_all_data_historical_date_pairs,
    get_all_data_monthly_date_pairs,
    get_all_data_yearly_date_pairs,
)
from .timeseries_matrix import TimeseriesMatrix

class PricesMatrix(TimeseriesMatrix):
    def __init__(self, prices, date_ref=None):
        super().__init__(df=prices)
        self.date_ref = self.set_date_ref(date_ref)
        self._historical_date_pairs = None
        self._monthly_date_pairs = None
        self._yearly_date_pairs = None
        self._date_inception = None
        self._date_end = None

    def set_date_ref(self, date_ref):
        return date_ref if date_ref is not None else self.date_f

    @property
    def historical_date_pairs(self):
        if self._historical_date_pairs is None:
            self._historical_date_pairs = get_all_data_historical_date_pairs(dates=self.dates, date_ref=self.date_ref)
        return self._historical_date_pairs

    @property
    def monthly_date_pairs(self):
        if self._monthly_date_pairs is None:
            self._monthly_date_pairs = get_all_data_monthly_date_pairs(dates=self.dates)
        return self._monthly_date_pairs
    
    @property
    def yearly_date_pairs(self):
        if self._yearly_date_pairs is None:
            self._yearly_date_pairs = get_all_data_yearly_date_pairs(dates=self.dates)
        return self._yearly_date_pairs

    @property
    def date_inception(self):
        if self._date_inception is None:
            self._date_inception = self.date_i
        return self._date_inception

    @property
    def date_end(self):
        if self._date_end is None:
            self._date_end = self.date_f
        return self._date_end
