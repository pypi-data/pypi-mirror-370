"""DataInterface Module
"""
## import standard libraries
import abc
import logging
import sys
from datetime import datetime, time, timedelta
from pprint import pformat
from typing import Dict, List, Optional, Tuple, Union

# import local files
from ogd.common.filters.RangeFilter import RangeFilter
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.models.Event import Event
from ogd.common.models.EventSet import EventSet
from ogd.common.models.Feature import Feature
from ogd.common.models.FeatureSet import FeatureSet
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.storage.connectors.StorageConnector import StorageConnector
from ogd.common.utils.typing import Map
from ogd.common.utils.Logger import Logger

class Interface(abc.ABC):
    """Base class for all connectors that serve as an interface to some IO resource.

    All subclasses must implement the `_availableIDs`, `_availableDates`, `_IDsFromDates`, and `_datesFromIDs` functions.
    """

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Connector(self) -> StorageConnector:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        """Private implementation of the logic to retrieve all IDs of given mode from the connected storage.

        :param mode: The type of ID to be listed.
        :type mode: IDMode
        :return: A list of IDs with given mode available through the connected storage.
        :rtype: List[str]
        """
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str,datetime]:
        """Private implementation of the logic to retrieve the full range of dates/times from the connected storage.

        :return: A dict mapping `min` and `max` to the minimum and maximum datetimes
        :rtype: Dict[str,datetime]
        """
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _availableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    @abc.abstractmethod
    def _getFeatureRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        # pylint: disable-next=protected-access
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the {sys._getframe().f_code.co_name} function!")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool):
        self._config    : DataTableConfig = config
        self._fail_fast : bool            = fail_fast
        super().__init__()

    @property
    def Config(self) -> DataTableConfig:
        return self._config

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def AvailableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> Optional[List[str]]:
        """Retrieve all IDs of given mode from the connected storage.

        :param mode: The type of ID to be listed.
        :type mode: IDMode
        :return: A list of IDs with given mode available through the connected storage.
        :rtype: List[str]
        """
        ret_val = None
        if self.Connector.IsOpen:
            self._safeguardFilters(filters=filters)
            _msg = f"Retrieving IDs with {mode} ID mode on date(s) {filters.Sequences} with version(s) {filters.Versions} from {self.Connector.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableIDs(mode=mode, filters=filters)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val

    def AvailableDates(self, filters:DatasetFilterCollection) -> Union[Dict[str,datetime], Dict[str,None]]:
        """Retrieve the full range of dates/times covered by data in the connected storage, subject to given filters.

        Note, this is different from listing the exact dates in which the data exists.
        This function gets the range from the earliest instance of an event matching the filters, to the last such instance.

        TODO: Create separate functions for exact dates and date range.

        :return: A dictionary mapping `min` and `max` to the range of dates covering all data for the given IDs/versions
        :rtype: Union[Dict[str,datetime], Dict[str,None]]
        """
        ret_val = {'min':None, 'max':None}
        if self.Connector.IsOpen:
            self._safeguardFilters(filters=filters)
            _msg = f"Retrieving range of event/feature dates with version(s) {filters.Versions} from {self.Connector.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableDates(filters=filters)
        else:
            Logger.Log(f"Could not get full date range from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val

    def AvailableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        """Get a list of all versions of given type in the connected storage, subject to ID and date filters.

        :param mode: _description_
        :type mode: VersionType
        :param id_filter: _description_
        :type id_filter: IDFilterCollection
        :param date_filter: _description_
        :type date_filter: TimingFilterCollection
        :return: _description_
        :rtype: List[SemanticVersion | str]
        """
        ret_val = []
        if self.Connector.IsOpen:
            self._safeguardFilters(filters=filters)
            _msg = f"Retrieving data versions on date(s) {filters.Sequences} from {self.Connector.ResourceName}."
            Logger.Log(_msg, logging.INFO, depth=3)
            ret_val = self._availableVersions(mode=mode, filters=filters)
        else:
            Logger.Log(f"Could not retrieve data versions from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)
        return ret_val

    def GetEventCollection(self, filters:DatasetFilterCollection, fallbacks:Map) -> EventSet:
        _events : List[Event] = []

        if self.Connector.IsOpen:
            self._safeguardFilters(filters=filters)
            if isinstance(self.Config.TableSchema, EventTableSchema):
                _msg = f"Retrieving event data from {self.Connector.ResourceName}."
                Logger.Log(_msg, logging.INFO, depth=3)

                rows = self._getEventRows(filters=filters)
                for row in rows:
                    try:
                        event = self.Config.TableSchema.EventFromRow(row, fallbacks=fallbacks)
                        # in case event index was not given, we should fall back on using the order it came to us.
                    except Exception as err: # pylint: disable=broad-exception-caught
                        if self._fail_fast:
                            Logger.Log(f"Error while converting row to Event! Cancelling data retrieval.\nFull error: {err}\nRow data: {pformat(row)}", logging.ERROR, depth=2)
                            raise err
                        else:
                            Logger.Log(f"Error while converting row ({row}) to Event! This row will be skipped.\nFull error: {err}", logging.WARNING, depth=2)
                    else:
                        _events.append(event)
            else:
                Logger.Log(f"Could not retrieve Event data from {self.Connector.ResourceName}, this interface is not configured for Event data!", logging.WARNING, depth=3)
        else:
            Logger.Log(f"Could not retrieve Event data from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)

        return EventSet(events=_events, filters=filters)

    def GetFeatureCollection(self, filters:DatasetFilterCollection, fallbacks:Map) -> FeatureSet:
        _features : List[Feature] = []

        if self.Connector.IsOpen:
            self._safeguardFilters(filters=filters)
            if isinstance(self.Config.TableSchema, FeatureTableSchema):
                _msg = f"Retrieving event data from {self.Connector.ResourceName}."
                Logger.Log(_msg, logging.INFO, depth=3)

                rows = self._getFeatureRows(filters=filters)
                for row in rows:
                    try:
                        feature = self.Config.TableSchema.FeatureFromRow(row, fallbacks=fallbacks)
                        # in case event index was not given, we should fall back on using the order it came to us.
                    except Exception as err: # pylint: disable=broad-exception-caught
                        if self._fail_fast:
                            Logger.Log(f"Error while converting row to Feature! Cancelling data retrieval.\nFull error: {err}\nRow data: {pformat(row)}", logging.ERROR, depth=2)
                            raise err
                        else:
                            Logger.Log(f"Error while converting row ({row}) to Feature! This row will be skipped.\nFull error: {err}", logging.WARNING, depth=2)
                    else:
                        _features.append(feature)
            else:
                Logger.Log(f"Could not retrieve Feature data from {self.Connector.ResourceName}, this interface is not configured for Feature data!", logging.WARNING, depth=3)
        else:
            Logger.Log(f"Could not retrieve Feature data from {self.Connector.ResourceName}, the storage connection is not open!", logging.WARNING, depth=3)

        return FeatureSet(features=_features, filters=filters)

    # *** PRIVATE STATICS ***

    @classmethod
    def _safeguardFilters(cls, filters:DatasetFilterCollection) -> None:
        """Function to perform a check on a filter set, and update the filters if they are not satisfactory.

        This is used in the top-level data retrieval functions to ensure the function won't try to read
        e.g. an entire database at once if the Interface user forgot to specify any filters.
        By default, it adds a filter for only the previous day's data if no filters were specified at all.
        
        Subclasses of Interface are allowed and encouraged to override the function to place appropriate constraints
        and provide appropriate defaults.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        """
        if not (filters.any):
            Logger.Log("Request filters did not define any filters at all! Defaulting to filter for yesterday's data!", logging.WARNING)
            yesterday = datetime.combine(datetime.now().date(), time(0)) - timedelta(days=1)
            filters.Sequences.Timestamps = RangeFilter[datetime](mode=FilterMode.INCLUDE, minimum=yesterday, maximum=datetime.now())

    # *** PRIVATE METHODS ***
