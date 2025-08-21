# import standard libraries
import abc
from typing import Final, Optional
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.typing import Map


class DataStoreConfig(Config):
    """Dumb struct to contain data pertaining to a data source, which a StorageConnector can connect to.

    Every source has:
    - A named "type" to inform what StorageConnector should be instantiated
    - A config "name" for use within ogd software for identifying a particular data source config
    - A resource "location" for use by the StorageConnector (such as a filename, cloud project name, or database host)
    """

    _DEFAULT_TYPE : Final[str] = "UNKNOWN STORE TYPE"

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Location(self) -> LocationSchema:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Location function!")

    @property
    @abc.abstractmethod
    def Credential(self) -> CredentialConfig:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Credential function!")

    @property
    @abc.abstractmethod
    def AsConnectionInfo(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the AsConnectionInfo function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, store_type:Optional[str], other_elements:Optional[Map]=None):
        """Constructor for the `DataStoreConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.
        Because `DataStoreConfig` is just a base class for other specific datastore configuration classes,
        the sample format below includes keys not used by `DataStoreConfig`.
        The actual key used is `SOURCE_TYPE`, which may optionally be named `DB_TYPE`.

        Expected format:

        ```
        {
            "SOURCE_TYPE" : "BIGQUERY",
            "PROJECT_ID" : "someprojectid",
            "FILE_CREDENTIAL" : {
                "FILE" : "key.txt",
                "PATH" : "./"
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param store_type: _description_
        :type store_type: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._store_type : str = store_type or self._parseStoreType(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def Type(self) -> str:
        """The type of source indicated by the data source schema.

        This includes but is not limited to "FIREBASE", "BIGQUERY", and "MySQL".
        It is used primarily to indicate that data store class the config is compatible with;
        may be subject to replacement/removal at some point.

        :return: A string describing the type of the data source
        :rtype: str
        """
        return self._store_type

    # *** PUBLIC STATICS ***


    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseStoreType(unparsed_elements:Map) -> str:
        return DataStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["SOURCE_TYPE", "DB_TYPE"],
            to_type=str,
            default_value=DataStoreConfig._DEFAULT_TYPE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
