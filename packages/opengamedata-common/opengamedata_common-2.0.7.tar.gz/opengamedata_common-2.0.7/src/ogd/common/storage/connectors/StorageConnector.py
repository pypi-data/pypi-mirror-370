"""StorageConnector Module
"""

# import standard libraries
import abc
import logging

# import local files
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.utils.Logger import Logger

class StorageConnector(abc.ABC):
    """Base class for all interfaces and outerfaces.
    Ensures each inter/outerface can be opened and closed, like most system resources.

    All subclasses must implement the `_open` and `_close` functions.
    """

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def StoreConfig(self) -> DataStoreConfig:
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the StoreConfig function!")

    @abc.abstractmethod
    def _open(self, writeable:bool=True) -> bool:
        """Private implementation of the logic for opening a connection to a storage resource

        :return: True if the connection was successful, otherwise False.
        :rtype: bool
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the _open function!")

    @abc.abstractmethod
    def _close(self) -> bool:
        """Private implementation of the logic for closing a connection to a storage resource

        :return: True if the connection was closed successfully, otherwise False.
        :rtype: bool
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the _close function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self):
        self._is_open : bool = False

    def __del__(self):
        self.Close()

    @property
    def IsOpen(self) -> bool:
        """Property to indicate whether a connection with the storage resource is open or not.

        :return: True if there is an open connection to the storage resource, otherwise false.
        :rtype: bool
        """
        return True if self._is_open else False

    @property
    def ResourceName(self) -> str:
        return self.StoreConfig.Location.Location

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Open(self, writeable:bool=True, force_reopen:bool = False) -> bool:
        """Function to open the connection to a storage resource.

        If the resource was already open, this function (by default) does nothing.
        The type of resource is determined by the implementation of a given interface/outerface class.

        :param force_reopen: Force a re-open of the storage resource, if it was already open. Defaults to False
        :type force_reopen: bool, optional
        :return: True if the resource was successfully opened (or was already open), otherwise False.
        :rtype: bool
        """
        if not self.IsOpen:
            self._is_open = self._open(writeable=writeable)
        elif force_reopen:
            self.Close()
            self._is_open = self._open(writeable=writeable)
            Logger.Log(f"Successfully force-reopened {self.__class__}", logging.INFO)
        return self.IsOpen

    def Close(self, force_close:bool = False) -> bool:
        """Function to close the connection to a storage resource.

        If there was no open connection, this function (by default) does nothing.

        :param force_close: Force an attempt to close the resource, even if there is not a known open connection. Defaults to False
        :type force_close: bool, optional
        :return: True if the resource was successfully closed (or was not open to begin with), otherwise False.
        :rtype: bool
        """
        ret_val = True
        if self.IsOpen:
            ret_val = self._close()
        elif force_close:
            try:
                self._close()
            except Exception as err:
                Logger.Log(f"Encountered an error while force-closing {self.__class__}:\n{err}", logging.WARNING)
            else:
                Logger.Log(f"Successfully force-closed {self.__class__}", logging.INFO)

        return ret_val

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
