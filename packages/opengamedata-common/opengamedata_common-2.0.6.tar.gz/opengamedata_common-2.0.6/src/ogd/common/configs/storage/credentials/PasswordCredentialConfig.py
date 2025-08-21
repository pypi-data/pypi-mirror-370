# import standard libraries
from typing import Dict, Final, List, Optional, Self
# import local files
from ogd.common.configs.storage.credentials.CredentialConfig import CredentialConfig
from ogd.common.utils.typing import Map


class PasswordCredential(CredentialConfig):
    """Dumb struct to contain data pertaining to credentials for accessing a data source.

    In general, a credential can have a key, or a user-password combination.
    """
    _DEFAULT_USER : Final[str]  = "DEFAULT USER"
    _DEFAULT_PASS : Final[None] = None

    def __init__(self, name:str, username:Optional[str], password:Optional[str], other_elements:Optional[Map]=None):
        """Constructor for the `IteratedConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "user" : "username",
            "pass" : "password",
        },
        ```

        :param name: _description_
        :type name: str
        :param username: _description_
        :type username: str
        :param password: _description_
        :type password: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        fallbacks : Map = other_elements or {}
        self._user = username or self._parseUser(unparsed_elements=fallbacks)
        self._pass = password or self._parsePass(unparsed_elements=fallbacks)
        super().__init__(name=name, other_elements=fallbacks)

    @property
    def User(self) -> str:
        return self._user

    @property
    def Pass(self) -> Optional[str]:
        return self._pass

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"User : `{self.User}`\nPass: `*** HIDDEN ***`"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "PasswordCredential":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: PasswordCredential
        """
        _user = cls._parseUser(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
        _pass = cls._parsePass(unparsed_elements=unparsed_elements, key_overrides=key_overrides, default_override=default_override)
        return PasswordCredential(name=name, username=_user, password=_pass, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "PasswordCredential":
        return PasswordCredential(
            name="DefaultPasswordCredential",
            username=cls._DEFAULT_USER,
            password=cls._DEFAULT_PASS,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseUser(unparsed_elements:Map,
                   key_overrides:Optional[Dict[str, str]]=None,
                   default_override:Optional["PasswordCredential"]=None) -> str:
        default_keys : List[str] = ["USER"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys \
                                if key_overrides else default_keys
        default_value : Optional[str] = default_override.User if default_override else PasswordCredential._DEFAULT_USER

        return PasswordCredential.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_value,
            remove_target=True
        )

    @staticmethod
    def _parsePass(unparsed_elements:Map,
                   key_overrides:Optional[Dict[str, str]]=None,
                   default_override:Optional["PasswordCredential"]=None) -> str:
        default_keys : List[str] = ["PASS", "PASSWORD", "PW"]
        search_keys  : List[str] = [key_overrides[key] for key in default_keys if key in key_overrides] + default_keys \
                                if key_overrides else default_keys
        default_value : Optional[str] = default_override.Pass if default_override else PasswordCredential._DEFAULT_PASS

        return PasswordCredential.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=search_keys,
            to_type=str,
            default_value=default_value,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
