# import standard libraries
from typing import Dict, Final, Optional, Self
from urllib.parse import ParseResult
# import local files
from ogd.common.configs.storage.credentials.PasswordCredentialConfig import PasswordCredential
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.schemas.locations.URLLocationSchema import URLLocationSchema
from ogd.common.utils.typing import Map

class SSHConfig(DataStoreConfig):
    _STORE_TYPE = "SSH"
    _DEFAULT_LOCATION: Final[URLLocationSchema] = URLLocationSchema(
        name="DefaultSSHLocation",
        url=ParseResult(
            scheme="http",
            netloc="127.0.0.1:22",
            path="", params="", query="", fragment=""
        )
    )
    _DEFAULT_CREDENTIAL: Final[PasswordCredential] = PasswordCredential.Default()

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 location:Optional[URLLocationSchema],
                 ssh_credential:Optional[PasswordCredential],
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `SSHConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "SSH_HOST": "ogd-logger.fielddaylab.wisc.edu",
            "SSH_USER": "username",
            "SSH_PASS": "password",
            "SSH_PORT": 22
        },
        ```

        :param name: _description_
        :type name: str
        :param location: _description_
        :type location: Optional[URLLocationSchema]
        :param ssh_credential: _description_
        :type ssh_credential: Optional[PasswordCredential]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._location   : URLLocationSchema  = location       or self._parseLocation(unparsed_elements=unparsed_elements)
        self._credential : PasswordCredential = ssh_credential or self._parseCredential(unparsed_elements=unparsed_elements)
        super().__init__(name=name, store_type=self._STORE_TYPE, other_elements=other_elements)

    @property
    def Host(self) -> Optional[str]:
        return self._location.Host

    @property
    def User(self) -> str:
        return self._credential.User

    @property
    def Pass(self) -> Optional[str]:
        return self._credential.Pass

    @property
    def Port(self) -> Optional[int]:
        return self._location.Port

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Location(self) -> URLLocationSchema:
        return self._location

    @property
    def Credential(self) -> PasswordCredential:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : `{self.AsConnectionInfo}`"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str

        ret_val = f"{self.User}@{self.Host}:{self.Port}"
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "SSHConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :return: _description_
        :rtype: SSHConfig
        """
        return SSHConfig(name=name, location=None, ssh_credential=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "SSHConfig":
        return SSHConfig(
            name="DefaultSSHConfig",
            location=SSHConfig._DEFAULT_LOCATION,
            ssh_credential=SSHConfig._DEFAULT_CREDENTIAL,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseLocation(unparsed_elements:Map) -> URLLocationSchema:
        _overrides = {"host":"SSH_HOST", "port":"SSH_PORT"}

        return URLLocationSchema.FromDict(
            name              =  "SSHHostLocation",
            unparsed_elements = unparsed_elements,
            key_overrides     = _overrides
        )

    @staticmethod
    def _parseCredential(unparsed_elements:Map) -> PasswordCredential:
        _overrides = { "USER":"SSH_USER", "PASS":"SSH_PASS", "PW":"SSH_PW" }

        return PasswordCredential.FromDict(
            name="SSHCredential",
            unparsed_elements=unparsed_elements,
            key_overrides=_overrides
        )

    # *** PRIVATE METHODS ***
