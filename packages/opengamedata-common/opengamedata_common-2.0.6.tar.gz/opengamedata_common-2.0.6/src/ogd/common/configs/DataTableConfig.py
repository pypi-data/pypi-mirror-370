# import standard libraries
from typing import Dict, Final, LiteralString, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.schemas.tables.TableSchemaFactory import TableSchemaFactory
from ogd.common.schemas.tables import TableSchema as ts
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
from ogd.common.utils.typing import Map

class DataTableConfig(Schema):
    """A simple Schema structure containing configuration for a specific table of data.

    It principally contains 3 key components:
    1. `StoreConfig` : The DataStoreConfig that specifies the storage resource containing the configured table.
    2. `Location`    : The LocationSchema that specifies the location of the configured table within the storage resource.
    3. `TableSchema` : The TableSchema that specifies the structure of the configured table.
    
    When given to an interface, this schema is treated as a specification of the table from which to retrieve data.
    When given to an outerface, this schema is treated as a specification of the table in which to store data.
    (note that some interfaces/outerfaces, such as debugging i/o-faces, may ignore the configuration)

    .. TODO : Implement and use a smart Load(...) function of TableConfig to load schema from given name, rather than FromFile.
    """

    _DEFAULT_STORE_NAME       : Final[LiteralString] = "OPENGAMEDATA_BQ"
    _DEFAULT_TABLE_SCHEMA_NAME : Final[LiteralString] = "OPENGAMEDATA_BIGQUERY"
    _DEFAULT_DB_NAME           : Final[LiteralString] = "UNKNOWN GAME"
    _DEFAULT_TABLE_NAME        : Final[LiteralString] = "_daily"
    _DEFAULT_TABLE_LOC         : Final[DatabaseLocationSchema] = DatabaseLocationSchema(
        name="DefaultTableLocation",
        database_name=_DEFAULT_DB_NAME,
        table_name=_DEFAULT_TABLE_NAME
    )

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 store_name:Optional[str],
                 schema_name:Optional[str],
                 table_location:Optional[DatabaseLocationSchema],
                 store_config:Optional[DataStoreConfig]=None, table_schema:Optional[ts.TableSchema]=None,
                 other_elements:Optional[Map]=None):
        """Constructor for the `DataTableConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "source" : "DATA_SOURCE_NAME",
            "database": "db_name",
            "schema" : "TABLE_SCHEMA_NAME",
            "table" : "table_name"
        },
        ```

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: Optional[str]
        :param source_name: _description_
        :type source_name: Optional[str]
        :param schema_name: _description_
        :type schema_name: Optional[str]
        :param table_location: _description_
        :type table_location: Optional[DatabaseLocationSchema]
        :param other_elements: _description_
        :type other_elements: Optional[Map]
        """
        unparsed_elements : Map = other_elements or {}

        self._store_name     : str                       = store_name    or self._parseStoreName(unparsed_elements=unparsed_elements)
        self._store_config   : Optional[DataStoreConfig] = store_config
        self._schema_name    : str                       = schema_name    or self._parseTableSchemaName(unparsed_elements=unparsed_elements)
        self._table_schema   : ts.TableSchema            = table_schema   or TableSchemaFactory.FromFile(filename=self._schema_name)
        self._table_location : DatabaseLocationSchema    = table_location or self._parseTableLocation(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def StoreName(self) -> str:
        """The string name of the DataStoreConfig for this DataTableConfig.

        The DataStoreConfig contains information necessary to connect to the data store containing the configured data table.

        :return: _description_
        :rtype: str
        """
        return self._store_name

    @property
    def StoreConfig(self) -> Optional[DataStoreConfig]:
        """The DataStoreConfig for this DataTableConfig.

        This DataStoreConfig contains information necessary to connect to the data store containing the configured data table.

        :return: _description_
        :rtype: Optional[DataStoreConfig]
        """
        return self._store_config
    @StoreConfig.setter
    def StoreConfig(self, source:DataStoreConfig):
        self._store_config = source

    @property
    def TableSchemaName(self) -> str:
        """The string name of the TableSchema for this DataTableConfig.

        The TableSchema contains information on the internal column structure of the configured data table.

        :return: _description_
        :rtype: str
        """
        return self._schema_name

    @property
    def TableSchema(self) -> ts.TableSchema:
        """The TableSchema for this DataTableConfig.

        This TableSchema contains information on the internal column structure of the configured data table.

        :return: _description_
        :rtype: TableSchema
        """
        return self._table_schema
    @TableSchema.setter
    def TableSchema(self, schema:ts.TableSchema):
        self._table_schema = schema

    @property
    def Location(self) -> DatabaseLocationSchema:
        """The DatabaseLocationSchema for this DataTableConfig.

        This DatabaseLocationSchema contains information on how to locate the configured data table within its data store.

        .. TODO: Allow other types of location, not every data store is a database. For now, when using non-database stores, the DatabaseLocationSchema can simply be interpreted as containing e.g. the sheet (in an Excel file) within a file, or file within a folder.

        :return: _description_
        :rtype: DatabaseLocationSchema
        """
        return self._table_location

    @property
    def DatabaseName(self) -> str:
        """The database name provided by the DataTableConfig's Location property

        :return: _description_
        :rtype: str
        """
        return self._table_location.DatabaseName

    @property
    def TableName(self) -> Optional[str]:
        """The table name provided by the DataTableConfig's Location property

        :return: _description_
        :rtype: Optional[str]
        """
        return self._table_location.TableName

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.TableSchemaName}_ format, source {self.StoreName} : {self.Location.Location}"
        return ret_val

    @classmethod
    def Default(cls) -> "DataTableConfig":
        return DataTableConfig(
            name="DefaultDataTableConfig",
            store_name=cls._DEFAULT_STORE_NAME,
            store_config=None,
            schema_name=cls._DEFAULT_TABLE_SCHEMA_NAME,
            table_schema=None,
            table_location=cls._DEFAULT_TABLE_LOC,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None,
                  default_override:Optional[Self]=None) -> "DataTableConfig":
        """Create a DataTableConfig from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.
        TODO : data_sources shouldn't really be a param here. Better to have e.g. a way to register the list into DataTableConfig class, or something.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: DataTableConfig
        """
        return DataTableConfig(name=name, store_name=None, schema_name=None,
                                table_location=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseStoreName(unparsed_elements:Map) -> str:
        return DataTableConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["source", "source_name", "store", "store_name"],
            to_type=str,
            default_value=DataTableConfig._DEFAULT_STORE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseTableSchemaName(unparsed_elements:Map) -> str:
        return DataTableConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["table_schema", "schema"],
            to_type=str,
            default_value=DataTableConfig._DEFAULT_TABLE_SCHEMA_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseTableLocation(unparsed_elements:Map) -> DatabaseLocationSchema:
        return DatabaseLocationSchema.FromDict(
            name="TableLocation",
            unparsed_elements=unparsed_elements,
            default_override=DataTableConfig._DEFAULT_TABLE_LOC
        )

    # *** PRIVATE METHODS ***
