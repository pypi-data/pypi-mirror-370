"""ElementMappingType Module
"""

# import standard libraries
from enum import IntEnum

class ElementMappingType(IntEnum):
    """Enum representing the different kinds of column-element mappings in TableConfigs.

    Namely:

    * Dictionary
    * List
    * Single
    """
    SINGLE = 1
    LIST = 2
    DICT = 3

    def __str__(self):
        return self.name

    @classmethod
    def FromString(cls, string:str) -> "ElementMappingType":
        match string.upper():
            case "SINGLE":
                return cls.SINGLE
            case "LIST":
                return cls.LIST
            case "DICT" | "DICTIONARY":
                return cls.DICT
            case _:
                raise ValueError(f"Unrecognized element mapping type {string}!")
