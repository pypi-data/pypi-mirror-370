## import standard libraries
from typing import Any
# import local files
from ogd.common.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

class NoFilter(Filter[Any]):
    def __init__(self):
        super().__init__(mode=FilterMode.NOFILTER)

    def __str__(self) -> str:
        ret_val : str

        ret_val = "unfiltered"

        return ret_val
    
    def __repr__(self) -> str:
        return f"<class {type(self).__name__} {self.FilterMode}:unfiltered data>"

    @property
    def AsSet(self) -> None:
        return None

    @property
    def Min(self) -> None:
        return None

    @property
    def Max(self) -> None:
        return None
