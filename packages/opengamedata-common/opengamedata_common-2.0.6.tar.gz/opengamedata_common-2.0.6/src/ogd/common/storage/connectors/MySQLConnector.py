from datetime import datetime
import logging
import traceback
from typing import Final, Optional
# 3rd-party imports
import sshtunnel
from mysql.connector import connection, cursor
# import locals
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Pair

AQUALAB_MIN_VERSION : Final[float] = 6.2

class MySQLConnector(StorageConnector):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:MySQLConfig):
        self._config = config
        self._tunnel     : Optional[sshtunnel.SSHTunnelForwarder] = None
        self._connection : Optional[connection.MySQLConnection] = None
        self._cursor     : Optional[cursor.MySQLCursor] = None
        super().__init__()

    @property
    def Connection(self) -> Optional[connection.MySQLConnection]:
        return self._connection

    @property
    def Cursor(self) -> Optional[cursor.MySQLCursor]:
        return self._cursor

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def StoreConfig(self) -> MySQLConfig:
        return self._config

    def _open(self, writeable:bool=True) -> bool:
        """
        Function to set up a connection to a database, via an ssh tunnel if available.

        :param db_settings: A dictionary mapping names of database parameters to values.
        :type db_settings: Dict[str,Any]
        :param ssh_settings: A dictionary mapping names of ssh parameters to values, or None if no ssh connection is desired., defaults to None
        :type ssh_settings: Optional[Dict[str,Any]], optional
        :return: A tuple consisting of the tunnel and database connection, respectively.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        Logger.Log("Preparing database connection...", logging.DEBUG)
        if self.StoreConfig is not None and isinstance(self.StoreConfig, MySQLConfig):
            start = datetime.now()
            self._connection, self._tunnel = self._connectToMySQL(config=self.StoreConfig)
            if self.Connection is not None:
                self._cursor = self.Connection.cursor()
            Logger.Log("Done preparing database connection.", logging.DEBUG)
            time_delta = datetime.now() - start
            Logger.Log(f"Database Connection Time: {time_delta}", logging.INFO)
        else:
            Logger.Log("Unable to connect to MySQL, game source schema does not have a valid MySQL config!", level=logging.ERROR)
            self.Close() # make sure we don't leave anything connected.

        return self.Connection is not None and self.Connection.is_connected()

    def _close(self) -> bool:
        if self.Connection is not None:
            self.Connection.close()
            Logger.Log("Closed MySQL database connection", logging.DEBUG)
        else:
            Logger.Log("No MySQL database to close.", logging.DEBUG)
        if self._tunnel is not None:
            self._tunnel.stop()
            Logger.Log("Stopped MySQL tunnel connection", logging.DEBUG)
        else:
            Logger.Log("No MySQL tunnel to stop", logging.DEBUG)
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
        return True if (super().IsOpen and self.Connection is not None and self.Connection.is_connected()) else False

    # *** PRIVATE STATICS ***

    # Function to help connect to a mySQL server.
    @staticmethod
    def _connectToMySQL(config:MySQLConfig) -> Pair[Optional[connection.MySQLConnection], Optional[sshtunnel.SSHTunnelForwarder]]:
        """Function to help connect to a mySQL server.

        Simply tries to make a connection, and prints an error in case of failure.
        :param login: A SQLLogin object with the data needed to log into MySQL.
        :type login: SQLLogin
        :return: If successful, a MySQLConnection object, otherwise None.
        :rtype: Optional[connection.MySQLConnection]
        """
        _tunnel     : Optional[sshtunnel.SSHTunnelForwarder] = None
        _connection : Optional[connection.MySQLConnection]   = None
        if config.HasSSH:
            Logger.Log(f"Preparing to connect to MySQL via SSH, on host {config.SSH.Host}", level=logging.DEBUG)
            if (config.SSH.Host is not None and config.SSH.Host != ""
            and config.SSH.User is not None and config.SSH.User != ""
            and config.SSH.Pass is not None and config.SSH.Pass != ""):
                _connection,_tunnel = MySQLConnector._connectToMySQLviaSSH(config=config)
            else:
                Logger.Log(f"SSH login had empty data, preparing to connect to MySQL directly instead, on host {config.DBHost}", level=logging.DEBUG)
        else:
            Logger.Log(f"Preparing to connect to MySQL directly, on host {config.DBHost}", level=logging.DEBUG)
        try:
            Logger.Log(f"Connecting to SQL (no SSH) at {config.AsConnectionInfo}...", logging.DEBUG)
            _connection = connection.MySQLConnection(host     = config.DBHost,    port    = config.DBPort,
                                                 user     = config.DBUser,    password= config.DBPass,
                                                 charset = 'utf8')
            Logger.Log("Connected.", logging.DEBUG)
        #except MySQLdb.connections.Error as err:
        except Exception as err:
            msg = f"""Could not connect to the MySql database.
            Login info: {config.AsConnectionInfo} w/port type={type(config.DBPort)}.
            Full error: {type(err)} {str(err)}"""
            Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
        return _connection, _tunnel

    ## Function to help connect to a mySQL server over SSH.
    @staticmethod
    def _connectToMySQLviaSSH(config:MySQLConfig) -> Pair[Optional[connection.MySQLConnection], Optional[sshtunnel.SSHTunnelForwarder]]:
        """Function to help connect to a mySQL server over SSH.

        Simply tries to make a connection, and prints an error in case of failure.
        :param sql: A SQLLogin object with the data needed to log into MySQL.
        :type sql: SQLLogin
        :param ssh: An SSHLogin object with the data needed to log into MySQL.
        :type ssh: SSHLogin
        :return: An open connection to the database if successful, otherwise None.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        _tunnel     : Optional[sshtunnel.SSHTunnelForwarder] = None
        _connection : Optional[connection.MySQLConnection]   = None
        MAX_TRIES : Final[int] = 5
        tries : int = 0
        connected_ssh : bool = False

        # First, connect to SSH
        while connected_ssh == False and tries < MAX_TRIES:
            if tries > 0:
                Logger.Log("Re-attempting to connect to SSH.", logging.INFO)
            try:
                Logger.Log(f"Connecting to SSH at {config.SSHConf.AsConnectionInfo}...", logging.DEBUG)
                _tunnel = sshtunnel.SSHTunnelForwarder(
                    (config.SSH.Host, config.SSH.Port), ssh_username=config.SSH.User, ssh_password=config.SSH.Pass,
                    remote_bind_address=(config.DBHost, config.DBPort), logger=Logger.std_logger
                )
                _tunnel.start()
                connected_ssh = True
                Logger.Log("Connected.", logging.DEBUG)
            except Exception as err:
                msg = f"Could not connect via SSH: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.Print(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                tries = tries + 1
        if connected_ssh == True and _tunnel is not None:
            # Then, connect to MySQL
            try:
                Logger.Log(f"Connecting to SQL (via SSH) at {config.DBUser}@{config.DBHost}:{_tunnel.local_bind_port}...", logging.DEBUG)
                _connection = connection.MySQLConnection(host     = config.DBHost,    port    = _tunnel.local_bind_port,
                                                     user     = config.DBUser,    password= config.DBPass,
                                                     charset ='utf8')
                Logger.Log("Connected", logging.DEBUG)
                return (_connection, _tunnel)
            except Exception as err:
                msg = f"Could not connect to the MySql database: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.Print(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                if _tunnel is not None:
                    _tunnel.stop()
                return (None, None)
        else:
            return (None, None)

    # *** PRIVATE METHODS ***
