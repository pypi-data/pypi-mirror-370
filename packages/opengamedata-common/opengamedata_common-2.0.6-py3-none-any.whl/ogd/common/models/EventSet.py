## import standard libraries
from typing import List
# import local files
from ogd.common.filters.collections import *
from ogd.common.models.Event import Event, EventSource
from ogd.common.utils.typing import ExportRow

class EventSet:
    """Dumb struct that primarily just contains an ordered list of events.
       It also contains information on any filters used to define the dataset, such as a date range or set of versions.
    """

    def __init__(self, events:List[Event], filters:DatasetFilterCollection) -> None:
        self._events = events
        self._filters = filters

    def __add__(self, events:Event | List[Event] | "EventSet") -> "EventSet":
        if isinstance(events, Event):
            return EventSet(events=self.Events + [events], filters=self.Filters)
        elif isinstance(events, list):
            return EventSet(events=self.Events + events, filters=self.Filters)
        # TODO : need to merge filters
        else:
            return EventSet(events=self.Events + events.Events, filters=self.Filters)

    def __iadd__(self, events:Event | List[Event] | "EventSet") -> "EventSet":
        if isinstance(events, Event):
            self.Events.append(events)
        elif isinstance(events, list):
            self.Events += events
        elif isinstance(events, EventSet):
            self.Events += events.Events
        return self

    def __len__(self):
        return len(self.Events)

    def __iter__(self):
        for event in self.Events:
            yield event

    @property
    def Events(self) -> List[Event]:
        return self._events
    @Events.setter
    def Events(self, events:List[Event]):
        self._events = events

    @property
    def GameEvents(self) -> List[Event]:
        return [event for event in self.Events if event.EventSource == EventSource.GAME]

    @property
    def EventLines(self) -> List[ExportRow]:
        return [event.ColumnValues for event in self.Events]
    @property
    def GameEventLines(self) -> List[ExportRow]:
        return [event.ColumnValues for event in self.GameEvents]

    @property
    def Filters(self) -> DatasetFilterCollection:
        return self._filters

    @property
    def EventsHeader(self) -> List[str]:
        return Event.ColumnNames()

    @property
    def AsMarkdown(self):
        _filters_clause = "* ".join([f"{key} : {val}" for key,val in self.Filters.AsDict.items()])
        return f"## Event Dataset\n\n{_filters_clause}"

    def ClearEvents(self):
        self._events = []
