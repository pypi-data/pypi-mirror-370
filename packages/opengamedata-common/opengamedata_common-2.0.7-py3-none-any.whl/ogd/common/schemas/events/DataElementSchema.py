# import standard libraries
import logging
from typing import Dict, Final, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class DataElementSchema(Schema):
    """
    Dumb struct to contain a specification of a data element from the EventData, GameState, or UserData attributes of an Event.
    """

    _DEFAULT_TYPE        : Final[str]  = "str"
    _DEFAULT_DESCRIPTION : Final[str]  = "Default data element generated the DataElementSchema class. Does not represent actual data."
    _DEFAULT_DETAILS     : Final[None] = None

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, element_type:Optional[str], description:Optional[str], details:Optional[Dict[str, str]], other_elements:Optional[Map]=None):
        """Constructor for the `DataElementSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        In the format below, `details` is an optional key.

        Expected format:

        ```
        {
               "type": "List[Dict]",
               "details": {
                  "name": "str",
                  "price": "int"
               },
               "description": "A description of what the data element means or represents. In this example, some kind of a pricing menu."
        },
        ```

        :param name: _description_
        :type name: str
        :param element_type: _description_
        :type element_type: Optional[str]
        :param description: _description_
        :type description: Optional[str]
        :param details: _description_
        :type details: Optional[Dict[str, str]]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._type        : str                      = element_type or self._parseElementType(unparsed_elements=unparsed_elements)
        self._description : str                      = description  or self._parseDescription(unparsed_elements=unparsed_elements)
        self._details     : Optional[Dict[str, str]] = details      or self._parseDetails(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def ElementType(self) -> str:
        return self._type

    @property
    def Description(self) -> str:
        return self._description

    @property
    def Details(self) -> Optional[Dict[str, str]]:
        return self._details

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ElementType}*, {self.Description}"
        if self.Details is not None:
            detail_markdowns = [f"    - **{name}** - {desc}  " for name,desc in self.Details.items()]
            detail_joined = '\n'.join(detail_markdowns)
            ret_val += f"  \n  Details:  \n{detail_joined}"
        return ret_val

    @property
    def AsMarkdownRow(self) -> str:
        ret_val : str = f"| {self.Name} | {self.ElementType} | {self.Description} |"
        if self.Details is not None:
            detail_markdowns = [f"**{name}** : {desc}" for name,desc in self.Details.items()]
            ret_val += ', '.join(detail_markdowns)
        ret_val += " |"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DataElementSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DataElementSchema
        """
        return DataElementSchema(name=name, element_type=None, description=None, details=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "DataElementSchema":
        return DataElementSchema(
            name="DefaultDataElementSchema",
            element_type=cls._DEFAULT_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            details=cls._DEFAULT_DETAILS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "DataElementSchema":
        """Override of base class function to create an instance of DataElementSchema, from data in a Map (Dict[str, Any])

        :param name: The name of the instance.
        :type name: str
        :param unparsed_elements: The raw dictionary-formatted data that will make up the content of the instance.
        :type unparsed_elements: Map
        :return: _description_
        :rtype: Schema
        """
        if not isinstance(unparsed_elements, dict):
            if isinstance(unparsed_elements, str):
                unparsed_elements = { 'description' : unparsed_elements }
                Logger.Log(f"For EventDataElement config of `{name}`, unparsed_elements was a str, probably in legacy format. Defaulting to all_elements = {'{'} description : {unparsed_elements['description']} {'}'}", logging.WARN)
            else:
                unparsed_elements = {}
                Logger.Log(f"For EventDataElement config of `{name}`, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)

        return cls._fromDict(name=name, unparsed_elements=unparsed_elements)

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseElementType(unparsed_elements:Map) -> str:
        return DataElementSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["type"],
            to_type=str,
            default_value=DataElementSchema._DEFAULT_TYPE,
            remove_target=True
        )
    
    @staticmethod
    def _parseDescription(unparsed_elements:Map) -> str:
        return DataElementSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=DataElementSchema._DEFAULT_DESCRIPTION,
            remove_target=True
        )

    @staticmethod
    def _parseDetails(unparsed_elements:Map):
        ret_val : Dict[str, str] = {}

        details = DataElementSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["details"],
            to_type=dict,
            default_value=DataElementSchema._DEFAULT_DETAILS,
            remove_target=True
        )
        if isinstance(details, dict):
            for key in details.keys():
                if not isinstance(key, str):
                    _key = str(key)
                    Logger.Log(f"EventDataElement detail key was unexpected type {type(key)}, defaulting to str(key) == {_key}", logging.WARN)
                else:
                    _key = key
                ret_val[_key] = DataElementSchema.ParseElement(
                    unparsed_elements=details,
                    valid_keys=[_key],
                    to_type=str,
                    default_value="UNKNOWN TYPE",
                    remove_target=False
                )
        else:
            ret_val = details
        return ret_val

    # *** PRIVATE METHODS ***

