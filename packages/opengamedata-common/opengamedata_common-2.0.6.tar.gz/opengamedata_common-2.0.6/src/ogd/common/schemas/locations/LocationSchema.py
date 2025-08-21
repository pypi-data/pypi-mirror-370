## import standard libraries
import abc
from typing import Optional
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.typing import Map

## @class LocationSchema
class LocationSchema(Schema):

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Location(self) -> str:
        """Gets a string representation of the full location.

        :return: A string representation of the full location.
        :rtype: str
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Location function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Optional[Map]=None):
        super().__init__(name=name, other_elements=other_elements)

    def __str__(self) -> str:
        return self.Location

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
