# import standard libraries
from typing import Dict, Final, Optional, Self, TypeAlias
from pathlib import Path
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.schemas.locations.RAMLocationSchema import RAMLocationSchema
from ogd.common.utils.typing import Map

class DictionaryStoreConfig(DataStoreConfig):
    _STORE_TYPE = "DICTIONARY"
    _DEFAULT_LOCATION: Final[RAMLocationSchema] = RAMLocationSchema(name="DictionaryLocation")
    _DEFAULT_CREDENTIAL: Final[EmptyCredential] = EmptyCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:Optional[RAMLocationSchema],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `FileStoreConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        In the format below, `FILE_CREDENTIAL` is optional.

        Expected format:

        ```
        {
            "SOURCE_TYPE" : "FILE",
            "PATH" : "path/to/file.ext",
            "FILE_CREDENTIAL" : {
                "USER" : "username",
                "PASS" : "password"
            }
        }
        ```

        :param name: _description_
        :type name: str
        :param location: _description_
        :type location: FileLocationSchema
        :param file_credential: _description_
        :type file_credential: FileCredential
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._location   = location or DictionaryStoreConfig._DEFAULT_LOCATION
        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=unparsed_elements)

    @property
    def Location(self) -> RAMLocationSchema:
        return self._location

    @property
    def Credential(self) -> EmptyCredential:
        return DictionaryStoreConfig._DEFAULT_CREDENTIAL

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = "DICTIONARY SOURCE"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"DICTIONARY"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DictionaryStoreConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: FileStoreConfig
        """
        return DictionaryStoreConfig(name=name, location=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DictionaryStoreConfig":
        return DictionaryStoreConfig(
            name="DefaultFileStoreConfig",
            location=cls._DEFAULT_LOCATION,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
