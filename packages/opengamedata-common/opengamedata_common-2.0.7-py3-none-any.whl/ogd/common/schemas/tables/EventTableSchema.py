## import standard libraries
import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple, Optional, Self
## import local files
from ogd.common.models.Event import Event, EventSource
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.tables.EventMapSchema import EventMapSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

## @class TableSchema
class EventTableSchema(TableSchema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name,
                 column_map:Optional[EventMapSchema],
                 columns:Optional[List[ColumnSchema]],
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "column_map": {
                "session_id"           : "session_id",
                "app_id"               : null,
                "timestamp"            : ["client_time", "client_time_ms"],
                ...
            },

            "columns": [
                {
                    "name": "session_id",
                    "readable": "Session ID",
                    "description": "ID for the play session",
                    "type": "str"
                },
                {
                    "name": "client_time",
                    ...
                },
        },
        ```

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        unparsed_elements : Map = other_elements or {}

        self._column_map : EventMapSchema = column_map or self._parseColumnMap(unparsed_elements=unparsed_elements)
        # a couple other vars used in the row->event conversion
        self._latest_session : Optional[str] = None
        self._next_index     : int           = 0
        super().__init__(name=name, columns=columns, other_elements=unparsed_elements)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def ColumnMap(self) -> EventMapSchema:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._column_map

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        _columns_markdown = "\n".join([item.AsMarkdown for item in self.Columns])
        ret_val = "\n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            _columns_markdown,
            "## Event Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self.ColumnMap.AsMarkdown,
            ""]
        )
        return ret_val

    @classmethod
    def Default(cls) -> "EventTableSchema":
        return EventTableSchema(
            name="DefaultEventTableSchema",
            column_map=EventMapSchema.Default(),
            columns=cls._DEFAULT_COLUMNS,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "EventTableSchema":
        """Function to generate a TableSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "table_type" : <either EVENT or FEATURE>,
            "columns" : [<list of column schemas>],
            "column_map" : {<mapping of column names to indices>}
        }
        ```

        The specific handling of the column map will be determined by the specific TableSchema subclass on which the FromDict feature is called.

        :param name: The name of the returned TableSchema object
        :type name: str
        :param all_elements: A dictionary containing all elements to be parsed into the TableSchema object
        :type all_elements: Dict[str, Any]
        :param logger: An optional logger for outputting errors/warnings, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: An instance of the TableSchema subclass on which the function is called
        :rtype: TableSchema
        """
        return EventTableSchema(name=name, column_map=None, columns=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    _conversion_warnings = Counter()
    def EventFromRow(self, row:Tuple, concatenator:str = '.', fallbacks:Map={}) -> Event:
        """Function to convert a row to an Event, based on the loaded schema.
        In general, columns specified in the schema's column_map are mapped to corresponding elements of the Event.
        If the column_map gave a list, rather than a single column name, the values from each column are concatenated in order with '.' character separators.
        Finally, the concatenated values (or single value) are parsed according to the type required by Event.
        One exception: For event_data, we expect to create a Dict object, so each column in the list will have its value parsed according to the type in 'columns',
            and placed into a dict mapping the original column name to the parsed value (unless the parsed value is a dict, then it is merged into the top-level dict).

        .. TODO Use conversions utils to deal with the types we're getting from the row.

        :param row: _description_
        :type row: Tuple
        :param concatenator: _description_, defaults to '.'
        :type concatenator: str, optional
        :param fallbacks: _description_, defaults to {}
        :type fallbacks: Map, optional
        :raises TypeError: _description_
        :return: _description_
        :rtype: Event
        """
        ret_val : Event

        if not isinstance(self.ColumnMap, EventMapSchema):
            raise TypeError(f"{self.Name} contains a mapping for Features, not Events!")

        # define vars to be passed as params
        app_id      : str
        user_id     : Optional[str]
        sess_id     : str
        app_ver     : str
        app_br      : str
        log_ver     : str
        tstamp      : datetime
        offset      : Optional[timezone]
        event_index : Optional[int]
        ename       : str
        edata       : Map
        state       : Optional[Map]
        udata       : Optional[Map]

        # 1. Get ID data
        idx = self._indexFromMapping(self.ColumnMap.AppIDColumn)
        app_id = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=fallbacks.get("app_id"))
        if not isinstance(app_id, str):
            if "app_id" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set app_id as {type(app_id)}, but app_id should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["app_id"] += 1
            app_id = str(app_id)

        idx = self._indexFromMapping(self.ColumnMap.UserIDColumn)
        user_id = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=fallbacks.get("user_id"))
        if user_id is not None and not isinstance(user_id, str):
            if "uid" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set user_id as {type(user_id)}, but user_id should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["uid"] += 1
            user_id = str(user_id)

        idx = self._indexFromMapping(self.ColumnMap.SessionIDColumn)
        sess_id = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=fallbacks.get("session_id"))
        if not isinstance(sess_id, str):
            if "sess_id" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set session_id as {type(sess_id)}, but session_id should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["sess_id"] += 1
            sess_id = str(sess_id)
        if self._latest_session != sess_id:
            self._latest_session = sess_id
            self._next_index = 0

        # 2. Get versioning data
        idx = self._indexFromMapping(self.ColumnMap.AppVersionColumn)
        app_ver = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=fallbacks.get('app_version'))
        if not isinstance(app_ver, str):
            if "app_ver" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set app_version as {type(app_ver)}, but app_version should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["app_ver"] += 1
            app_ver = str(app_ver)

        idx = self._indexFromMapping(self.ColumnMap.AppBranchColumn)
        app_br = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=fallbacks.get('app_branch'))
        if not isinstance(app_br, str):
            if "app_br" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set app_branch as {type(app_br)}, but app_branch should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["app_br"] += 1
            app_br = str(app_br)

        idx = self._indexFromMapping(self.ColumnMap.LogVersionColumn)
        log_ver = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=fallbacks.get('log_version', "0"))
        if not isinstance(log_ver, str):
            if "log_ver" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set log_version as {type(log_ver)}, but log_version should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["log_ver"] += 1
            log_ver = str(log_ver)

        # 3. Get sequencing data

        # TODO: go bac to isostring function; need 0-padding on ms first, though.
        # Not sure how old this to-do is though, it may not be relevant anymore.
        idx = self._indexFromMapping(self.ColumnMap.TimestampColumn)
        tstamp  = self._valueFromRow(row=row, indices=idx,   concatenator=concatenator, fallback=None)
        if not isinstance(tstamp, datetime):
            if "timestamp" not in self._conversion_warnings:
                Logger.Log(f"{self.Name} event table schema parsed timestamp as {type(tstamp)}, but timestamp should be a datetime", logging.WARN)
            self._conversion_warnings["timestamp"] += 1
            tstamp = conversions.DatetimeFromString(tstamp)

        idx = self._indexFromMapping(self.ColumnMap.TimeOffsetColumn)
        offset = self._valueFromRow(row=row, indices=idx,  concatenator=concatenator, fallback=fallbacks.get('time_offset'))
        if isinstance(offset, timedelta):
            if "offset" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set offset as {type(offset)}, but offset should be a timezone"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["offset"] += 1
            offset = timezone(offset)

        idx = self._indexFromMapping(self.ColumnMap.EventSequenceIndexColumn)
        event_index = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=fallbacks.get('event_sequence_index', self._next_index))
        if not isinstance(event_index, int):
            if "index" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set event_sequence_index as {type(event_index)}, but event_sequence_index should be an int"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["index"] += 1
            event_index = int(event_index or self._next_index)

        # 4. Get event-specific data
        idx = self._indexFromMapping(self.ColumnMap.EventNameColumn)
        ename   = self._valueFromRow(row=row, indices=idx,   concatenator=concatenator, fallback=fallbacks.get('event_name'))
        if not isinstance(ename, str):
            if "ename" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set event_name as {type(ename)}, but event_name should be a string"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["ename"] += 1
            ename = str(ename)

        idx = self._indexFromMapping(self.ColumnMap.EventSourceColumn)
        esrc = self._valueFromRow(row=row, indices=idx, concatenator=concatenator, fallback=fallbacks.get('event_source', EventSource.GAME))
        if not isinstance(esrc, EventSource):
            if "esrc" not in self._conversion_warnings:
                _msg = f"{self.Name} event table schema set event_source as {type(esrc)}, but event_source should be an EventSource"
                Logger.Log(_msg, logging.WARN)
            self._conversion_warnings["esrc"] += 1
            esrc = EventSource.GENERATED if esrc == "GENERATED" else EventSource.GAME

        idx = self._indexFromMapping(self.ColumnMap.EventDataColumn)
        datas : Dict[str, Any] = self._valueFromRow(row=row, indices=idx,   concatenator=concatenator, fallback=fallbacks.get('event_data'))
        edata   = dict(sorted(datas.items())) # Sort keys alphabetically

        # 5. Get context data

        idx = self._indexFromMapping(self.ColumnMap.UserDataColumn)
        udata   = self._valueFromRow(row=row, indices=idx,    concatenator=concatenator, fallback=fallbacks.get('user_data'))

        idx = self._indexFromMapping(self.ColumnMap.GameStateColumn)
        state   = self._valueFromRow(row=row, indices=idx,   concatenator=concatenator, fallback=fallbacks.get('game_state'))

        ret_val = Event(app_id=app_id, user_id=user_id, session_id=sess_id,
                        timestamp=tstamp, time_offset=offset, event_sequence_index=event_index,
                        event_name=ename, event_source=esrc, event_data=edata,
                        app_version=app_ver, app_branch=app_br, log_version=log_ver,
                        user_data=udata,
                        game_state=state, )
        ret_val.FallbackDefaults(index=self._next_index)
        self._next_index = (event_index or self._next_index) + 1

        return ret_val

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    @staticmethod
    def _parseColumnMap(unparsed_elements:Map) -> EventMapSchema:
        ret_val : EventMapSchema

        raw_map = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["column_map"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if raw_map:
            ret_val = EventMapSchema.FromDict(name="ColumnMap", unparsed_elements=raw_map)
        else:
            ret_val = EventMapSchema.Default()

        return ret_val
