# import standard libraries
from typing import Dict, Final, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.typing import Map

class ColumnSchema(Schema):
    _DEFAULT_READABLE    : Final[str] = "Default Column Schema Name"
    _DEFAULT_VALUE_TYPE  : Final[str] = "TYPE NOT GIVEN"
    _DEFAULT_DESCRIPTION : Final[str] = "NO DESCRIPTION GIVEN"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, readable:Optional[str], value_type:Optional[str], description:Optional[str], other_elements:Optional[Map]=None):
        """Constructor for the `ColumnSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "name": "column_name",
            "readable": "Human-Readable Column Name",
            "description": "Description of the column, what its contents represent.",
            "type": "str"
        },
        ```

        :param name: _description_
        :type name: str
        :param readable: _description_
        :type readable: Optional[str]
        :param value_type: _description_
        :type value_type: Optional[str]
        :param description: _description_
        :type description: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._readable    : str = readable    or self._parseReadable(unparsed_elements=unparsed_elements)
        self._value_type  : str = value_type  or self._parseValueType(unparsed_elements=unparsed_elements)
        self._description : str = description or self._parseDescription(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    def __str__(self):
        return self.Name

    def __repr__(self):
        return self.Name

    def __eq__(self, other:"ColumnSchema"):
        if not isinstance(other, ColumnSchema):
            if isinstance(other, dict):
                return self == ColumnSchema.FromDict(name=self.Name, unparsed_elements=other)
            return False
        return self.Name         == other.Name \
           and self.ReadableName == other.ReadableName \
           and self.ValueType    == other.ValueType \
           and self.Description  == other.Description

    @property
    def ReadableName(self) -> str:
        return self._name

    @property
    def Description(self) -> str:
        return self._description

    @property
    def ValueType(self) -> str:
        return self._value_type

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val = f"**{self.Name}** : *{self.ValueType}* - {self.ReadableName}, {self.Description}  "

        if len(self.NonStandardElements) > 0:
            other_elems = [f"{key}: {val}" for key,val in self.NonStandardElements]
            ret_val += f"\n    Other Elements: {', '.join(other_elems)}"

        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "ColumnSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: ColumnSchema
        """
        _name        : str = cls._parseName(name=name, unparsed_elements=unparsed_elements)

        return ColumnSchema(name=_name, readable=None, value_type=None, description=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "ColumnSchema":
        return ColumnSchema(
            name="DefaultColumnSchema",
            readable=cls._DEFAULT_READABLE,
            value_type=cls._DEFAULT_VALUE_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
    
    @staticmethod
    def _parseName(name:str, unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["name"],
            to_type=str,
            default_value=name,
            remove_target=True
        )
    
    @staticmethod
    def _parseReadable(unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["readable", "human_readable"],
            to_type=str,
            default_value=ColumnSchema._DEFAULT_READABLE,
            remove_target=True
        )
    
    @staticmethod
    def _parseDescription(unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=ColumnSchema._DEFAULT_DESCRIPTION,
            remove_target=True
        )
    
    @staticmethod
    def _parseValueType(unparsed_elements:Map):
        return ColumnSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["type"],
            to_type=str,
            default_value=ColumnSchema._DEFAULT_VALUE_TYPE,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
