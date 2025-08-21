## import standard libraries
import logging
from typing import Any, Optional, TypeVar
# import local files
from ogd.common.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.Logger import Logger

T = TypeVar("T", bound=Any)
class RangeFilter(Filter[T]):
    def __init__(self, mode:FilterMode=FilterMode.NOFILTER, minimum:Optional[T]=None, maximum:Optional[T]=None):
        super().__init__(mode=mode)
        if minimum and maximum and minimum > maximum:
            Logger.Log(f"When creating MinMaxFilter, got a minimum ({minimum}) larger than maximum ({maximum})!", level=logging.WARNING)
        self._min = minimum
        self._max = maximum

    def __str__(self) -> str:
        ret_val : str

        match self.FilterMode:
            case FilterMode.EXCLUDE:
                if self.Min and self.Max:
                    ret_val = f"outside {self.Min} to {self.Max}"
                elif self.Max:
                    ret_val = f"not under {self.Max}"
                else: # self.Min is not None
                    ret_val = f"not above {self.Min}"
            case FilterMode.INCLUDE:
                if self.Min and self.Max:
                    ret_val = f"from {self.Min} to {self.Max}"
                elif self.Max:
                    ret_val = f"under {self.Max}"
                else: # self.Min is not None
                    ret_val = f"above {self.Min}"
            case FilterMode.NOFILTER:
                ret_val = "unfiltered"

        return ret_val
    
    def __repr__(self) -> str:
        return f"<class {type(self).__name__} {self.FilterMode}:{self.Min}-{self.Max}>"

    @property
    def AsSet(self) -> None:
        return None

    @property
    def Min(self) -> Optional[T]:
        return self._min if self.FilterMode != FilterMode.NOFILTER else None

    @property
    def Max(self) -> Optional[T]:
        return self._max if self.FilterMode != FilterMode.NOFILTER else None

    @property
    def Range(self) -> Optional[slice]:
        return slice(self.Min, self.Max) if self.FilterMode != FilterMode.NOFILTER else None

    @staticmethod
    def FromSlice(mode:FilterMode, range_slice:slice) -> "RangeFilter":
        """Create a RangeFilter based on a slice object.

        This is sort of an abuse of the type, but it's a convenient way to represent a min and max where one or the other is optional.

        :param mode: _description_
        :type mode: FilterMode
        :param slice: _description_
        :type slice: slice
        :return: _description_
        :rtype: RangeFilter
        """
        return RangeFilter(mode=mode, minimum=range_slice.start, maximum=range_slice.stop)
