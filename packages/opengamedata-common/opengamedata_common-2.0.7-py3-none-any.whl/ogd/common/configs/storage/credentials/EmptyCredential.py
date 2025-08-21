# import standard libraries
from typing import Any, Dict, Optional, Self
# import local files
from ogd.common.configs.Config import Config
from ogd.common.utils.typing import Map

class EmptyCredential(Config):
    """Dumb struct to contain data pertaining to credentials for accessing a data source.

    In general, a credential can have a key, or a user-password combination.
    """
    # @overload
    # def __init__(self, name:str, other_elements:Dict[str, Any]): ...

    def __init__(self, name:str, other_elements:Dict[str, Any] | Any):
        super().__init__(name=name, other_elements=other_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self._name} Empty Credential"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "EmptyCredential":
        """Function to generate an EmptyCredential from a dictionary mapping string keys to values.

        Technically,  it doesn't matter what goes in, because an EmptyCredential is always empty.

        :param name: The name to be given to the credential configuration
        :type name: str
        :param unparsed_elements: A dictionary of all elements that are meant to be parsed by EmptyCredential and its superclasses.
        :type unparsed_elements: Map
        :return: A new EmptyCredential
        :rtype: EmptyCredential
        """
        return EmptyCredential(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "EmptyCredential":
        return EmptyCredential(
            name="DefaultEmptyCredential",
            other_elements={}
        )
