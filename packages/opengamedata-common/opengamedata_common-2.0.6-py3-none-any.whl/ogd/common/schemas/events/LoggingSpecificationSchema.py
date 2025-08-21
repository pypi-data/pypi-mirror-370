# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.events.EventSchema import EventSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class LoggingSpecificationSchema
class LoggingSpecificationSchema(Schema):
    """Class for loading a game's logging specification file.

    These contain information on the structure of the `game_state` and `user_data` elements logged with every event from the game,
    as well as descriptions of each type of event the game logs.
    Further, there is information on any de facto enums that are defined for portions of the log data
    (i.e. sets of valid string values for a particular key in `game_state`, `user_data`, or `event_data`)
    And finally, it specifies which logging version of the game is so documented, as well as the folder where the particular game's schema folder resides.
    """
    _DEFAULT_ENUMS       : Final[Dict[str, List[str]]] = {}
    _DEFAULT_GAME_STATE  : Final[Map]                  = {}
    _DEFAULT_USER_DATA   : Final[Map]                  = {}
    _DEFAULT_EVENT_LIST  : Final[List[EventSchema]]    = []
    _DEFAULT_LOG_VERSION : Final[int]                  = 0
    _DEFAULT_GAME_FOLDER : Final[Path]                 = Path("./") / "ogd" / "games"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:str, enum_defs:Optional[Dict[str, List[str]]],
                 game_state:Optional[Map], user_data:Optional[Map], event_list:Optional[List[EventSchema]],
                 logging_version:Optional[int], other_elements:Optional[Map]=None):
        """Constructor for the `LoggingSpecificationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "enumas": {
                "EnumOne": [ "VALUE1", "VALUE2", "VALUE3", ... ],
                ...
            }
            "game_state": {
                "game_state_element_name": {
                    "type": "float",
                    "description": "Description of the data element of the game_state column."
                },
                ...
            },
            "user_data": {
                "user_data_element_name": {
                    "type": "float",
                    "description": "Description of the data element of the user_data column."
                },
                ...
            },
            "events": {
                "event_name" : {
                    "description": "Description of what the event is and when it occurs.",
                    "event_data": {
                        "data_element_name": {
                        "type": "bool",
                        "description": "Description of what the data element means or represents."
                        },
                        ...
                    }
                }
            },
            "logging_version" : 1
        },
        ```

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: str
        :param enum_defs: _description_
        :type enum_defs: Dict[str, List[str]]
        :param game_state: _description_
        :type game_state: Map
        :param user_data: _description_
        :type user_data: Map
        :param event_list: _description_
        :type event_list: List[EventSchema]
        :param log_version: _description_
        :type log_version: int
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

    # 1. define instance vars
        self._game_id     : str                  = game_id
        self._enum_defs   : Dict[str, List[str]] = enum_defs       or self._parseEnumDefs(unparsed_elements=unparsed_elements)
        self._game_state  : Map                  = game_state      or self._parseGameState(unparsed_elements=unparsed_elements)
        self._user_data   : Map                  = user_data       or self._parseUserData(unparsed_elements=unparsed_elements)
        self._event_list  : List[EventSchema]    = event_list      or self._parseEventList(unparsed_elements=unparsed_elements)
        self._log_version : int                  = logging_version or self._parseLogVersion(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    # def __getitem__(self, key) -> Any:
    #     return _schema[key] if _schema is not None else None

    @property
    def GameName(self) -> str:
        """Property for the name of the game configured by this schema
        """
        return self._game_id

    @property
    def EnumDefs(self) -> Dict[str, List[str]]:
        """Property for the dict of all enums defined for sub-elements in the given game's schema.
        """
        return self._enum_defs

    @property
    def GameState(self) -> Dict[str, Any]:
        """Property for the dictionary describing the structure of the GameState column for the given game.
        """
        return self._game_state

    @property
    def UserData(self) -> Dict[str, Any]:
        """Property for the dictionary describing the structure of the UserData column for the given game.
        """
        return self._user_data

    @property
    def Events(self) -> List[EventSchema]:
        """Property for the list of events the game logs.
        """
        return self._event_list

    @property
    def EventNames(self) -> List[str]:
        """Property for the names of all event types for the game.
        """
        return [event.Name for event in self.Events]
    @property
    def EventTypes(self) -> List[str]:
        """Alias for the EventNames Property
        """
        return self.EventNames

    @property
    def LoggingVersion(self) -> int:
        return self._log_version

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        event_summary = ["## Logged Events",
                         "The individual fields encoded in the *game_state* and *user_data* Event element for all event types, and the fields in the *event_data* Event element for each individual event type logged by the game."
                        ]
        enum_list     = ["### Enums",
                         "\n".join(
                             ["| **Name** | **Values** |",
                             "| ---      | ---        |"]
                         + [f"| {name} | {val_list} |" for name,val_list in self.EnumDefs.items()]
                        )]
        game_state_list = ["### Game State",
                           "\n".join(
                               ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                               "| ---      | ---      | ---             | ---         |"]
                           + [elem.AsMarkdownRow for elem in self.GameState.values()]
                          )]
        user_data_list = ["### User Data",
                          "\n".join(
                              ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                              "| ---      | ---      | ---             | ---         |"]
                          + [elem.AsMarkdownRow for elem in self.UserData.values()]
                         )]
        # Set up list of events
        event_list = [event.AsMarkdownTable for event in self.Events] if len(self.Events) > 0 else ["None"]
        # Include other elements
        other_summary = ["## Other Elements",
                         "Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors."
                         ]
        other_element_list = [ f"{key} : {self._other_elements[key]}" for key in self._other_elements.keys()]

        ret_val = "  \n\n".join(event_summary
                              + enum_list + game_state_list + user_data_list + event_list
                              + other_summary + other_element_list)

        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "LoggingSpecificationSchema":
        """_summary_

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :raises ValueError: _description_
        :raises ValueError: _description_
        :return: _description_
        :rtype: LoggingSpecificationSchema
        """
        _game_id     : str                  = name
        return LoggingSpecificationSchema(name=name, game_id=_game_id, enum_defs=None,
                          game_state=None, user_data=None,
                          event_list=None, logging_version=None,
                          other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "LoggingSpecificationSchema":
        return LoggingSpecificationSchema(
            name="DefaultLoggingSpecificationSchema",
            game_id="DEFAULT_GAME",
            enum_defs=cls._DEFAULT_ENUMS,
            game_state=cls._DEFAULT_GAME_STATE,
            user_data=cls._DEFAULT_USER_DATA,
            event_list=cls._DEFAULT_EVENT_LIST,
            logging_version=cls._DEFAULT_LOG_VERSION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:Optional[Path] = None, search_templates:bool=True) -> "LoggingSpecificationSchema":
        """Function to get a LoggingSpecificationSchema from a file

        :param game_id: _description_
        :type game_id: str
        :param schema_path: _description_, defaults to None
        :type schema_path: Optional[Path], optional
        :param search_templates: _description_, defaults to True
        :type search_templates: bool, optional
        :raises ValueError: _description_
        :return: _description_
        :rtype: LoggingSpecificationSchema
        """
        ret_val : Schema

        game_id = schema_name.split(".")[0]
        # Give schema_path a default, don't think we can use game_id to construct it directly in the function header (so do it here if None)
        schema_path = schema_path or cls._DEFAULT_GAME_FOLDER / game_id / "schemas"
        ret_val = cls._fromFile(schema_name=game_id, schema_path=schema_path, search_templates=search_templates)
        if isinstance(ret_val, LoggingSpecificationSchema):
            return ret_val
        else:
            raise ValueError("The result of the class _fromFile function was not a LoggingSpecificationSchema!")

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseEnumDefs(unparsed_elements:Map) -> Dict[str, List[str]]:
        """_summary_

        TODO : Fully parse this, rather than just getting dictionary.

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Dict[str, List[str]]
        """
        ret_val : Dict[str, List[str]]

        enums_list = LoggingSpecificationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["enums"],
            to_type=dict,
            default_value=LoggingSpecificationSchema._DEFAULT_ENUMS,
            remove_target=True
        )
        if isinstance(enums_list, dict):
            ret_val = enums_list
        else:
            ret_val = LoggingSpecificationSchema._DEFAULT_ENUMS
            Logger.Log(f"enums_list was unexpected type {type(enums_list)}, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameState(unparsed_elements:Map) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]

        game_state = LoggingSpecificationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_state"],
            to_type=dict,
            default_value=LoggingSpecificationSchema._DEFAULT_GAME_STATE,
            remove_target=True
        )
        ret_val = {
            name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
            for name,elems in game_state.items()
        }

        return ret_val

    @staticmethod
    def _parseUserData(unparsed_elements:Map) -> Dict[str, DataElementSchema]:
        ret_val : Dict[str, DataElementSchema]

        user_data = LoggingSpecificationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["user_data"],
            to_type=dict,
            default_value=LoggingSpecificationSchema._DEFAULT_USER_DATA,
            remove_target=True
        )
        ret_val = {
            name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
            for name,elems in user_data.items()
        }

        return ret_val

    @staticmethod
    def _parseEventList(unparsed_elements:Map) -> List[EventSchema]:
        ret_val : List[EventSchema]

        events_list = LoggingSpecificationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["events"],
            to_type=dict,
            default_value=LoggingSpecificationSchema._DEFAULT_EVENT_LIST,
            remove_target=True
        )
        ret_val = [
            EventSchema.FromDict(name=key, unparsed_elements=val) for key,val in events_list.items()
        ]

        return ret_val

    @staticmethod
    def _parseLogVersion(unparsed_elements:Map) -> int:
        return LoggingSpecificationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["logging_version", "log_version"],
            to_type=int,
            default_value=LoggingSpecificationSchema._DEFAULT_LOG_VERSION,
            remove_target=True
        )


    # *** PRIVATE METHODS ***
