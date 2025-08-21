import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
# 3rd-party imports
import numpy as np
import pandas as pd
## import local files
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.CSVConnector import CSVConnector
from ogd.common.utils.Logger import Logger

type PDMask = Union[pd.Series, bool]
class CSVInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, extension:str="tsv", store:Optional[CSVConnector]=None):
        self._store : CSVConnector

        super().__init__(config=config, fail_fast=fail_fast)
        self._extension = extension
        self._data = pd.DataFrame()
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, FileStoreConfig):
            self._store = CSVConnector(
                config=self.Config.StoreConfig,
                with_secondary_files=set(),
            )
        else:
            raise ValueError(f"CSVInterface config was for a connector other than CSV/TSV files! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open(writeable=False)

        # We always just read the file right away.
        if self.Connector.IsOpen and self.Connector.File:
            # TODO should include option for access to the TableConfig in the interface, because obviously it should know what form the table takes.
            _default = lambda : np.dtype("object")
            _mapping : Dict[str, np.dtype] = {
                column.Name : np.dtype(column.ValueType if column.ValueType in {"str", "int", "float"} else "object")
                for column in self.Config.TableSchema.Columns
            }
            target_types = defaultdict(_default, _mapping)

            date_columns = [
                column.Name for column in self.Config.TableSchema.Columns if column.ValueType in {"datetime", "timezone"}
            ] if self.Config.TableSchema is not None else []

            self._data = pd.read_csv(
                filepath_or_buffer=self.Connector.File,
                delimiter=self.Delimiter,
                dtype=target_types,
                parse_dates=date_columns
            )
            Logger.Log(f"Loaded from CSV, columns are: {self._data.dtypes}", logging.INFO)
            Logger.Log(f"First few rows are:\n{self._data.head(n=3)}")

    @property
    def DataFrame(self) -> pd.DataFrame:
        return self._data

    @property
    def Extension(self) -> str:
        return self._extension

    @property
    def Delimiter(self) -> str:
        match self.Extension:
            case "tsv":
                return "\t"
            case "csv":
                return ","
            case _:
                Logger.Log(f"CSVInterface has unexpected extension {self.Extension}, defaulting to comma-separation!", logging.WARN)
                return ","

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> CSVConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        ret_val : List[str] = []

        if not self.DataFrame.empty:
            dates = pd.to_datetime(self.DataFrame['timestamp'], format='ISO8601').dt.tz_convert(None) # HACK : need to handle this better elsewhere, pretty sure we've got someplace else giving us filters with dates rather than datetime
            mask = None
            if filters.Sequences.Timestamps.Active:
                if filters.Sequences.Timestamps.Min and filters.Sequences.Timestamps.Max:
                    mask = (dates >= filters.Sequences.Timestamps.Min) & (dates <= filters.Sequences.Timestamps.Max)
                if filters.Sequences.Timestamps.Min:
                    mask = dates >= filters.Sequences.Timestamps.Min
                if filters.Sequences.Timestamps.Min and filters.Sequences.Timestamps.Max:
                    mask = dates <= filters.Sequences.Timestamps.Max
            # if versions is not None and versions is not []:
            #     mask = mask & (self._data['app_version'].isin(versions))
            data_masked = self.DataFrame.loc[mask] if mask is not None else self.DataFrame
            ret_val = [str(id) for id in data_masked['session_id'].unique().tolist()]

        return ret_val

    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str,datetime] = {}

        if self.Connector.IsOpen:
            sess_mask : PDMask = True
            if filters.IDFilters.Sessions.AsSet is not None:
                match filters.IDFilters.Sessions.FilterMode:
                    case FilterMode.INCLUDE:
                        sess_mask = self.DataFrame['session_id'].isin(filters.IDFilters.Sessions.AsSet)
                    case FilterMode.EXCLUDE:
                        sess_mask = ~self.DataFrame['session_id'].isin(filters.IDFilters.Sessions.AsSet)
                    case FilterMode.NOFILTER:
                        pass
            user_mask : PDMask = True
            if filters.IDFilters.Players.AsSet is not None:
                match filters.IDFilters.Players.FilterMode:
                    case FilterMode.INCLUDE:
                        user_mask = self.DataFrame['user_id'].isin(filters.IDFilters.Players.AsSet)
                    case FilterMode.EXCLUDE:
                        user_mask = ~self.DataFrame['user_id'].isin(filters.IDFilters.Players.AsSet)
                    case FilterMode.NOFILTER:
                        pass

            _col  = self.DataFrame[sess_mask & user_mask]['timestamp']
            min_date = _col.min()
            max_date = _col.max()
            ret_val = {'min':pd.to_datetime(min_date), 'max':pd.to_datetime(max_date)}

        return ret_val

    def _availableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self.Connector.IsOpen:
            version_col  : str = "log_version" if mode==VersionType.LOG else "app_version" if mode==VersionType.APP else "app_branch"
            ret_val = [SemanticVersion.FromString(str(ver)) for ver in self.DataFrame[version_col].unique().tolist()]

        return ret_val


    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        ret_val : List[Tuple] = []

        if self.Connector.IsOpen and not self.DataFrame.empty:
            sess_mask : PDMask = True
            if filters.IDFilters.Sessions.AsSet is not None:
                match filters.IDFilters.Sessions.FilterMode:
                    case FilterMode.INCLUDE:
                        sess_mask = self.DataFrame['session_id'].isin(filters.IDFilters.Sessions.AsSet)
                    case FilterMode.EXCLUDE:
                        sess_mask = ~self.DataFrame['session_id'].isin(filters.IDFilters.Sessions.AsSet)
                    case FilterMode.NOFILTER:
                        pass
            user_mask : PDMask = True
            if filters.IDFilters.Players.AsSet is not None:
                match filters.IDFilters.Players.FilterMode:
                    case FilterMode.INCLUDE:
                        user_mask = self.DataFrame['user_id'].isin(filters.IDFilters.Players.AsSet)
                    case FilterMode.EXCLUDE:
                        user_mask = ~self.DataFrame['user_id'].isin(filters.IDFilters.Players.AsSet)
                    case FilterMode.NOFILTER:
                        pass
            event_mask : PDMask = True
            if filters.Events.EventNames.AsSet is not None:
                match filters.Events.EventNames.FilterMode:
                    case FilterMode.INCLUDE:
                        event_mask = self.DataFrame['event_name'].isin(filters.Events.EventNames.AsSet)
                    case FilterMode.EXCLUDE:
                        event_mask = ~self.DataFrame['event_name'].isin(filters.Events.EventNames.AsSet)
                    case FilterMode.NOFILTER:
                        pass
            _data = self.DataFrame[sess_mask & user_mask & event_mask]
            ret_val = list(_data.itertuples(index=False, name=None))
        return ret_val

    def _getFeatureRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        return []

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @classmethod
    def _safeguardFilters(cls, filters:DatasetFilterCollection) -> None:
        """Override of the `_safeguardFilters` function to perform a check on a filter set, and update the filters if they are not satisfactory.

        For CSVInterface, we are comfortable reading the entirety of a file, so this override simply applies no constraints or defaults, and allows any filtering configuration.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        """
        return

    # *** PRIVATE METHODS ***
