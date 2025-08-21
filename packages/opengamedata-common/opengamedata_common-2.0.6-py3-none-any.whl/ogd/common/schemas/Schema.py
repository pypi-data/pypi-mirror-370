# import standard libraries
import abc
import logging
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, Final, List, Optional, Self, Type
# import local files
from ogd.common.utils.typing import conversions, Map
from ogd.common.utils import fileio
from ogd.common.utils.Logger import Logger

class Schema(abc.ABC):

    _DEFAULT_SCHEMA_NAME :Final[str] = "DefaultSchemaName"

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def AsMarkdown(self) -> str:
        """Gets a markdown-formatted representation of the schema.

        :return: A markdown-formatted representation of the schema.
        :rtype: str
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the AsMarkdown function!")

    @classmethod
    @abc.abstractmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> Self:
        """_summary_

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Map
        :param logger: _description_, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: _description_
        :rtype: Schema
        """
        raise NotImplementedError(f"{cls} has not implemented the _fromDict function!")

    @classmethod
    @abc.abstractmethod
    def Default(cls) -> Self:
        """Property to get an instance of the Schema with default member values.

        Note that these defaults may or may not be a usable configuration.
        :return: A schema with default member values.
        :rtype: Self
        """
        raise NotImplementedError(f"{cls} has not implemented the Default function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Optional[Map]=None):
        self._name : str           = name or Schema._DEFAULT_SCHEMA_NAME
        self._other_elements : Map = other_elements or {}

        if len(self._other_elements.keys()) > 0:
            Logger.Log(f"Schema for {self.Name} contained nonstandard elements {self.NonStandardElementNames}", logging.DEBUG)

    def __str__(self):
        return f"{type(self).__name__}[{self.Name}]"

    def __repr__(self):
        return f"{type(self).__name__}[{self.Name}]"

    @property
    def Name(self) -> str:
        """Gets the name of the specific schema represented by the class instance.

        :return: The name of the specific schema represented by the class instance.
        :rtype: str
        """
        return self._name

    @property
    def NonStandardElements(self) -> Map:
        """Gets a sub-dictionary of any non-standard schema elements found in the source dictionary for the given schema instance.

        :return: A dictionary of any non-standard schema elements found in the source dictionary for the given schema instance.
        :rtype: Map
        """
        return self._other_elements

    @property
    def NonStandardElementNames(self) -> List[str]:
        """Gets a list of names of non-standard schema elements found in the source dictionary for the given schema instance.

        :return: A list of names of non-standard schema elements found in the source dictionary for the given schema instance.
        :rtype: List[str]
        """
        return list(self._other_elements.keys())

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:Path | str, search_templates:bool=False) -> Self:
        """_summary_

        :param schema_name: _description_
        :type schema_name: str
        :param schema_path: _description_
        :type schema_path: Path
        :param search_templates: _description_, defaults to False
        :type search_templates: bool, optional
        :return: _description_
        :rtype: _type_
        """
        return cls._fromFile(schema_name=schema_name, schema_path=schema_path)

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> Self:
        """Function to create an instance of the given Schema subclass, from data in a Map (Dict[str, Any])

        :param name: The name of the instance.
        :type name: str
        :param unparsed_elements: The raw dictionary-formatted data that will make up the content of the instance.
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Schema
        """
        if not isinstance(unparsed_elements, dict):
            unparsed_elements   = {}
            _msg = f"For {name} {cls.__name__}, unparsed_elements was not a dict, defaulting to empty dict"
            Logger.Log(_msg, logging.WARN)

        return cls._fromDict(name=name, unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)

    @classmethod
    def ParseElement(cls, unparsed_elements:Map, valid_keys:List[str], to_type:Type | List[Type], default_value:Any, remove_target:bool=False, optional_element:bool=False, schema_name:Optional[str]=None) -> Any:
        """Function to parse an individual element from a dictionary, given a list of possible keys for the element, and a desired type.

        :param all_elements: A dictionary containing all elements to search through
        :type all_elements: Map
        :param valid_keys: A list of which keys to search for to find the desired element. This function will choose they first key in the list that appears in the `all_elements` dictionary.
        :type valid_keys: List[str]
        :param value_type: The desired type of value to return, or list of valid types. If a list, the returned value will either be the first type in the list of which the raw value is an instance, or a parsed instance of the first item in the list.
        :type value_type: Type | List[Type]
        :param default_value: A default value to return, if a valid value could not be parsed.
        :type default_value: Any
        :param remove_target: Whether to remove the target element, if found; defaults to False.
        :type remove_target: bool, optional
        :param optional_element: Whether the element being parsed should be considered optional, if True then no warning will be given if the element is not found. Defaults to False
        :type optional_element: bool, optional
        :return: The targeted value, with given type; otherwise the given default value.
        :rtype: Any
        """
        ret_val : Any = default_value
        decased_elements = {key.upper() : (key, val) for key,val in unparsed_elements.items()}

        found = False
        for _name in valid_keys:
            name = _name.upper()
            if name in decased_elements:
                value = decased_elements[name][1]
                if remove_target:
                    original_key = decased_elements[name][0]
                    del unparsed_elements[original_key]
                ret_val = conversions.ConvertToType(value=value, to_type=to_type, name=f"{cls.__name__} element {name}")
                found = True
                break
        if not found and not optional_element:
            _title = f"'{schema_name}'" if schema_name else "source"
            _msg = f"{cls.__name__} {_title} does not have a '{valid_keys[0]}' element; defaulting to {valid_keys[0]}={default_value}"
            Logger.Log(_msg, logging.WARN)

        # if we got empty value back from conversion, use default instead, that's more likely what we want.
        return ret_val or default_value

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @classmethod
    def _fromFile(cls, schema_name:str, schema_path:Path | str, search_templates:bool=False) -> Self:
        ret_val : Schema
        schema_file_name : str = f"{schema_name}.json" if not schema_name.lower().endswith(".json") else schema_name
        _schema_path = Path(schema_path)
            
        # 2. try to actually load the contents of the file.
        try:
            schema_contents = fileio.loadJSONFile(filename=schema_file_name, path=_schema_path)
        except (ModuleNotFoundError, FileNotFoundError) as err:
            # Case 1: Didn't find module, nothing else to try
            if isinstance(err, ModuleNotFoundError):
                Logger.Log(f"Unable to load schema at {_schema_path / schema_file_name}, module ({schema_path}) does not exist! Using default schema instead", logging.ERROR, depth=1)
                ret_val = cls.Default()
            # Case 2a: Didn't find file, search for template
            elif search_templates:
                Logger.Log(f"Unable to load schema at {_schema_path / schema_file_name}, {schema_name} does not exist! Trying to load from json template instead...", logging.WARNING, depth=1)
                ret_val = cls._schemaFromTemplate(schema_path=_schema_path, schema_name=schema_file_name)
            # Case 2b: Didn't find file, don't search for template
            else:
                Logger.Log(f"Unable to load schema at {_schema_path / schema_file_name}, {schema_file_name} does not exist! Using default schema instead", logging.ERROR, depth=1)
                ret_val = cls.Default()
        else:
            if schema_contents is None:
                Logger.Log(f"Could not load schema at {_schema_path / schema_file_name}, the file was empty! Using default schema instead", logging.ERROR, depth=1)
                ret_val = cls.Default()
            else:
                ret_val = cls._fromDict(name=schema_name, unparsed_elements=schema_contents)

        return ret_val

    @classmethod
    def _schemaFromTemplate(cls, schema_path:Path, schema_name:str) -> Self:
        template_name = schema_name + ".template"
        try:
            template_contents = fileio.loadJSONFile(filename=template_name, path=schema_path, autocorrect_extension=False)
        except FileNotFoundError:
            _msg = f"Unable to load schema template at {schema_path / template_name}, {template_name} does not exist!."
            Logger.Log(_msg, logging.WARN, depth=1)
            print(f"(via print) {_msg}.")
        else:
            if template_contents is not None:
                Logger.Log(f"Successfully loaded {schema_name} from template.", logging.INFO, depth=1)
                Logger.Log(f"Trying to copy {schema_name} from template, for future use...", logging.DEBUG, depth=2)
                template = schema_path / template_name
                try:
                    copyfile(template, schema_path / schema_name)
                except Exception as cp_err:
                    _msg = f"Could not make a copy of {schema_name} from template, a {type(cp_err)} error occurred:\n{cp_err}"
                    Logger.Log(         _msg, logging.WARN, depth=1)
                    print(f"(via print) {_msg}")
                else:
                    Logger.Log(f"Successfully copied {schema_name} from template.", logging.DEBUG, depth=2)
        return cls._fromDict(name=schema_name, unparsed_elements=template_contents)
    # *** PRIVATE METHODS ***
