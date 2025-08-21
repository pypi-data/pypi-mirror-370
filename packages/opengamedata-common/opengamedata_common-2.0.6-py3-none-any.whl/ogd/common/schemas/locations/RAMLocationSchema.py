## import standard libraries
import logging
from pathlib import Path
from typing import Dict, Final, List, Optional, Self, Tuple
## import local files
from ogd.common.schemas.locations.LocationSchema import LocationSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

## @class FileLocationSchema
class RAMLocationSchema(LocationSchema):
    """Class to encode the fact that some resource is contained in an object in RAM.

    Effectively just a dummy to make such things easier to deal with, config-wise.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str):
        """Constructor for the `RAMLocationSchema` class.
        """

        super().__init__(name=name, other_elements=None)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> str:
        return "Object in RAM"

    @property
    def AsMarkdown(self) -> str:
        return self.Location

    @classmethod
    def Default(cls) -> "RAMLocationSchema":
        return RAMLocationSchema(
            name="DefaultRAMLocation",
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "RAMLocationSchema":
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
        return RAMLocationSchema(name=name)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
