"""DataOuterface Module
"""
## import standard libraries
import abc
import logging
import sys
from typing import List, Set

# import local files
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.EventSet import EventSet
from ogd.common.models.FeatureSet import FeatureSet
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.typing import ExportRow
from ogd.common.utils.Logger import Logger

class Outerface:
    """Base class for feature and event output.

    :param Interface: _description_
    :type Interface: _type_
    :return: _description_
    :rtype: _type_
    """

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Connector(self) -> StorageConnector:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    # @abc.abstractmethod
    # def _destination(self, mode:ExportMode) -> str:
        # raise NotImplementedError(f"{self.__class__.__name__} has not implemented the Location function!")

    @abc.abstractmethod
    def _removeExportMode(self, mode:ExportMode) -> str:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")


    @abc.abstractmethod
    def _writeGameEventsHeader(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")


    @abc.abstractmethod
    def _writeAllEventsHeader(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")


    @abc.abstractmethod
    def _writeSessionHeader(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writePlayerHeader(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writePopulationHeader(self, header:List[str]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeSessionLines(self, session_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writePlayerLines(self, player_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writePopulationLines(self, population_lines:List[ExportRow]) -> None:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _writeMetadata(self, dataset_schema:DatasetSchema):
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, table_config:DataTableConfig, export_modes:Set[ExportMode]):
        self._config  : DataTableConfig = table_config
        self._modes   : Set[ExportMode] = export_modes

    @property
    def Config(self) -> DataTableConfig:
        return self._config

    @property
    def ExportModes(self) -> Set[ExportMode]:
        return self._modes

    @property
    def SessionCount(self) -> int:
        return self._session_ct
    @SessionCount.setter
    def SessionCount(self, new_val) -> None:
        self._session_ct = new_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # def Destination(self, mode:ExportMode):
    #     return self._destination(mode=mode)

    def RemoveExportMode(self, mode:ExportMode):
        self._removeExportMode(mode)
        self._modes.discard(mode)
        Logger.Log(f"Removed mode {mode} from {type(self).__name__} output.", logging.INFO)

    def WriteHeader(self, header:List[str], mode:ExportMode):
        if mode in self.ExportModes:
            match (mode):
                case ExportMode.EVENTS:
                    self._writeGameEventsHeader(header=header)
                    Logger.Log(f"Wrote event header for {self.Config.Location} events", depth=3)
                case ExportMode.DETECTORS:
                    self._writeAllEventsHeader(header=header)
                    Logger.Log(f"Wrote processed event header for {self.Config.Location} events", depth=3)
                case ExportMode.SESSION:
                    self._writeSessionHeader(header=header)
                    Logger.Log(f"Wrote session feature header for {self.Config.Location} sessions", depth=3)
                case ExportMode.PLAYER:
                    self._writePlayerHeader(header=header)
                    Logger.Log(f"Wrote player feature header for {self.Config.Location} players", depth=3)
                case ExportMode.POPULATION:
                    self._writePopulationHeader(header=header)
                    Logger.Log(f"Wrote population feature header for {self.Config.Location} populations", depth=3)
                case _:
                    Logger.Log(f"Failed to write header for unrecognized export mode {mode}!", level=logging.WARN, depth=3)
        else:
            Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)

    def WriteEvents(self, events:EventSet, mode:ExportMode) -> None:
        if isinstance(self.Config.TableSchema, EventTableSchema):
            if mode in self.ExportModes:
                match (mode):
                    case ExportMode.EVENTS:
                        self._writeGameEventLines(events=events.GameEventLines)
                        Logger.Log(f"Wrote {len(events.GameEventLines)} {self.Config.Location} events", depth=3)
                    case ExportMode.DETECTORS:
                        self._writeAllEventLines(events=events.EventLines)
                        Logger.Log(f"Wrote {len(events)} {self.Config.Location} processed events", depth=3)
                    case _:
                        Logger.Log(f"Failed to write lines for unrecognized Event export mode {mode}!", level=logging.WARN, depth=3)
            else:
                Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)
        else:
            Logger.Log(f"Could not write events from {type(self).__name__}, outerface was not configured for a Events table!", logging.WARNING, depth=3)

    def WriteFeatures(self, features:FeatureSet, mode:ExportMode) -> None:
        if isinstance(self.Config.TableSchema, FeatureTableSchema):
            if mode in self.ExportModes:
                match (mode):
                    case ExportMode.SESSION:
                        self._writeSessionLines(session_lines=features.SessionLines)
                        Logger.Log(f"Wrote {len(features.SessionLines)} {self.Config.Location} session lines", depth=3)
                    case ExportMode.PLAYER:
                        self._writePlayerLines(player_lines=features.PlayerLines)
                        Logger.Log(f"Wrote {len(features.PlayerLines)} {self.Config.Location} player lines", depth=3)
                    case ExportMode.POPULATION:
                        self._writePopulationLines(population_lines=features.PopulationLines)
                        Logger.Log(f"Wrote {len(features.PopulationLines)} {self.Config.Location} population lines", depth=3)
                    case _:
                        Logger.Log(f"Failed to write lines for unrecognized Feature export mode {mode}!", level=logging.WARN, depth=3)
            else:
                Logger.Log(f"Skipping WriteLines in {type(self).__name__}, export mode {mode} is not enabled for this outerface", depth=3)
        else:
            Logger.Log(f"Could not write features from {type(self).__name__}, outerface was not configured for a Features table!", logging.WARNING, depth=3)

    def WriteMetadata(self, dataset_schema:DatasetSchema):
        
        self._writeMetadata(dataset_schema=dataset_schema)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
