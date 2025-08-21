## import standard libraries
from datetime import datetime, timezone
from enum import IntEnum
from typing import Dict, List, Optional, Union
# import local files
from ogd.common.models.GameData import GameData
from ogd.common.utils.typing import Map

class EventSource(IntEnum):
    """Enum for the possible sources of an event - a game, or a generator.
    """
    GAME = 1
    GENERATED = 2

## @class Event
class Event(GameData):
    """
    Completely dumb struct that enforces a particular structure for the data we get from a source.
    Basically, whenever we fetch data, the TableConfig will be used to map columns to the required elements of an Event.
    Then the extractors etc. can just access columns in a direct manner.
    """
    def __init__(self, app_id:str,          user_id:Optional[str],          session_id:str,
                 app_version:Optional[str], app_branch:Optional[str],       log_version:Optional[str],     
                 timestamp:datetime,        time_offset:Optional[timezone], event_sequence_index:Optional[int],
                 event_name:str,            event_source:"EventSource",     event_data:Map,
                 game_state:Optional[Map],  user_data:Optional[Map]):
        """Constructor for an Event struct

        :param app_id: _description_
        :type app_id: str
        :param user_id: _description_
        :type user_id: Optional[str]
        :param session_id: _description_
        :type session_id: str
        :param app_version: _description_
        :type app_version: Optional[str]
        :param app_branch: _description_
        :type app_branch: Optional[str]
        :param log_version: _description_
        :type log_version: Optional[str]
        :param timestamp: _description_
        :type timestamp: datetime
        :param time_offset: _description_
        :type time_offset: Optional[timezone]
        :param event_sequence_index: _description_
        :type event_sequence_index: Optional[int]
        :param event_name: _description_
        :type event_name: str
        :param event_source: _description_
        :type event_source: EventSource
        :param event_data: _description_
        :type event_data: Map
        :param game_state: _description_
        :type game_state: Optional[Map]
        :param user_data: _description_
        :type user_data: Optional[Map]
        """
        # TODO: event source, e.g. from game or from detector
        super().__init__(app_id=app_id,           user_id=user_id,       session_id=session_id)
        self.app_version          : str           = app_version if app_version is not None else "0"
        self.app_branch           : str           = app_branch  if app_branch  is not None else "main"
        self.log_version          : str           = log_version if log_version is not None else "0"
        self.timestamp            : datetime      = timestamp
        self.time_offset          : Optional[timezone] = time_offset
        self.event_sequence_index : Optional[int] = event_sequence_index
        self.event_name           : str           = event_name
        self.event_source         : EventSource   = event_source
        self.event_data           : Map           = event_data
        self.game_state           : Map           = game_state if game_state is not None else {}
        self.user_data            : Map           = user_data if user_data is not None else {}
        self._hash                : Optional[int] = None

    def __str__(self):
        return f"app_id       : {self.app_id}\n"\
             + f"user_id      : {self.user_id}\n"\
             + f"session_id   : {self.session_id}\n"\
             + f"app_version  : {self.app_version}\n"\
             + f"app_branch   : {self.app_branch}\n"\
             + f"log_version  : {self.log_version}\n"\
             + f"timestamp    : {self.timestamp}\n"\
             + f"offset       : {self.TimeOffsetString}\n"\
             + f"index        : {self.event_sequence_index}\n"\
             + f"event_name   : {self.event_name}\n"\
             + f"event_source : {self.event_source.name}\n"\
             + f"event_data   : {self.event_data}\n"\
             + f"game_state   : {self.game_state}\n"\
             + f"user_data    : {self.user_data}\n"\

    def __hash__(self):
        _elems = [self.AppID, self.UserID, self.SessionID,
                  self.AppVersion, self.AppBranch, self.LogVersion,
                  self.Timestamp, self.TimeOffset, self.EventSequenceIndex,
                  self.EventName, self.EventSource, self.EventData,
                  self.GameState, self.UserData]
        _str_elems = [str(elem) for elem in _elems]
        return hash("".join(_str_elems))

    def FallbackDefaults(self, app_id:Optional[str]=None, index:Optional[int]=None):
        if self.app_id == None and app_id != None:
            self.app_id = app_id
        if self.event_sequence_index == None:
            self.event_sequence_index = index

    @staticmethod
    def FromJSON(json_data:Dict) -> "Event":
        """_summary_

        TODO : rename to FromDict, and make classmethod, to match conventions of schemas.

        :param json_data: _description_
        :type json_data: Dict
        :return: _description_
        :rtype: Event
        """
        return Event(
            session_id  =json_data.get("session_id", "SESSION ID NOT FOUND"),
            app_id      =json_data.get("app_id", "APP ID NOT FOUND"),
            timestamp   =json_data.get("client_time", "CLIENT TIME NOT FOUND"),
            event_name  =json_data.get("event_name", "EVENT NAME NOT FOUND"),
            event_data  =json_data.get("event_data", "EVENT DATA NOT FOUND"),
            event_source=EventSource.GAME,
            app_version =json_data.get("app_version", None),
            app_branch  =json_data.get("app_branch", None),
            log_version =json_data.get("log_version", None),
            time_offset =None,
            user_id     =json_data.get("user_id", None),
            user_data   =json_data.get("user_data", None),
            game_state  =json_data.get("game_state", None),
            event_sequence_index=json_data.get("event_sequence_index", json_data).get("session_n", None)
        )

    @staticmethod
    def ColumnNames() -> List[str]:
        """_summary_

        TODO: In Event schema 1.0, set order to match ordering of `__init__` function, which is meant to be better-organized.

        :return: _description_
        :rtype: List[str]
        """
        return ["session_id",  "app_id",       "timestamp",   "event_name",
                "event_data",  "event_source", "app_version", "app_branch",
                "log_version", "offset",        "user_id",    "user_data",
                "game_state",  "index"]

    @property
    def ColumnValues(self) -> List[Union[str, datetime, timezone, Map, int, None]]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, Map, int, None]]
        """
        return [self.session_id,  self.app_id,             self.timestamp,   self.event_name,
                self.event_data,  self.event_source.name,  self.app_version, self.app_branch,
                self.log_version, self.TimeOffsetString,   self.user_id,     self.user_data,
                self.game_state,  self.event_sequence_index]

    @property
    def Hash(self) -> int:
        if not self._hash:
            self._hash = hash(self)
        return self._hash

    @property
    def AppVersion(self) -> str:
        """The semantic versioning string for the game that generated this Event.

        Some legacy games may use a single integer or a string similar to AppID in this column.

        :return: The semantic versioning string for the game that generated this Event
        :rtype: str
        """
        return self.app_version

    @property
    def AppBranch(self) -> str:
        """The name of the branch of a game version that generated this Event.

        The branch name is typically used for cases where multiple experimental versions of a game are deployed in parallel;
        most events will simply have a branch of "main" or "master."

        :return: The name of the branch of a game version that generated this Event
        :rtype: str
        """
        return self.app_branch

    @property
    def LogVersion(self) -> str:
        """The version of the logging schema implemented in the game that generated the Event

        For most games, this is a single integer; however, semantic versioning is valid for this column as well.

        :return: The version of the logging schema implemented in the game that generated the Event
        :rtype: str
        """
        return self.log_version

    @property
    def Timestamp(self) -> datetime:
        """A UTC timestamp of the moment at which the game client sent the Event

        The timestamp is based on the GMT timezone, in keeping with UTC standards.
        Some legacy games may provide the time based on a local time zone, rather than GMT.

        :return: A UTC timestamp of the moment at which the game client sent the event
        :rtype: datetime
        """
        return self.timestamp

    @property
    def TimeOffset(self) -> Optional[timezone]:
        """A timedelta for the offset from GMT to the local time zone of the game client that sent the Event

        Some legacy games do not include an offset, and instead log the Timestamp based on the local time zone.

        :return: A timedelta for the offset from GMT to the local time zone of the game client that sent the Event
        :rtype: Optional[timedelta]
        """
        return self.time_offset

    @property
    def TimeOffsetString(self) -> Optional[str]:
        """A string representation of the offset from GMT to the local time zone of the game client that sent the Event

        Some legacy games do not include an offset, and instead log the Timestamp based on the local time zone.

        :return: A timedelta for the offset from GMT to the local time zone of the game client that sent the Event
        :rtype: Optional[timedelta]
        """
        return self.time_offset.tzname(None) if self.time_offset is not None else None

    @property
    def EventSequenceIndex(self) -> Optional[int]:
        """A strictly-increasing counter indicating the order of events in a session.

        The first event in a session has EventSequenceIndex == 0, the next has index == 1, etc.

        :return: A strictly-increasing counter indicating the order of events in a session
        :rtype: int
        """
        return self.event_sequence_index

    @property
    def EventName(self) -> str:
        """The name of the specific type of event that occurred

        For some legacy games, the names in this column have a format of CUSTOM.1, CUSTOM.2, etc.
        For these games, the actual human-readable event names for these events are stored in the EventData column.
        Please see individual game logging documentation for details.

        :return: The name of the specific type of event that occurred
        :rtype: str
        """
        return self.event_name

    @property
    def EventData(self) -> Map:
        """A dictionary containing data specific to Events of this type.

        For details, see the documentation in the given game's README.md, included with all datasets.
        Alternately, review the {GAME_NAME}.json file for the given game.

        :return: A dictionary containing data specific to Events of this type
        :rtype: Dict[str, Any]
        """
        return self.event_data

    @property
    def EventSource(self) -> EventSource:
        """An enum indicating whether the event was generated directly by the game, or calculated by a post-hoc detector.

        :return: An enum indicating whether the event was generated directly by the game, or calculated by a post-hoc detector
        :rtype: EventSource
        """
        return self.event_source

    @property
    def UserData(self) -> Map:
        """A dictionary containing any user-specific data tracked across gameplay sessions or individual games.

        :return: A dictionary containing any user-specific data tracked across gameplay sessions or individual games
        :rtype: Dict[str, Any]
        """
        return self.user_data

    @property
    def GameState(self) -> Map:
        """A dictionary containing any game-specific data that is defined across all event types in the given game.

        This column typically includes data that offers context to a given Event's data in the EventData column.
        For example, this column would typically include a level number or quest name for whatever level/quest the user was playing when the Event occurred.

        :return: A dictionary containing any game-specific data that is defined across all event types in the given game
        :rtype: Dict[str, Any]
        """
        return self.game_state
