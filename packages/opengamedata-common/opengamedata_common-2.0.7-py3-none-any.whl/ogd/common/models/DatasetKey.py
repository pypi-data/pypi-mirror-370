# standard imports
import re
from calendar import monthrange
from datetime import date, datetime
from pathlib import Path
from typing import Final, List, Optional, Tuple

from dateutil.parser import parse as dateparse

class DatasetKey:
    """
    DatasetKey dumb struct.

    TODO : Rework this to be more like other schemas.
    """

    #region *** BUILT-INS & PROPERTIES ***

    _DEFAULT_GAME_ID   : Final[str] = "UNKOWN_GAME"
    _DEFAULT_DATE_FROM : Final[date] = date(year=2000, month=1, day=1)
    _DEFAULT_DATE_TO   : Final[date] = date(year=2000, month=1, day=31)

    """Simple little class to make logic with dataset keys easier
    """
    def __init__(self, game_id:str,
                 full_month:Optional[str | Tuple[int, int]]=None, full_file:Optional[str | Path]=None,
                 from_date:Optional[date|str|int]=None, to_date:Optional[date|str|int]=None,
                 player_id:Optional[str]=None, player_id_file:Optional[str|Path]=None,
                 session_id:Optional[str]=None, session_id_file:Optional[str|Path]=None
    ):
        self._game_id      : str = game_id or DatasetKey._DEFAULT_GAME_ID
        if not any(x is not None for x in [full_month, full_file, from_date, to_date, player_id, player_id_file, session_id, session_id_file]):
            raise ValueError("Attempted to create DatasetKey without specifying dates or a player or a session identifier!")
        else:
            self._from_date : Optional[date] = None
            self._to_date   : Optional[date] = None
            if full_month:
                if isinstance(full_month, str):
                    month_start = dateparse(timestr=full_month, default=datetime.min)
                    _, month_end = monthrange(year=month_start.year, month=month_start.month)
                    self._from_date = month_start.date()
                    self._to_date   = month_start.replace(day=month_end).date()
            else:
                # 1. Get from date
                if isinstance(from_date, date):
                    self._from_date = from_date
                elif isinstance(from_date, str):
                    self._from_date = dateparse(from_date).date()
                elif isinstance(from_date, int):
                    self._from_date = dateparse(str(from_date)).date()
                # 2. Get to date
                if isinstance(to_date, date):
                    self._to_date = to_date
                elif isinstance(to_date, str):
                    self._to_date = dateparse(to_date).date()
                elif isinstance(to_date, int):
                    self._to_date = dateparse(str(to_date)).date()
            self._full_file       : Optional[str]  = full_file.stem if isinstance(full_file, Path) else Path(full_file).stem if isinstance(full_file, str) else None
            self._player_id       : Optional[str]  = player_id
            self._player_id_file  : Optional[str]  = player_id_file.stem if isinstance(player_id_file, Path) else Path(player_id_file).stem if isinstance(player_id_file, str) else None
            self._session_id      : Optional[str]  = session_id
            self._session_id_file : Optional[str]  = session_id_file.stem if isinstance(session_id_file, Path) else Path(session_id_file).stem if isinstance(session_id_file, str) else None

    def __str__(self):
        """Returns formatted string for the dataset key, with the form "GAME_ID_<from_ID>_<YYYYMMDD_to_YYYYMMDD>"

        The formatting works as follows:
        1. `game_id` always comes first
        2. If a date range was given, it always appears at the end in form `YYYYMMDD_to_YYYYMMDD`, where the first part is the earliest day, the later part is the last day.
        3. If session/player IDs were given, the most-specific such ID appears after the `game_id`  
            a. A session ID is always more specific than a player ID  
            b. A single ID is always more specific than a file.  
            * Note that in general, the system should never allow you to specify multiple IDs,
            e.g. you should not be able to ever request a player ID files and a specific individual session ID.
            Should any such issue arrive, however, it will be resolved with the logic above.  

        :return: _description_
        :rtype: _type_
        """
        date_clause = f"{self._from_date.strftime('%Y%m%d')}_to_{self._to_date.strftime('%Y%m%d')}" if self._from_date and self._to_date else None
        has_id = any([id is not None for id in [self._session_id, self._session_id_file, self._player_id, self._player_id_file, self._full_file]])
        id_clause = f"from_{self._session_id or self._session_id_file or self._player_id or self._player_id_file or self._full_file}" if has_id else None
        pieces : List[str] = [x for x in [self._game_id, id_clause, date_clause] if x is not None]
        return "_".join(pieces)
    
    @property
    def IsValid(self) -> bool:
        range_elements = [
            self._from_date, self._to_date,
            self._player_id, self._player_id_file,
            self._session_id, self._session_id_file
        ]
        return any(elem is not None for elem in range_elements)
    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def DateFrom(self) -> Optional[date]:
        return self._from_date
    @property
    def DateTo(self) -> Optional[date]:
        return self._to_date

    #endregion

    #region *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetKey":
        return DatasetKey(
            game_id=cls._DEFAULT_GAME_ID,
            from_date=cls._DEFAULT_DATE_FROM,
            to_date=cls._DEFAULT_DATE_TO
        )

    @staticmethod
    def FromString(raw_key:str):
        """Parse a dataset key from string.

        :param raw_key: _description_
        :type raw_key: str
        :return: _description_
        :rtype: _type_
        """
        game_id_pattern = r"[A-Z1-9_]+"
        game_id_group   = f"(?P<game_id>{game_id_pattern})"
        id_pattern      = r"from_[\w_]+"
        id_group        = f"(?P<id_only>{id_pattern})"
        date_pattern    = r"\d{8}_to_\d{8}"
        date_group      = f"(?P<date_only>{date_pattern})"
        id_and_date_group = f"(?:(?P<id>{id_pattern})_(?P<date>{date_pattern}))"
        pattern = f"{game_id_group}_(?:{id_and_date_group}|{id_group}|{date_group})"
        split_date_pattern = r"(?P<start>\d{8})_to_(?P<end>\d{8})"
        idtype_pattern = r"(?P<singlesession>\d+)|(?P<singleplayer>[A-Za-z]+)|(?P<file>.+)"
        match = re.match(pattern=pattern, string=raw_key)
        if match:
            _game_id : str = match.group('game_id')
            _from_date  : Optional[date] = None
            _to_date    : Optional[date] = None
            _session_id : Optional[str]  = None
            _player_id  : Optional[str]  = None
            _file_name  : Optional[str]  = None
        # 1. Get Game ID from key
        # 2. Get Dates from key
            # If this _dataset_key matches the expected format,
            # i.e. split is: ["GAME", "ID", "PARTS",..., "YYYYMMDD", "to", "YYYYMMDD"]
            # Technically, the dates aren't required, and we could have a player ID instead.
            # In that case, we just don't have dates built into the Key.
            # File API should be prepared to account for this.
            date_str = match.groupdict().get("date") or match.groupdict().get("date_only") or ""
            date_match = re.match(split_date_pattern, date_str)
            if date_match:
                _from_date = dateparse(date_match.group("start")).date()
                _to_date   = dateparse(date_match.group("end")).date()
            id_str = match.groupdict().get("id") or match.groupdict().get("id_only") or ""
            id_match = re.match(f"from_{idtype_pattern}", id_str)
            if id_match:
                _session_id = id_match.group("singlesession")
                _player_id  = id_match.group("singleplayer")
                _file_name  = id_match.group("file")
        else:
            raise ValueError(f"{raw_key} is not a valid DatasetKey!")
        return DatasetKey(game_id=_game_id, from_date=_from_date, to_date=_to_date, session_id=_session_id, player_id=_player_id, full_file=_file_name)

    #endregion

    #region *** PUBLIC METHODS ***

    #endregion

    #region *** PRIVATE STATICS ***

    #endregion

    #region *** PRIVATE METHODS ***

    #endregion
