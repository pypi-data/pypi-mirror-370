import abc
from typing import Generic, List, Optional, Set, TypeVar

from ogd.common.models.enums.FilterMode import FilterMode

T = TypeVar("T")
class Filter(Generic[T]):
    @property
    @abc.abstractmethod
    def AsSet(self) -> Optional[Set[T]]:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the AsSet function!")

    @property
    @abc.abstractmethod
    def Min(self) -> Optional[T]:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Min function!")

    @property
    @abc.abstractmethod
    def Max(self) -> Optional[T]:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Max function!")

    def __init__(self, mode:FilterMode=FilterMode.NOFILTER):
        """Constructor for base Filter class.
        By default, creates a filter equivalent to "NoFilter" class, meaning this filter will not remove any data.

        :param mode: the mode by which to apply the filter, either excluding or including all values that match the filter; defaults to FilterMode.NOFILTER
        :type mode: FilterMode, optional
        """
        self._mode = mode

    @property
    def Active(self) -> bool:
        return self.FilterMode != FilterMode.NOFILTER
    
    @property
    def FilterMode(self) -> FilterMode:
        return self._mode

    @property
    def AsList(self) -> Optional[List[T]]:
        return list(self.AsSet) if self.AsSet is not None else None
