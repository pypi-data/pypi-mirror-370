## import standard libraries
from typing import Dict, Final, List, Optional, TypeAlias
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.typing import Map

ColumnMapElement : TypeAlias = Optional[str | List[str] | Dict[str,str]]

## @class TableSchema
class ColumnMapSchema(Schema):

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_COLUMNS : Final[List] = []

    def __init__(self, name,
                 app_id:Optional[ColumnMapElement],
                 user_id:Optional[ColumnMapElement],
                 session_id:Optional[ColumnMapElement],
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
            "app_id"               : null,
            "session_id"           : "session_id",
            "user_data"            : "user_data",
            ...
        }
        ```

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        # declare and initialize vars
        self._raw_map : Map = other_elements or {}

        self._app_id     : ColumnMapElement = app_id     or self._parseAppID(unparsed_elements=self._raw_map)
        self._user_id    : ColumnMapElement = user_id    or self._parseUserID(unparsed_elements=self._raw_map)
        self._session_id : ColumnMapElement = session_id or self._parseSessionID(unparsed_elements=self._raw_map)

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Mapping(self) -> Dict[str, ColumnMapElement]:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._raw_map

    @property
    def AppIDColumn(self) -> Optional[ColumnMapElement]:
        return self._app_id

    @property
    def UserIDColumn(self) -> Optional[ColumnMapElement]:
        return self._user_id

    @property
    def SessionIDColumn(self) -> Optional[ColumnMapElement]:
        return self._session_id

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        event_column_list = []
        for event_element,columns_mapped in self.Mapping.items():
            if columns_mapped is not None:
                if isinstance(columns_mapped, str):
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*'  ")
                elif isinstance(columns_mapped, int):
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*'  ")
                elif isinstance(columns_mapped, list):
                    mapped_list = ", ".join([f"'*{item}*'" for item in columns_mapped])
                    event_column_list.append(f"**{event_element}** = Columns {mapped_list}  ") # figure out how to do one string foreach item in list.
                else:
                    event_column_list.append(f"**{event_element}** = Column '*{columns_mapped}*' (DEBUG: Type {type(columns_mapped)})  ")
            else:
                event_column_list.append(f"**{event_element}** = null  ")
        ret_val = "\n".join(event_column_list)
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseAppID(unparsed_elements:Map) -> Optional[str | List[str]]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["app_id", "game_id"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseUserID(unparsed_elements:Map) -> Optional[str | List[str]]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["user_id", "player_id"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseSessionID(unparsed_elements:Map) -> Optional[str | List[str]]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["session_id"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    # *** PRIVATE METHODS ***
