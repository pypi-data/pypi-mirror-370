"""EventTableSchema Module"""
# import standard libraries
from typing import Dict, List, Optional, Self

# import local files
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema, ColumnMapElement
from ogd.common.utils.typing import Map

## @class TableSchema
class EventMapSchema(ColumnMapSchema):
    """Dumb struct to hold useful info about the structure of database data for a particular game.

    This includes the indices of several important database columns, the names
    of the database columns, the max and min levels in the game, and a list of
    IDs for the game sessions in the given requested date range.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name,
                 app_id:Optional[str | List[str]],       user_id:Optional[str | List[str]],      session_id:Optional[str | List[str]],
                 app_version:Optional[ColumnMapElement], app_branch:Optional[ColumnMapElement],  log_version:Optional[ColumnMapElement],
                 timestamp:Optional[ColumnMapElement],   time_offset:Optional[ColumnMapElement], event_sequence_index:Optional[ColumnMapElement],
                 event_name:Optional[ColumnMapElement],  event_source:Optional[ColumnMapElement],event_data:Optional[ColumnMapElement],
                 game_state:Optional[ColumnMapElement],  user_data:Optional[ColumnMapElement],
                 other_elements:Optional[Map]=None):
        """Constructor for the TableSchema class.
        
        If optional params are not given, data is searched for in `other_elements`.

        The structure is assumed to be as follows:

        ```python
        {
            "session_id"           : "session_id",
            "app_id"               : null,
            "timestamp"            : "client_time",
            "event_name"           : "event_name",
            "event_data"           : "event_data",
            "event_source"         : "event_source",
            "app_version"          : "app_version",
            "app_branch"           : "app_branch",
            "log_version"          : "log_version",
            "time_offset"          : "client_offset",
            "user_id"              : "user_id",
            "user_data"            : "user_data",
            "game_state"           : "game_state",
            "event_sequence_index" : "event_sequence_index"
        }
        ```

        :param name: _description_
        :type name: _type_
        :param app_id: _description_
        :type app_id: Optional[ColumnMapElement]
        :param user_id: _description_
        :type user_id: Optional[ColumnMapElement]
        :param session_id: _description_
        :type session_id: Optional[ColumnMapElement]
        :param app_version: _description_
        :type app_version: Optional[ColumnMapElement]
        :param app_branch: _description_
        :type app_branch: Optional[ColumnMapElement]
        :param log_version: _description_
        :type log_version: Optional[ColumnMapElement]
        :param timestamp: _description_
        :type timestamp: Optional[ColumnMapElement]
        :param time_offset: _description_
        :type time_offset: Optional[ColumnMapElement]
        :param event_sequence_index: _description_
        :type event_sequence_index: Optional[ColumnMapElement]
        :param event_name: _description_
        :type event_name: Optional[ColumnMapElement]
        :param event_source: _description_
        :type event_source: Optional[ColumnMapElement]
        :param event_data: _description_
        :type event_data: Optional[ColumnMapElement]
        :param game_state: _description_
        :type game_state: Optional[ColumnMapElement]
        :param user_data: _description_
        :type user_data: Optional[ColumnMapElement]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        super().__init__(name=name, app_id=app_id, user_id=user_id, session_id=session_id,
                         other_elements=unparsed_elements)
        self._app_version          : ColumnMapElement = app_version          or self._parseAppVersion(unparsed_elements=self._raw_map)
        self._app_branch           : ColumnMapElement = app_branch           or self._parseAppBranch(unparsed_elements=self._raw_map)
        self._log_version          : ColumnMapElement = log_version          or self._parseLogVersion(unparsed_elements=self._raw_map)
        self._timestamp            : ColumnMapElement = timestamp            or self._parseTimestamp(unparsed_elements=unparsed_elements)
        self._time_offset          : ColumnMapElement = time_offset          or self._parseTimeoffset(unparsed_elements=unparsed_elements)
        self._event_sequence_index : ColumnMapElement = event_sequence_index or self._parseSequenceIndex(unparsed_elements=unparsed_elements)
        self._event_name           : ColumnMapElement = event_name           or self._parseEventName(unparsed_elements=unparsed_elements)
        self._event_source         : ColumnMapElement = event_source         or self._parseEventSource(unparsed_elements=unparsed_elements)
        self._event_data           : ColumnMapElement = event_data           or self._parseEventData(unparsed_elements=unparsed_elements)
        self._game_state           : ColumnMapElement = game_state           or self._parseGameState(unparsed_elements=unparsed_elements)
        self._user_data            : ColumnMapElement = user_data            or self._parseUserData(unparsed_elements=unparsed_elements)

    def __eq__(self, other:"EventMapSchema"):
        if not isinstance(other, EventMapSchema):
            return False
        else:
            return self.AppIDColumn == other.AppIDColumn \
               and self.UserIDColumn == other.UserIDColumn \
               and self.SessionIDColumn == other.SessionIDColumn \
               and self.AppVersionColumn == other.AppVersionColumn \
               and self.AppBranchColumn == other.AppBranchColumn \
               and self.LogVersionColumn == other.LogVersionColumn \
               and self.TimestampColumn == other.TimestampColumn \
               and self.TimeOffsetColumn == other.TimeOffsetColumn \
               and self.EventSequenceIndexColumn == other.EventSequenceIndexColumn \
               and self.EventNameColumn == other.EventNameColumn \
               and self.EventSourceColumn == other.EventSourceColumn \
               and self.EventDataColumn == other.EventDataColumn \
               and self.GameStateColumn == other.GameStateColumn \
               and self.UserDataColumn == other.UserDataColumn

    @property
    def AppVersionColumn(self) -> ColumnMapElement:
        return self._app_version

    @property
    def AppBranchColumn(self) -> ColumnMapElement:
        return self._app_branch

    @property
    def LogVersionColumn(self) -> ColumnMapElement:
        return self._log_version

    @property
    def TimestampColumn(self) -> ColumnMapElement:
        return self._timestamp

    @property
    def EventNameColumn(self) -> ColumnMapElement:
        return self._event_name

    @property
    def EventDataColumn(self) -> ColumnMapElement:
        return self._event_data

    @property
    def EventSourceColumn(self) -> ColumnMapElement:
        return self._event_source

    @property
    def TimeOffsetColumn(self) -> ColumnMapElement:
        return self._time_offset

    @property
    def UserDataColumn(self) -> ColumnMapElement:
        return self._user_data

    @property
    def GameStateColumn(self) -> ColumnMapElement:
        return self._game_state

    @property
    def EventSequenceIndexColumn(self) -> ColumnMapElement:
        return self._event_sequence_index

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def Default(cls) -> "EventMapSchema":
        return EventMapSchema(
            name="DefaultEventTableSchema",
            app_id="app_id",
            user_id="user_id",
            session_id="session_id",
            app_version="app_version",
            app_branch="app_branch",
            log_version="log_version",
            timestamp="timestamp",
            time_offset="time_offset",
            event_sequence_index="event_sequence_index",
            event_name="event_name",
            event_source="event_source",
            event_data="event_data",
            game_state="game_state",
            user_data="user_data",
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "EventMapSchema":
        """Function to generate an EventMapSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "session_id"           : "session_id",
            "app_id"               : null,
            "timestamp"            : "client_time",
            "event_name"           : "event_name",
            "event_data"           : "event_data",
            "event_source"         : "event_source",
            "app_version"          : "app_version",
            "app_branch"           : "app_branch",
            "log_version"          : "log_version",
            "time_offset"          : "client_offset",
            "user_id"              : "user_id",
            "user_data"            : "user_data",
            "game_state"           : "game_state",
            "event_sequence_index" : "event_sequence_index"
        }
        ```

        The specific handling of the column map will be determined by the specific TableSchema subclass on which the FromDict feature is called.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :param key_overrides: _description_, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :param default_override: _description_, defaults to None
        :type default_override: Optional[Self], optional
        :return: _description_
        :rtype: EventMapSchema
        """
        return EventMapSchema(name=name,
                              app_id=None, user_id=None, session_id=None,
                              app_version=None, app_branch=None, log_version=None,
                              timestamp=None, time_offset=None, event_sequence_index=None,
                              event_name=None, event_source=None, event_data=None,
                              game_state=None, user_data=None,
                              other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseAppVersion(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["app_version"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseAppBranch(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["app_branch", "app_flavor"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseLogVersion(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["log_version"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseTimestamp(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["timestamp"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseTimeoffset(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["offset", "time_offset", "timezone", "time_zone"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseSequenceIndex(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_sequence_index", "event_index", "sequence_index"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseEventName(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_name", "event_type"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseEventSource(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_source", "source"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseEventData(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_data"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseGameState(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseUserData(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["user_data", "player_data"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )
