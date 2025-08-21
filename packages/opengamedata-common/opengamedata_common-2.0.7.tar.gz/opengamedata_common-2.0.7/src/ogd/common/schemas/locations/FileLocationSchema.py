## import standard libraries
import logging
from pathlib import Path
from typing import Dict, Final, List, Optional, Self, Tuple
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class FileLocationSchema
class FileLocationSchema(LocationSchema):
    """Class to encode the location of data within a database resource.

    Generally, the location of a database system would be a URLLocation,
    while DatabaseLocation refers to the location of a specific database or table within such a system.
    """

    _DEFAULT_PATH     : Final[Path] = Path("./")
    _DEFAULT_FILENAME : Final[str]  = "file.tsv"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, folder_path:Path | str, filename:str, other_elements:Optional[Map]=None):
        """Constructor for the `FileLocationSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "folder" : "path/to/folder",
            "filename" : "file.ext"
        },
        ```

        :param name: _description_
        :type name: str
        :param folder_path: _description_
        :type folder_path: Path | str
        :param filename: _description_
        :type filename: str
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._folder_path  : Path
        self._filename     : str


        if isinstance(folder_path, str):
            folder_path = Path(folder_path)
        # 1. If we got both params, then just use them.
        if folder_path and filename:
            self._folder_path = folder_path
            self._filename    = filename
        # 2. Otherwise, try to get as full path as first try. If it return something, then we've got what we need.
        else:
            parsed_path = self._parsePath(unparsed_elements=unparsed_elements)
            if parsed_path:
                self._folder_path = parsed_path[0]
                self._filename    = parsed_path[1]
        # 3. If there wasn't a full path, then we move on to just parse folder and filename from dict directly.
            else:
                self._folder_path = folder_path or self._parsePath(unparsed_elements=unparsed_elements)
                self._filename    = filename    or self._parseFilename(unparsed_elements=unparsed_elements)
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Folder(self) -> Path:
        """The path of the folder containing the file located by this schema.

        :return: The name of the database where the table is located
        :rtype: str
        """
        return self._folder_path

    @property
    def Filename(self) -> str:
        """The name of the file indicated by the FileLocationSchema

        :return: _description_
        :rtype: str
        """
        return self._filename

    @property
    def Filepath(self) -> Path:
        """The full path to the file indicated by the FileLocationSchema

        :return: _description_
        :rtype: Path
        """
        return self.Folder / self.Filename

    @property
    def FileExists(self):
        return self.Filepath.is_file()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return str(self.Filepath)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: {self.Folder / self.Filename}"
        return ret_val

    @classmethod
    def Default(cls) -> "FileLocationSchema":
        return FileLocationSchema(
            name="DefaultFileLocation",
            folder_path=cls._DEFAULT_PATH,
            filename=cls._DEFAULT_FILENAME,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "FileLocationSchema":
        """Create a DatabaseLocationSchema from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :param key_overrides: _description_, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :param default_override: _description_, defaults to None
        :type default_override: Optional[Self], optional
        :return: _description_
        :rtype: FileLocationSchema
        """
        _folder_path : Path
        _filename    : str

        # 2. Otherwise, try to get as full path as first try. If it return something, then we've got what we need.
        parsed_path = cls._parsePath(unparsed_elements=unparsed_elements, key_overrides=key_overrides)
        _used = {"path"}
        if parsed_path:
            _folder_path = parsed_path[0]
            _filename    = parsed_path[1]
        # 3. If there wasn't a full path, then we move on to just parse folder and filename from dict directly.
        else:
            _folder_path = cls._parseFolderPath(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
            _filename    = cls._parseFilename(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
            # if we didn't find a folder, but the file has a '/' in it, we should be able to get file separate from path.
            if _folder_path is None and _filename is not None and "/" in _filename:
                _full_path = Path(_filename)
                _folder_path = _full_path.parent
                _filename    = _full_path.name
            _used = _used.union({"folder", "filename", "file"})

        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return FileLocationSchema(name=name, folder_path=_folder_path, filename=_filename, other_elements=_leftovers)

    # *** PUBLIC STATICS ***

    @staticmethod
    def FromString(name:str, fullpath:str) -> "FileLocationSchema":
        return FileLocationSchema.FromPath(name=name, fullpath=Path(fullpath))

    @staticmethod
    def FromPath(name:str, fullpath:Path) -> "FileLocationSchema":
        if fullpath:
            # if not fullpath.is_file():
            #     raise ValueError(f"FileLocationSchema was given a path '{fullpath}' which is not a valid file!", logging.WARNING)
            if not "." in fullpath.name:
                Logger.Log(f"FileLocationSchema was given a path '{fullpath}' which does not include a file extension!", logging.WARNING)
            return FileLocationSchema(name=name, folder_path=fullpath.parent, filename=fullpath.name)

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parsePath(unparsed_elements:Map,
                   key_overrides:Optional[Dict[str, str]]=None) -> Optional[Tuple[Path, str]]:
        """Function to parse a full path into a folder and filename

        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Optional[str]
        """
        ret_val = None

        default_keys : List[str] = ["path"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys

        raw_path = FileLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=Path,
            default_value=None,
            remove_target=True
        )
        if raw_path:
            ret_val = (raw_path.parent, raw_path.name)
            if not raw_path.is_file():
                Logger.Log(f"FileLocationSchema was given a path '{raw_path}' which is not a valid file!", logging.WARNING)
            elif not "." in raw_path.name:
                Logger.Log(f"FileLocationSchema was given a path '{raw_path}' which does not include a file extension!", logging.WARNING)

        return ret_val

    @staticmethod
    def _parseFolderPath(unparsed_elements:Map,
                         key_overrides:Optional[Dict[str, str]]=None,
                         default_override:Optional["FileLocationSchema"]=None) -> Path:
        default_keys : List[str] = ["folder", "path"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_value : Path = default_override.Folder if default_override else FileLocationSchema._DEFAULT_PATH

        return FileLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=Path,
            default_value=default_value,
            remove_target=True
        )

    @staticmethod
    def _parseFilename(unparsed_elements:Map,
                       key_overrides:Optional[Dict[str, str]]=None,
                       default_override:Optional["FileLocationSchema"]=None) -> str:
        default_keys : List[str] = ["filename", "file"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys if key_overrides else default_keys
        default_value : str = default_override.Filename if default_override else FileLocationSchema._DEFAULT_FILENAME

        return FileLocationSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_value,
            remove_target=True
        )
