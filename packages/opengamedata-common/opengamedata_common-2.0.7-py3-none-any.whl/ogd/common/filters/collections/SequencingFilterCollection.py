## import standard libraries
from datetime import date, datetime, time
from typing import Optional
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair

class SequencingFilterCollection:
    """Dumb struct to hold filters for timing information

    For now, it just does timestamps and session index, if need be we may come back and allow filtering by timezone offset
    """
    def __init__(self,
                 timestamp_filter     : Optional[RangeFilter[datetime] | NoFilter | Pair[datetime, datetime] | Pair[date, date]] = None,
                 session_index_filter : Optional[SetFilter[int] | RangeFilter[int] | NoFilter] = None):
        """Constructor for the TimingFilterCollection structure.

        Accepts a collection of filters to be applied on timing of data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param log_ver_filter: The filter to apply to log version, defaults to NoFilter()
        :type log_ver_filter: Filter, optional
        :param app_ver_filter: The filter to apply to app version, defaults to NoFilter()
        :type app_ver_filter: Filter, optional
        :param branch_filter: The filter to apply to app branch, defaults to NoFilter()
        :type branch_filter: Filter, optional
        """
        self._timestamp_filter     : RangeFilter[datetime] | NoFilter      = SequencingFilterCollection._toTimestampFilter(timestamps=timestamp_filter)
        self._session_index_filter : SetFilter[int] | RangeFilter[int] | NoFilter = session_index_filter or NoFilter()

    def __str__(self) -> str:
        ret_val = "no timestamp filters"
        if self.Timestamps or self.SessionIndices:
            _times_str = f"time(s) {self.Timestamps}" if self.Timestamps else None
            _idxes_str = f"event index(s) {self.SessionIndices}" if self.SessionIndices else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"timestamp filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.Timestamps or self.SessionIndices:
            _times_str = f"time(s) {self.Timestamps}" if self.Timestamps else None
            _idxes_str = f"event index(s) {self.SessionIndices}" if self.SessionIndices else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def Timestamps(self) -> Filter[datetime]:
        return self._timestamp_filter
    @Timestamps.setter
    def Timestamps(self, allowed_times:Optional[RangeFilter[datetime] | NoFilter | slice | Pair[datetime | date, datetime | date]]) -> None:
        self._timestamp_filter = SequencingFilterCollection._toTimestampFilter(timestamps=allowed_times)

    @property
    def SessionIndices(self) -> Filter[int]:
        return self._session_index_filter
    @SessionIndices.setter
    def SessionIndices(self, allowed_indices:Optional[SetFilter[int] | RangeFilter[int] | NoFilter | slice | Pair[int, int]]) -> None:
        if allowed_indices is None or isinstance(allowed_indices, NoFilter):
            self._session_index_filter = NoFilter()
        elif isinstance(allowed_indices, Filter):
            self._session_index_filter = allowed_indices
        elif isinstance(allowed_indices, slice):
            self._session_index_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, range_slice=allowed_indices)
        elif isinstance(allowed_indices, tuple):
            self._session_index_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_indices[0], maximum=allowed_indices[1])

    @property
    def any(self) -> bool:
        return self.Timestamps.Active or self.SessionIndices.Active

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toTimestampFilter(timestamps:Optional[RangeFilter[datetime] | NoFilter | slice | Pair[datetime | date, datetime | date]]) -> RangeFilter[datetime] | NoFilter:
        ret_val : RangeFilter[datetime] | NoFilter

        if timestamps is None or isinstance(timestamps, NoFilter):
            ret_val = NoFilter()
        elif isinstance(timestamps, RangeFilter):
            ret_val = timestamps
        elif isinstance(timestamps, slice):
            # TODO : deal with types of the actual start and stop here
            ret_val = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, range_slice=timestamps)
        elif isinstance(timestamps, tuple):
            dt_from : date | datetime = timestamps[0]
            dt_to   : date | datetime = timestamps[1]
            if isinstance(dt_from, date):
                dt_from = datetime.combine(dt_from, time(0))
            if isinstance(dt_to, date):
                dt_to = datetime.combine(dt_to, time(0))
            ret_val = RangeFilter(mode=FilterMode.INCLUDE, minimum=dt_from, maximum=dt_to)

        return ret_val

    # *** PRIVATE METHODS ***
