# import standard libraries
from typing import Dict, Final, Optional, Self, TypeAlias
from pathlib import Path
# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.credentials.EmptyCredential import EmptyCredential
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.schemas.locations.FileLocationSchema import FileLocationSchema
from ogd.common.utils.typing import Map

FileCredential : TypeAlias = PasswordCredential | EmptyCredential

class FileStoreConfig(DataStoreConfig):
    _STORE_TYPE = "FILE"
    _DEFAULT_LOCATION: Final[FileLocationSchema] = FileLocationSchema(
        name="DefaultFileStoreLocation",
        folder_path=Path('./data'),
        filename="UNKNOWN.tsv",
        other_elements=None
    )
    _DEFAULT_CREDENTIAL: Final[EmptyCredential] = EmptyCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:Optional[FileLocationSchema | Path | str],
                 file_credential:Optional[FileCredential],
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

        self._location    : FileLocationSchema
        if isinstance(location, FileLocationSchema):
            self._location = location
        elif isinstance(location, Path):
            self._location = FileLocationSchema.FromPath(name=f"{name}Location", fullpath=location)
        elif isinstance(location, str):
            self._location = FileLocationSchema.FromPath(name=f"{name}Location", fullpath=Path(location))
        else:
            self._location = self._parseLocation(unparsed_elements=unparsed_elements)
        self._credential  : FileCredential     = file_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=unparsed_elements)

    @property
    def Filename(self) -> str:
        """The name of the file targeted by the FileStoreConfig

        :return: _description_
        :rtype: str
        """
        return self._location.Filename

    @property
    def Folder(self) -> Path:
        """The path to the folder containing the data store file

        :return: The path to the folder containing the data store file.
        :rtype: Path
        """
        return self._location.Folder

    @property
    def FileExtension(self) -> str:
        return self.Filename.rsplit(".", maxsplit=1)[-1]

    @property
    def Filepath(self) -> str | Path:
        """The full path to the file targeted by the FileStoreConfig

        :return: _description_
        :rtype: str | Path
        """
        return self.Location.Filepath

    @property
    def Location(self) -> FileLocationSchema:
        return self._location

    @property
    def Credential(self) -> PasswordCredential | EmptyCredential:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = "FILE SOURCE"
        ret_val = f"{self.Name} : Folder=_{self.Folder}_, File=_{self.Filename}_"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.Name}:{self.Filepath}"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "FileStoreConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: FileStoreConfig
        """
        return FileStoreConfig(name=name, location=None, file_credential=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "FileStoreConfig":
        return FileStoreConfig(
            name="DefaultFileStoreConfig",
            location=cls._DEFAULT_LOCATION,
            file_credential=FileStoreConfig._DEFAULT_CREDENTIAL,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocation(unparsed_elements:Map) -> FileLocationSchema:
        return FileLocationSchema.FromDict(name="FileStoreLocation", unparsed_elements=unparsed_elements)

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> FileCredential:
        ret_val : FileCredential
        _cred_elements = FileStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["FILE_CREDENTIAL"],
            to_type=dict,
            default_value=None,
            remove_target=True
        )
        if _cred_elements:
            ret_val = PasswordCredential.FromDict(name="FileStoreCredential", unparsed_elements=_cred_elements)
        else:
            ret_val = FileStoreConfig._DEFAULT_CREDENTIAL
        return ret_val

    # *** PRIVATE METHODS ***
