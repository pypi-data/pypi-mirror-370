import logging
import os
from google.cloud import bigquery
from typing import Final, Optional
# import locals
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

class BigQueryConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:BigQueryConfig):
        self._config = config
        self._client : Optional[bigquery.Client] = None
        super().__init__()

    @property
    def Client(self) -> Optional[bigquery.Client]:
        return self._client

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def StoreConfig(self) -> BigQueryConfig:
        return self._config

    def _open(self, writeable:bool=True) -> bool:
        if not self._is_open:
            if "GITHUB_ACTIONS" in os.environ:
                self._client = bigquery.Client()
            else:
                _keypath = str(self.StoreConfig.Credential.Filepath)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _keypath or "NO CREDENTIAL CONFIGURED!"
                self._client = bigquery.Client()
            if self._client != None:
                self._is_open = True
                Logger.Log("Connected to BigQuery database.", logging.DEBUG)
                return True
            else:
                Logger.Log("Could not connect to BigQuery Database.", logging.WARNING)
                return False
        else:
            return True

    def _close(self) -> bool:
        if self._client is not None:
            self._client.close()
            Logger.Log("Closed connection to BigQuery.", logging.DEBUG)
        else:
            Logger.Log("No BigQuery client to close.", logging.WARNING)
        self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    @property
    def IsOpen(self) -> bool:
        """Overridden version of IsOpen function, checks that BigQueryInterface client has been initialized.

        :return: True if the interface is open, else False
        :rtype: bool
        """
        return True if (super().IsOpen and self._client is not None) else False

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
