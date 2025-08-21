## import standard libraries
from typing import Dict, Final, List, Optional, Self
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.typing import Map

## @class DatabaseLocationSchema
class DatabaseLocationSchema(LocationSchema):
    """Class to encode the location of data within a database resource.

    Generally, the location of a database system would be a URLLocation,
    while DatabaseLocation refers to the location of a specific database or table within such a system.
    """

    _DEFAULT_DB_NAME    : Final[str]  = "DEFAULT_DB"
    _DEFAULT_TABLE_NAME : Final[None] = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, database_name:Optional[str], table_name:Optional[str], other_elements:Optional[Map]=None):
        """Constructor for the `DatabaseLocationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        In the format below, `TABLE_NAME` is an optional element.

        Expected format:

        ```
        {
            "DATABASE" : "database_name",
            "TABLE" : "table_name"
        },
        ```

        :param name: _description_
        :type name: str
        :param database_name: _description_
        :type database_name: Optional[str]
        :param table_name: _description_
        :type table_name: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._db_name    : str           = database_name or self._parseDatabaseName(unparsed_elements=unparsed_elements)
        self._table_name : Optional[str] = table_name    or self._parseTableName(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def DatabaseName(self) -> str:
        """The name of the database, within a DB system, where the table is located.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._db_name

    @property
    def TableName(self) -> Optional[str]:
        return self._table_name

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return self.DatabaseName + ( f".{self._table_name}" if self.TableName else "" )

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.DatabaseName}.{self.TableName}"
        return ret_val

    @classmethod
    def Default(cls) -> "DatabaseLocationSchema":
        return DatabaseLocationSchema(
            name="DefaultDatabaseLocation",
            database_name=cls._DEFAULT_DB_NAME,
            table_name=cls._DEFAULT_TABLE_NAME,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None,
                  default_override:Optional[Self]=None)-> "DatabaseLocationSchema":
        """Create a DatabaseLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: DatabaseLocationSchema
        """
        _db_name    : str           = cls._parseDatabaseName(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
        _table_name : Optional[str] = cls._parseTableName(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
        return DatabaseLocationSchema(name=name, database_name=_db_name, table_name=_table_name, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseTableName(unparsed_elements:Map,
                        key_overrides:Optional[Dict[str, str]]=None,
                        default_override:Optional["DatabaseLocationSchema"]=None) -> Optional[str]:
        default_keys : List[str] = ["table", "table_name"]
        search_keys  : List[str] = ([key_overrides[key] for key in default_keys if key in key_overrides] + default_keys) \
                                if key_overrides else default_keys
        default_value : Optional[str] = default_override.TableName if default_override else DatabaseLocationSchema._DEFAULT_TABLE_NAME

        return DatabaseLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_value,
            remove_target=True
        )

    @staticmethod
    def _parseDatabaseName(unparsed_elements:Map,
                           key_overrides:Optional[Dict[str, str]]=None,
                           default_override:Optional["DatabaseLocationSchema"]=None) -> str:
        default_keys : List[str] = ["database"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys \
                                if key_overrides else default_keys
        default_value : Optional[str] = default_override.DatabaseName if default_override else DatabaseLocationSchema._DEFAULT_DB_NAME

        return DatabaseLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_value,
            remove_target=True
        )
