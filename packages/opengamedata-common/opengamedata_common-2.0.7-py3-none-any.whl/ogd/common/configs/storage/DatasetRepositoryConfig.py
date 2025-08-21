# standard imports
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Final, Optional, Self, TypeAlias

# ogd imports
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.configs.storage.RepositoryIndexingConfig import RepositoryIndexingConfig
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.schemas.locations.DirectoryLocationSchema import DirectoryLocationSchema
from ogd.common.schemas.datasets.DatasetCollectionSchema import DatasetCollectionSchema
from ogd.common.utils.fileio import loadJSONFile
from ogd.common.utils.typing import Map

BaseLocation : TypeAlias = URLLocationSchema | DirectoryLocationSchema

# Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.
class DatasetRepositoryConfig(DataStoreConfig):
    """Simple Config-y class to track the base URLs/paths for a list of files and/or file templates.

    It also expects to track a mapping of game names to collections of datasets, under a "datasets" key.
    Then the structure is like:

    ```
    {
        "files_base" : "path/to/folder/"
        "templates_base" : "URL/to/templates/"
        "datasets" : {
            "GAME_NAME" : {
                "DATASET_START_to_END" : { ... },
                "DATASET_START_to_END" : { ... },
                ...
            }
            ...
        }
    }
    ```
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_INDEXING : Final[RepositoryIndexingConfig] = RepositoryIndexingConfig.Default()
    _DEFAULT_DATASETS : Final[Dict[str, DatasetCollectionSchema]] = {}

    def __init__(self, name:str,
                 # params for class
                 indexing:Optional[RepositoryIndexingConfig | Map | Path | str],
                 datasets:Optional[Dict[str, DatasetCollectionSchema]],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        fallbacks : Map = other_elements or {}

        self._indexing : RepositoryIndexingConfig           = self._toIndexingConfig(indexing=indexing, fallbacks=fallbacks)
        self._datasets : Dict[str, DatasetCollectionSchema] = datasets or self._parseDatasets(unparsed_elements=fallbacks)
        super().__init__(name=name, store_type="Repository", other_elements=other_elements)

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def LocalDirectory(self) -> DirectoryLocationSchema:
        """Property for the base 'path' to a set of dataset files.
        May be an actual path, or a base URL for accessing from a file server.

        :return: _description_
        :rtype: Optional[str]
        """
        return self.Indexing.LocalDirectory

    @property
    def RemoteURL(self) -> Optional[URLLocationSchema]:
        """Property for the base 'path' to a set of dataset files.
        May be an actual path, or a base URL for accessing from a file server.

        :return: _description_
        :rtype: Optional[str]
        """
        return self.Indexing.RemoteURL

    @property
    def TemplatesBase(self) -> URLLocationSchema:
        return self.Indexing.TemplatesURL

    @property
    def Indexing(self) -> RepositoryIndexingConfig:
        return self._indexing

    @property
    def Games(self) -> Dict[str, DatasetCollectionSchema]:
        return self._datasets

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @property
    def Location(self) -> BaseLocation:
        return self.LocalDirectory

    @property
    def Credential(self) -> EmptyCredential:
        return EmptyCredential.Default()

    @property
    def AsConnectionInfo(self) -> str:
        return f"{self.Name} : {self.Location.Location}"

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DatasetRepositoryConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetRepositoryConfig
        """
        return DatasetRepositoryConfig(name=name, indexing=None, datasets=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetRepositoryConfig":
        return DatasetRepositoryConfig(
            name="CONFIG NOT FOUND",
            indexing=cls._DEFAULT_INDEXING,
            datasets=cls._DEFAULT_DATASETS,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toIndexingConfig(indexing:Optional[RepositoryIndexingConfig | Map | Path | str], fallbacks:Map) -> RepositoryIndexingConfig:
        ret_val : RepositoryIndexingConfig
        if isinstance(indexing, RepositoryIndexingConfig):
            ret_val = indexing
        elif isinstance(indexing, dict):
            ret_val = RepositoryIndexingConfig.FromDict(name="DatasetRepositoryIndex", unparsed_elements=fallbacks)
        elif isinstance(indexing, Path) | isinstance(indexing, str):
            ret_val = RepositoryIndexingConfig(name="DatasetRepositoryIndex", local_dir=indexing, remote_url=None, templates_url=None)
        else:
            ret_val = DatasetRepositoryConfig._parseIndexingConfig(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _parseIndexingConfig(unparsed_elements:Map) -> RepositoryIndexingConfig:
        ret_val : RepositoryIndexingConfig

        raw_config = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["CONFIG", "INDEXING", "FILE_INDEXING"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        ret_val = RepositoryIndexingConfig.FromDict(name="RepositoryIndex", unparsed_elements=raw_config)

        return ret_val

    @staticmethod
    def _parseDatasets(unparsed_elements:Map) -> Dict[str, DatasetCollectionSchema]:
        ret_val : Dict[str, DatasetCollectionSchema]

        _data_elems = DatasetRepositoryConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["datasets"],
            to_type=[dict, str],
            default_value=None,
            remove_target=True
        )
        if isinstance(_data_elems, dict):
            ret_val = {
                key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=datasets if isinstance(datasets, dict) else {})
                for key, datasets in _data_elems.items()
            }
        elif isinstance(_data_elems, str):
            raw_elems = loadJSONFile(_data_elems)
            ret_val = {
                key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=val) \
                for key, val in raw_elems.items()
            }
        elif len(unparsed_elements) > 0:
            ret_val = {
                key : DatasetCollectionSchema.FromDict(name=key, unparsed_elements=datasets if isinstance(datasets, dict) else {})
                for key, datasets in unparsed_elements.items() if key.upper() != "CONFIG"
            }
        else:
            ret_val = DatasetRepositoryConfig._DEFAULT_DATASETS

        return ret_val

    # *** PRIVATE METHODS ***
