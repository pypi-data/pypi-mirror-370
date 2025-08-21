## import standard libraries
from typing import List, Optional, Set, Tuple
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair

class EventFilterCollection:
    """Dumb struct to hold filters for versioning information
    """

    def __init__(self,
                 event_name_filter : Optional[SetFilter[str] | NoFilter]                    = None,
                 event_code_filter : Optional[SetFilter[int] | RangeFilter[int] | NoFilter] = None):
        """Constructor for the EventFilterCollection structure.

        Accepts a collection of filters to be applied on event names/codes included in the data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param event_name_filter: The filter to apply to event names, defaults to NoFilter()
        :type event_name_filter: Filter, optional
        :param event_code_filter: The filter to apply to event codes, defaults to NoFilter()
        :type event_code_filter: Filter, optional
        """
        self._event_names : SetFilter[str] | NoFilter                    = event_name_filter or NoFilter()
        self._event_codes : SetFilter[int] | RangeFilter[int] | NoFilter = event_code_filter or NoFilter()

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.EventNames or self.EventCodes:
            _name_str = f"event name(s) {self.EventCodes}" if self.EventNames else None
            _code_str = f"event code(s) {self.EventCodes}" if self.EventCodes else None
            _ver_strs = ", ".join([elem for elem in [_name_str, _code_str] if elem is not None])
            ret_val = f"versioning filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.EventNames is not None or self.EventCodes is not None:
            _name_str = repr(self.EventNames) if self.EventNames else None
            _code_str = repr(self.EventCodes) if self.EventCodes else None
            _ver_strs = " ^ ".join([elem for elem in [_name_str, _code_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def EventNames(self) -> Filter[str]:
        """Property containing the filter for event names.

        :return: _description_
        :rtype: Optional[SetFilter]
        """
        return self._event_names
    @EventNames.setter
    def EventNames(self, allowed_events:Optional[SetFilter[str] | NoFilter | List[str] | Set[str] | Tuple[str] | str]):
        """Can be conveniently set from an existing filter, or collection of event names.

        If set this way, the filter is assumed to be an "inclusion" filter.

        :param allowed_events: _description_, defaults to None
        :type allowed_events: Optional[List[str]  |  Set[str]], optional
        :return: _description_
        :rtype: Filter
        """
        if allowed_events is None or isinstance(allowed_events, NoFilter):
            self._event_names = NoFilter()
        elif isinstance(allowed_events, SetFilter):
            self._event_names = allowed_events
        else:
            self._event_names = SetFilter(mode=self.EventNames.FilterMode, set_elements=allowed_events)

    @property
    def EventCodes(self) -> Filter[int]:
        return self._event_codes
    @EventCodes.setter
    def EventCodes(self, allowed_events:Optional[SetFilter[int] | RangeFilter[int] | NoFilter | List[int] | Set[int] | slice | Pair[int, int]]):
        if allowed_events is None or isinstance(allowed_events, NoFilter):
            self._event_codes = NoFilter()
        elif isinstance(allowed_events, Filter):
            self._event_codes = allowed_events
        elif isinstance(allowed_events, list) or isinstance(allowed_events, set):
            self._event_codes = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_events))
        elif isinstance(allowed_events, slice):
            self._event_codes = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, range_slice=allowed_events)
        elif isinstance(allowed_events, tuple):
            self._event_codes = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_events[0], maximum=allowed_events[1])

    @property
    def any(self) -> bool:
        return self.EventNames.Active or self.EventCodes.Active

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
