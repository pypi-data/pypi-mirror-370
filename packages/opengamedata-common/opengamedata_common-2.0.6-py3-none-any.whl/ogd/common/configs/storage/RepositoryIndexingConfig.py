# import standard libraries
from pathlib import Path
from typing import Dict, Final, Optional, Self
# import local files
from ogd.common.configs.Config import Config
from ogd.common.schemas.locations.DirectoryLocationSchema import DirectoryLocationSchema
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.utils.typing import Map

class RepositoryIndexingConfig(Config):
    _DEFAULT_LOCAL_DIR    : Final[DirectoryLocationSchema] = DirectoryLocationSchema(name="DefaultLocalDir", folder_path=Path("./data/"), other_elements={})
    _DEFAULT_REMOTE_RAW   : Final[str]                     = "https://opengamedata.fielddaylab.wisc.edu/"
    _DEFAULT_REMOTE_URL   : Final[URLLocationSchema]       = URLLocationSchema.FromString(name="DefaultRemoteURL", raw_url=_DEFAULT_REMOTE_RAW)
    _DEFAULT_TEMPLATE_RAW : Final[str]                     = "https://github.com/opengamedata/opengamedata-samples"
    _DEFAULT_TEMPLATE_URL : Final[URLLocationSchema]       = URLLocationSchema.FromString(name="DefaultTemplateURL", raw_url=_DEFAULT_TEMPLATE_RAW)

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 local_dir:Optional[DirectoryLocationSchema | Map | Path | str],
                 remote_url:Optional[URLLocationSchema | Map | str],
                 templates_url:Optional[URLLocationSchema | Map | str],
                 other_elements:Optional[Map]=None):
        """Constructor for the `IndexingConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "LOCAL_DIR"     : "./data/",
            "REMOTE_URL"    : "https://opengamedata.fielddaylab.wisc.edu/",
            "TEMPLATES_URL" : "https://github.com/opengamedata/opengamedata-samples"
        }
        ```

        :param name: _description_
        :type name: str
        :param local_dir: _description_
        :type local_dir: Optional[Path]
        :param remote_url: _description_
        :type remote_url: Optional[str]
        :param templates_url: _description_
        :type templates_url: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        fallbacks : Map = other_elements or {}

        self._local_dir     : DirectoryLocationSchema     = self._toLocalDir(local_dir=local_dir, fallbacks=fallbacks)
        self._remote_url    : Optional[URLLocationSchema] = self._toRemoteURL(remote_url=remote_url, fallbacks=fallbacks)
        self._templates_url : URLLocationSchema           = self._toTemplatesURL(templates_url=templates_url, fallbacks=fallbacks)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def LocalDirectory(self) -> DirectoryLocationSchema:
        return self._local_dir

    @property
    def RemoteURL(self) -> Optional[URLLocationSchema]:
        return self._remote_url

    @property
    def TemplatesURL(self) -> URLLocationSchema:
        return self._templates_url

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def Default(cls) -> "RepositoryIndexingConfig":
        return RepositoryIndexingConfig(
            name            = "DefaultFileIndexingConfig",
            local_dir       = cls._DEFAULT_LOCAL_DIR,
            remote_url      = cls._DEFAULT_REMOTE_URL,
            templates_url   = cls._DEFAULT_TEMPLATE_URL,
            other_elements  = {}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "RepositoryIndexingConfig":
        """Create a file indexing Configuration from a dict.

        Expects dictionary to have the following form:
        ```json
        {
            "LOCAL_DIR"     : "./data/",
            "REMOTE_URL"    : "https://opengamedata.fielddaylab.wisc.edu/",
            "TEMPLATES_URL" : "https://github.com/opengamedata/opengamedata-samples"
        }
        ```

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: FileIndexingConfig
        """
        return RepositoryIndexingConfig(name=name, local_dir=None, remote_url=None, templates_url=None, other_elements=unparsed_elements)


    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : Local=_{self.LocalDirectory}_, Remote=_{self.RemoteURL}_"
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _toLocalDir(local_dir:Optional[DirectoryLocationSchema | Map | Path | str], fallbacks:Map) -> DirectoryLocationSchema:
        ret_val : DirectoryLocationSchema
        if isinstance(local_dir, DirectoryLocationSchema):
            ret_val = local_dir
        elif isinstance(local_dir, dict):
            ret_val = DirectoryLocationSchema.FromDict(name="RepositoryDirectory", unparsed_elements=local_dir)
        elif isinstance(local_dir, str) or isinstance(local_dir, str):
            ret_val = DirectoryLocationSchema(name="RepositoryDirectory", folder_path=local_dir)
        else:
            ret_val = RepositoryIndexingConfig._parseLocalDir(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _toRemoteURL(remote_url:Optional[URLLocationSchema | Map | str], fallbacks:Map) -> URLLocationSchema:
        ret_val : URLLocationSchema
        if isinstance(remote_url, URLLocationSchema):
            ret_val = remote_url
        elif isinstance(remote_url, dict):
            ret_val = URLLocationSchema.FromDict(name="RemoteRepoURL", unparsed_elements=remote_url)
        elif isinstance(remote_url, str):
            ret_val = URLLocationSchema(name="RemoteRepoURL", url=remote_url)
        else:
            ret_val = RepositoryIndexingConfig._parseRemoteURL(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _toTemplatesURL(templates_url:Optional[URLLocationSchema | Map | str], fallbacks:Map) -> URLLocationSchema:
        ret_val : URLLocationSchema
        if isinstance(templates_url, URLLocationSchema):
            ret_val = templates_url
        elif isinstance(templates_url, dict):
            ret_val = URLLocationSchema.FromDict(name="TemplatesURL", unparsed_elements=fallbacks)
        elif isinstance(templates_url, str):
            ret_val = URLLocationSchema(name="TemplatesURL", url=templates_url)
        else:
            ret_val = RepositoryIndexingConfig._parseTemplatesURL(unparsed_elements=fallbacks)
        return ret_val

    @staticmethod
    def _parseLocalDir(unparsed_elements:Map) -> DirectoryLocationSchema:
        ret_val : DirectoryLocationSchema

        raw_base = RepositoryIndexingConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["files_base", "local_dir", "folder", "path"],
            to_type=[Path, str, dict],
            default_value=None,
            remove_target=True
        )
        if raw_base:
            if isinstance(raw_base, Path):
                ret_val = DirectoryLocationSchema(name="LocalDir", folder_path=raw_base)
            elif isinstance(raw_base, str):
                ret_val = DirectoryLocationSchema(name="LocalDir", folder_path=Path(raw_base))
            elif isinstance(raw_base, dict):
                ret_val = DirectoryLocationSchema.FromDict(name="LocalDir", unparsed_elements=raw_base)
        else:
            ret_val = RepositoryIndexingConfig._DEFAULT_LOCAL_DIR

        return ret_val

    @staticmethod
    def _parseRemoteURL(unparsed_elements:Map) -> URLLocationSchema:
        ret_val : URLLocationSchema

        raw_url = RepositoryIndexingConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["remote_url", "url"],
            to_type=[str, dict],
            default_value=None,
            remove_target=True
        )
        if raw_url:
            if isinstance(raw_url, str):
                ret_val = URLLocationSchema.FromString(name="RemoteURL", raw_url=raw_url)
            elif isinstance(raw_url, dict):
                ret_val = URLLocationSchema.FromDict(name="RemoteURL", unparsed_elements=raw_url)
            else:
                ret_val = RepositoryIndexingConfig._DEFAULT_REMOTE_URL

        return ret_val

    @staticmethod
    def _parseTemplatesURL(unparsed_elements:Map) -> URLLocationSchema:
        ret_val : URLLocationSchema

        raw_url = RepositoryIndexingConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["templates_url", "url"],
            to_type=[str, dict],
            default_value=None,
            remove_target=True
        )
        if raw_url:
            if isinstance(raw_url, str):
                ret_val = URLLocationSchema.FromString(name="TemplatesURL", raw_url=raw_url)
            elif isinstance(raw_url, dict):
                ret_val = URLLocationSchema.FromDict(name="TemplatesURL", unparsed_elements=raw_url)
            else:
                ret_val = RepositoryIndexingConfig._DEFAULT_TEMPLATE_URL

        return ret_val

    # *** PRIVATE METHODS ***
