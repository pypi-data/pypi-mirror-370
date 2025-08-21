# import standard libraries
from pathlib import Path
from typing import Dict, Final, Optional, Self
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.KeyCredentialConfig import KeyCredential
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.utils.typing import Map

class BigQueryConfig(DataStoreConfig):
    _STORE_TYPE       : Final[str] = "BIGQUERY"
    _DEFAULT_LOCATION : Final[DatabaseLocationSchema] = DatabaseLocationSchema(
        name="DefaultBQLocation",
        database_name="wcer-field-day-ogd-1798",
        table_name=None,
        other_elements=None
    )
    _DEFAULT_CREDENTIAL : Final[KeyCredential] = KeyCredential(
        name="DefaultBQKeyCredential",
        location=FileLocationSchema(name="DefaultBQKeyFile", folder_path=Path("./config/"), filename="ogd.json"),
    )

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:Optional[DatabaseLocationSchema | Map | str],
                 credential:Optional[KeyCredential | Map | str],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `BigQueryConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "SOURCE_TYPE" : "BIGQUERY",
            "PROJECT_ID" : "someprojectid",
            "PROJECT_KEY" : {
                "KEY" : "key.txt",
                "PATH" : "./"
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param location: _description_
        :type location: Optional[DatabaseLocationSchema]
        :param credential: _description_
        :type credential: Optional[KeyCredential]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        fallbacks : Map = other_elements or {}

        self._location   : DatabaseLocationSchema = self._toLocation(location=location, fallbacks=fallbacks)
        self._credential : KeyCredential          = self._toCredential(credential=credential, fallbacks=fallbacks)

        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=fallbacks)

    @property
    def Location(self) -> DatabaseLocationSchema:
        """The Project ID for the BigQuery source

        :return: _description_
        :rtype: str
        """
        return self._location

    @property
    def Credential(self) -> KeyCredential:
        return self._credential

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.Location.Location}"
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: `{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @classmethod
    def Default(cls) -> "BigQueryConfig":
        return BigQueryConfig(
            name="DefaultBigQueryConfig",
            location=cls._DEFAULT_LOCATION,
            credential=KeyCredential.Default(),
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None) -> "BigQueryConfig":
        """Create a BigQuery Configuration from a dict.

        Expects dictionary to have the following form:
        ```json
        {
            "SOURCE_TYPE" : "BIGQUERY",
            "PROJECT_ID" : "someprojectid",
            "PROJECT_KEY" : {
                "FILE" : "key.txt",
                "PATH" : "./"
            }
        }
        ```

        Optionally, use "DATASET_ID" or "database" in place of "PROJECT_ID" key.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: BigQueryConfig
        """
        return BigQueryConfig(name=name, location=None, credential=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toLocation(location:Optional[DatabaseLocationSchema | Map | str], fallbacks:Map) -> DatabaseLocationSchema:
        ret_val : DatabaseLocationSchema
        if isinstance(location, DatabaseLocationSchema):
            ret_val = location
        elif isinstance(location, dict):
            ret_val = DatabaseLocationSchema.FromDict(name="BQDatabaseLocation", unparsed_elements=location)
        elif isinstance(location, str):
            ret_val = DatabaseLocationSchema(name="BQDatabaseLocation", database_name=location, table_name=None)
        else:
            ret_val = BigQueryConfig._parseLocation(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _toCredential(credential:Optional[KeyCredential | Map | str], fallbacks:Map) -> KeyCredential:
        ret_val : KeyCredential
        if isinstance(credential, KeyCredential):
            ret_val = credential
        elif isinstance(credential, dict):
            ret_val = KeyCredential.FromDict(name="BQCredential", unparsed_elements=credential)
        elif isinstance(credential, str):
            ret_val = KeyCredential(name="BQCredential", location=credential)
        else:
            ret_val = BigQueryConfig._parseCredential(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _parseLocation(unparsed_elements:Map) -> DatabaseLocationSchema:
        ret_val : DatabaseLocationSchema

        # First check for project ID or dataset ID given directly
        project_id = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_ID", "DATASET_ID"],
            to_type=str,
            default_value=None,
            remove_target=True
        )
        # If we found it, use to construct
        if project_id:
            ret_val = DatabaseLocationSchema(name="BigQueryLocation", database_name=project_id, table_name=None, other_elements={})
        # Else, have the class look for whatever key it's expecting.
        else:
            ret_val = DatabaseLocationSchema.FromDict(name="BigQueryLocation", unparsed_elements=unparsed_elements)
        
        return ret_val

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> KeyCredential:
        ret_val : KeyCredential

        raw_credential = BigQueryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["PROJECT_KEY"],
            to_type=[dict, str],
            default_value=BigQueryConfig._DEFAULT_CREDENTIAL,
            remove_target=True
        )
        if isinstance(raw_credential, dict):
            ret_val = KeyCredential.FromDict(name="KeyCredential", unparsed_elements=raw_credential)
        elif isinstance(raw_credential, str):
            ret_val = KeyCredential(name="BigQueryConfigCredential", location=FileLocationSchema.FromDict(name="BQCredentialLocation", unparsed_elements={"file":raw_credential}), other_elements=None)
        return ret_val

    # *** PRIVATE METHODS ***

