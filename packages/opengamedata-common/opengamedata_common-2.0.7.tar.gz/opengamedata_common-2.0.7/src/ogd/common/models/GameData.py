## import standard libraries
import abc
import logging
from datetime import datetime, timezone
from typing import List, Optional, Union
# import local files
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class GameData
class GameData(abc.ABC):
    """
    Completely dumb struct that enforces a particular structure for the data we get from a source.
    This acts as a common starting point for the `Event` and `Feature` classes, defining the common elements between the two.

    TODO : Consider whether to inherit from Schema. Would at least be good to have FromDict as a required function
    """

    @staticmethod
    @abc.abstractmethod
    def ColumnNames() -> List[str]:
        raise NotImplementedError("GameData has not implemented the ColumnNames function!")

    @abc.abstractmethod
    def ColumnValues(self) -> List[Union[str, datetime, timezone, Map, int, None]]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.
        .. todo:: Currently assuming a single app/log version, but theoretically we could, for example, have multiple app versions show up in a single population. Need to handle this, e.g. allow a list.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, Map, int, None]]
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the ColumnValues function!")

    def __init__(self, app_id:str, user_id:Optional[str], session_id:Optional[str]):
        """Constructor for a GameData struct.

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
        """
        # TODO: event source, e.g. from game or from detector
        self.app_id               : str           = app_id
        self.user_id              : Optional[str] = user_id
        self.session_id           : Optional[str] = session_id

    @staticmethod
    def CompareVersions(a:str, b:str, version_separator='.') -> int:
        a_parts : Optional[List[int]]
        b_parts : Optional[List[int]]
        try:
            a_parts = [int(i) for i in a.split(version_separator)]
        except ValueError:
            a_parts = None
        try:
            b_parts = [int(i) for i in b.split(version_separator)]
        except ValueError:
            b_parts = None

        if a_parts is not None and b_parts is not None:
            for i in range(0, min(len(a_parts), len(b_parts))):
                if a_parts[i] < b_parts[i]:
                    return -1
                elif a_parts[i] > b_parts[i]:
                    return 1
            if len(a_parts) < len(b_parts):
                return -1
            elif len(a_parts) > len(b_parts):
                return 1
            else:
                return 0
        else:
            # try to do some sort of sane handling in case we got null values for a version
            if a_parts is None and b_parts is None:
                Logger.Log(f"Got invalid values of {a} & {b} for versions a & b!", logging.ERROR)
                return 0
            elif a_parts is None:
                Logger.Log(f"Got invalid value of {a} for version a!", logging.ERROR)
                return 1
            elif b_parts is None:
                Logger.Log(f"Got invalid value of {b} for version b!", logging.ERROR)
                return -1
        return 0 # should never reach here; just putting this here to satisfy linter

    @property
    def AppID(self) -> str:
        """The Application ID of the game that generated the Event

        Generally, this will be the game's name, or some abbreviation of the name.

        :return: The Application ID of the game that generated the Event
        :rtype: str
        """
        return self.app_id

    @property
    def SessionID(self) -> str:
        """The Session ID of the session that generated the Event

        Generally, this will be a numeric string.
        Every session ID is unique (with high probability) from all other sessions.

        :return: The Session ID of the session that generated the Event
        :rtype: str
        """
        return self.session_id or "*"

    @property
    def PlayerID(self) -> str:
        """Syntactic sugar for the UserID property:
        
        A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        This identifier is only included by games with a mechanism for individuals to resume play in a new session.

        :return: A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        :rtype: Optional[str]
        """
        return self.user_id or "*"

    @property
    def UserID(self) -> Optional[str]:
        """A persistent ID for a given user, identifying the individual across multiple gameplay sessions

        This identifier is only included by games with a mechanism for individuals to resume play in a new session.

        :return: A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        :rtype: Optional[str]
        """
        return self.user_id
