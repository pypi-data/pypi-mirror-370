## import standard libraries
from typing import Optional
# import local files
from ogd.common.filters.collections.EventFilterCollection import EventFilterCollection
from ogd.common.filters.collections.IDFilterCollection import IDFilterCollection
from ogd.common.filters.collections.SequencingFilterCollection import SequencingFilterCollection
from ogd.common.filters.collections.VersioningFilterCollection import VersioningFilterCollection

class DatasetFilterCollection:
    def __init__(self,
                 id_filters:Optional[IDFilterCollection]=None,
                 sequence_filters:Optional[SequencingFilterCollection]=None,
                 version_filters:Optional[VersioningFilterCollection]=None,
                 event_filters:Optional[EventFilterCollection]=None):
        self._id_filters       : IDFilterCollection         = id_filters       or IDFilterCollection()
        self._sequence_filters : SequencingFilterCollection = sequence_filters or SequencingFilterCollection()
        self._version_filters  : VersioningFilterCollection = version_filters  or VersioningFilterCollection()
        self._event_filters    : EventFilterCollection      = event_filters    or EventFilterCollection()

    @property
    def IDFilters(self):
        return self._id_filters
    
    @property
    def Sequences(self):
        return self._sequence_filters
    
    @property
    def Versions(self):
        return self._version_filters
    
    @property
    def Events(self):
        return self._event_filters

    @property
    def any(self) -> bool:
        """Property to check whether any filter in the collection is active

        :return: _description_
        :rtype: bool
        """
        return self.IDFilters.any or self.Sequences.any or self.Versions.any or self.Events.any

    @property
    def AsDict(self):
        return {
            "session_id" : self.IDFilters.Sessions,
            "player_id" : self.IDFilters.Players
        }
