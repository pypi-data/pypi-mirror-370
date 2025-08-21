# standard imports
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from typing import Dict, Final, List, LiteralString, Optional, Tuple, Union, override
# 3rd-party imports
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
# OGD imports
from ogd.common.filters import *
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.filters.collections.SequencingFilterCollection import SequencingFilterCollection
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

type BigQueryParameter = Union[bigquery.ScalarQueryParameter, bigquery.ArrayQueryParameter, bigquery.RangeQueryParameter]
@dataclass
class ParamaterizedClause:
    clause: LiteralString
    params: List[BigQueryParameter]

class BigQueryInterface(Interface):
    """Implementation of Interface functions for BigQuery.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, store:Optional[BigQueryConnector]=None):
        self._store : BigQueryConnector

        super().__init__(config=config, fail_fast=fail_fast)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, BigQueryConfig):
            self._store = BigQueryConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"BigQueryInterface config was for a connector other than BigQuery! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

    @property
    def DBPath(self) -> str:
        """The path of form "[projectID].[datasetID].[tableName]" used to make queries

        TODO : do something more... clever than directly using configured values. That's how it's been so far, and that's fine,
        but wouldn't want any clever inputs here.

        :return: The full path from project ID to table name, if properly set in configuration, else the literal string "INVALID SOURCE SCHEMA".
        :rtype: str
        """
        return f"{self.Connector.StoreConfig.Location.DatabaseName}.{self.Config.Location.Location}_*"


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> BigQueryConnector:
        return self._store

    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        """
        .. TODO : take other filters into account
        """
        ret_val = []

        if self.Connector.Client:
            # 1. Create query & config
            id_col : LiteralString       = "session_id" if mode==IDMode.SESSION else "user_id"
            suffix : ParamaterizedClause = self._generateSuffixClause(date_filter=filters.Sequences)
            suffix_clause = f"WHERE {suffix.clause}" if suffix.clause is not None else ""
            query = f"""
                SELECT DISTINCT {id_col}
                FROM `{self.DBPath}`
                {suffix_clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=suffix.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for all {mode} ids:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, cfg)
            except BadRequest as err:
                Logger.Log(f"In _availableIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[id_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} ids. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    @override
    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str, datetime] = {}

        if self.Connector.Client:
            # 1. Create query & config
            where_clause = self._generateWhereClause(filters=filters)
            query = f"""
                SELECT MIN(server_time), MAX(server_time)
                FROM `{self.DBPath}`
                {where_clause.clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for full date range:\n{query}", logging.DEBUG, depth=3)
            try:
                data = list(self.Connector.Client.query(query, job_config=cfg))
                Logger.Log(f"...Query yielded results:\n{data}", logging.DEBUG, depth=3)
            except BadRequest as err:
                Logger.Log(f"In _availableDates, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                if len(data) == 1:
                    dates = data[0]
                    if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
                        _min = dates[0] if type(dates[0]) == datetime else datetime.strptime(str(dates[0]), "%m-%d-%Y %H:%M:%S")
                        _max = dates[1] if type(dates[1]) == datetime else datetime.strptime(str(dates[1]), "%m-%d-%Y %H:%M:%S")
                        ret_val = {'min':_min, 'max':_max}
                    else:
                        Logger.Log("BigQueryInterface query did not give both a min and a max, setting both to 'now'", logging.WARNING, depth=3)
                        ret_val = {'min':datetime.now(), 'max':datetime.now()}
                else:
                    Logger.Log("BigQueryInterface query did not return any results, setting both min and max to 'now'", logging.WARNING, depth=3)
                    ret_val = {'min':datetime.now(), 'max':datetime.now()}
        else:
            Logger.Log(f"Can't retrieve available dates from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    @override
    def _availableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self.Connector.Client:
            # 1. Create query & config
            version_col  : LiteralString       = "log_version" if mode==VersionType.LOG else "app_version" if mode==VersionType.APP else "app_branch"
            where_clause : ParamaterizedClause = self._generateWhereClause(filters=filters)
            query = f"""
                SELECT DISTINCT {version_col}
                FROM `{self.DBPath}`
                {where_clause.clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for distinct {mode} versions:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, job_config=cfg)
            except BadRequest as err:
                Logger.Log(f"In _availableVersions, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row[version_col]) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} versions. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} versions from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)
        return ret_val

    @override
    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        ret_val = []

        if self.Connector.Client:
            # 1. Create query & config
            where_clause : ParamaterizedClause = self._generateWhereClause(filters=filters)
            # TODO Order by user_id, and by timestamp within that.
            # Note that this could prove to be wonky when we have more games without user ids,
            # will need to really rethink this when we start using new system.
            # Still, not a huge deal because most of these will be rewritten at that time anyway.
            query = f"""
                SELECT *
                FROM `{self.DBPath}`
                {where_clause.clause}
                ORDER BY `user_id`, `session_id`, `event_sequence_index` ASC
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            # 2. Actually run the thing
            Logger.Log(f"Running query for rows from IDs:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, job_config=cfg)
            except BadRequest as err:
                Logger.Log(f"In _rowsFromIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                Logger.Log(f"...Query yielded results, with query in state: {data.state}", logging.DEBUG, depth=3)
                for row in data:
                    items = tuple(row.items())
                    event = []
                    for item in items:
                        match item[0]:
                            case "event_params":
                                _params = {param['key']:param['value'] for param in item[1]}
                                event.append(json.dumps(_params, sort_keys=True))
                            case "device":
                                event.append(json.dumps(item[1], sort_keys=True))
                            case _:
                                event.append(item[1])
                    ret_val.append(tuple(event))
        else:
            Logger.Log(f"Can't retrieve collection of events from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)

        return ret_val

    def _getFeatureRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        return []

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _generateSuffixClause(date_filter:SequencingFilterCollection) -> ParamaterizedClause:
        clause = ""
        params = []

        if date_filter.Timestamps.Min and date_filter.Timestamps.Max:
            str_min, str_max = date_filter.Timestamps.Min.strftime("%Y%m%d"), date_filter.Timestamps.Max.strftime("%Y%m%d")
            clause = "_TABLE_SUFFIX BETWEEN @suffixstart AND @suffixend"
            params.append(
                bigquery.ScalarQueryParameter(type_="STRING", value=str_min, name="suffixstart")
            )
            params.append(
                bigquery.ScalarQueryParameter(type_="STRING", value=str_max, name="suffixend")
            )

        return ParamaterizedClause(clause=clause, params=params)

    @staticmethod
    def _generateWhereClause(filters:DatasetFilterCollection) -> ParamaterizedClause:
        exclude : LiteralString

        sess_clause : Optional[LiteralString] = None
        sess_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.IDFilters.Sessions.Active:
            sessions : List[str] = filters.IDFilters.Sessions.AsList or []
            if len(sessions) > 0:
                exclude = "NOT" if filters.IDFilters.Sessions.FilterMode == FilterMode.EXCLUDE else ""
                sess_clause = f"`session_id` {exclude} IN UNNEST(@session_list)"
                sess_param = [
                    bigquery.ArrayQueryParameter(name="session_list", array_type="STRING", values=sessions)
                ]

        users_clause : Optional[LiteralString] = None
        users_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.IDFilters.Players.Active:
            players : List[str] = filters.IDFilters.Players.AsList or []
            if len(players) > 0:
                exclude = "NOT" if filters.IDFilters.Players.FilterMode == FilterMode.EXCLUDE else ""
                users_clause = f"`user_id` {exclude} IN UNNEST(@user_list)"
                users_param = [
                    bigquery.ArrayQueryParameter(name="user_list", array_type="STRING", values=players)
                ]

        times_clause : Optional[LiteralString] = None
        times_param  : List[bigquery.RangeQueryParameter | bigquery.ScalarQueryParameter] = []
        if filters.Sequences.Timestamps.Active:
            if filters.Sequences.Timestamps.Min and filters.Sequences.Timestamps.Max:
                exclude = "NOT" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ""
                times_clause = f"`client_time` {exclude} BETWEEN @timestamp_range"
                times_param = [
                    bigquery.RangeQueryParameter(name="timestamp_range", range_element_type="TIMESTAMP", start=filters.Sequences.Timestamps.Min, end=filters.Sequences.Timestamps.Max)
                ]
            elif filters.Sequences.Timestamps.Min:
                exclude = "<" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                times_clause = f"`client_time` {exclude} @timestamp_min"
                times_param = [
                    bigquery.ScalarQueryParameter(name="timestamp_min", type_="TIMESTAMP", value=filters.Sequences.Timestamps.Min)
                ]
            else: # date_filter.TimestampFilter.Max is not None
                exclude = ">" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                times_clause = f"`client_time` {exclude} @timestamp_max"
                times_param = [
                    bigquery.ScalarQueryParameter(name="timestamp_max", type_="TIMESTAMP", value=filters.Sequences.Timestamps.Max)
                ]

        indices_clause : Optional[LiteralString] = None
        indices_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.Sequences.SessionIndices.Active:
            indices : List[int] = filters.Sequences.SessionIndices.AsList or []
            if len(indices) > 0:
                exclude = "NOT" if filters.Sequences.SessionIndices.FilterMode == FilterMode.EXCLUDE else ""
                indices_clause = f"`event_session_index` {exclude} IN UNNEST(@sess_index_list)"
                indices_param = [
                    bigquery.ArrayQueryParameter(name="sess_index_list", array_type="INT64", values=indices)
                ]

        log_clause : Optional[LiteralString] = None
        log_param  : List[BigQueryParameter] = []
        if filters.Versions.LogVersions.Active:
            if isinstance(filters.Versions.LogVersions, SetFilter):
                logs : List[str] = [str(ver) for ver in filters.Versions.LogVersions.AsList] if filters.Versions.LogVersions.AsList else []
                if len(logs) > 0:
                    exclude = "NOT" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_clause = f"`log_version` {exclude} IN UNNEST(@log_versions)"
                    log_param = [
                        bigquery.ArrayQueryParameter(name="log_versions", array_type="STRING", values=logs)
                    ]
            elif isinstance(filters.Versions.LogVersions, RangeFilter):
                if filters.Versions.LogVersions.Min and filters.Versions.LogVersions.Max:
                    exclude = "NOT" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_clause = f"`log_version` {exclude} BETWEEN @log_version_min AND @log_version_max"
                    log_param = [
                        bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value=str(filters.Versions.LogVersions.Min)),
                        bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value=str(filters.Versions.LogVersions.Max))
                    ]
                elif filters.Versions.LogVersions.Min:
                    exclude = "<" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    log_clause = f"`log_version` {exclude} @log_version_min"
                    log_param = [
                        bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value=str(filters.Versions.LogVersions.Min))
                    ]
                else: # version_filter.LogVersionFilter.Max is not None
                    exclude = ">" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    log_clause = f"`log_version` {exclude} @log_version_max"
                    log_param = [
                        bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value=str(filters.Versions.LogVersions.Max))
                    ]

        app_clause : Optional[LiteralString] = None
        app_param  : List[BigQueryParameter] = []
        if filters.Versions.AppVersions.Active:
            if isinstance(filters.Versions.AppVersions, SetFilter):
                apps : List[str] = [str(ver) for ver in filters.Versions.AppVersions.AsList] if filters.Versions.AppVersions.AsList else []
                if len(apps) > 0:
                    exclude = "NOT" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_clause = f"`app_version` {exclude} IN UNNEST(@app_versions)"
                    app_param = [
                        bigquery.ArrayQueryParameter(name="app_versions", array_type="STRING", values=apps)
                    ]
            elif isinstance(filters.Versions.AppVersions, RangeFilter):
                if filters.Versions.AppVersions.Min and filters.Versions.AppVersions.Max:
                    exclude = "NOT" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_clause = f"`app_version` {exclude} BETWEEN @app_version_min AND @app_version_max"
                    app_param = [
                        bigquery.ScalarQueryParameter(name="app_version_min", type_="STRING", value=str(filters.Versions.AppVersions.Min)),
                        bigquery.ScalarQueryParameter(name="app_version_max", type_="STRING", value=str(filters.Versions.AppVersions.Max))
                    ]
                elif filters.Versions.AppVersions.Min:
                    exclude = "<" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    app_clause = f"`app_version` {exclude} @app_version_min"
                    app_param = [
                        bigquery.ScalarQueryParameter(name="app_version_min", type_="STRING", value=str(filters.Versions.AppVersions.Min))
                    ]
                else: # version_filter.AppVersionFilter.Max is not None
                    exclude = ">" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    app_clause = f"`app_version` {exclude} @app_version_max"
                    app_param = [
                        bigquery.ScalarQueryParameter(name="app_version_max", type_="STRING", value=str(filters.Versions.AppVersions.Max))
                    ]

        branch_clause : Optional[LiteralString] = None
        branch_param  : List[BigQueryParameter] = []
        if filters.Versions.AppBranches.Active:
            if isinstance(filters.Versions.AppBranches, SetFilter):
                branches : List[str] = filters.Versions.AppBranches.AsList or []
                if len(branches) > 0:
                    exclude = "NOT" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_clause = f"`app_branch` {exclude} IN UNNEST(@app_branches)"
                    branch_param = [
                        bigquery.ArrayQueryParameter(name="app_branches", array_type="STRING", values=branches)
                    ]
            elif isinstance(filters.Versions.AppBranches, RangeFilter):
                if filters.Versions.AppBranches.Min and filters.Versions.AppBranches.Max:
                    exclude = "NOT" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_clause = f"`app_branch` {exclude} BETWEEN @app_branch_min AND @app_branch_max"
                    branch_param = [
                        bigquery.ScalarQueryParameter(name="app_branch_min", type_="STRING", value=str(filters.Versions.AppBranches.Min)),
                        bigquery.ScalarQueryParameter(name="app_branch_max", type_="STRING", value=str(filters.Versions.AppBranches.Max))
                    ]
                elif filters.Versions.AppBranches.Min:
                    exclude = "<" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    branch_clause = f"`app_branch` {exclude} @app_branch_min"
                    branch_param = [
                        bigquery.ScalarQueryParameter(name="app_branch_min", type_="STRING", value=str(filters.Versions.AppBranches.Min))
                    ]
                else: # version_filter.AppBranchFilter.Max is not None
                    exclude = ">" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    branch_clause = f"`app_branch` {exclude} @app_branch_max"
                    branch_param = [
                        bigquery.ScalarQueryParameter(name="app_branch_max", type_="STRING", value=str(filters.Versions.AppBranches.Max))
                    ]

        events_clause : Optional[LiteralString] = None
        events_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.Events.EventNames.Active:
            events : List[str] = filters.Events.EventNames.AsList or []
            if len(events) > 0:
                exclude = "NOT" if filters.Events.EventNames.FilterMode == FilterMode.EXCLUDE else ""
                events_clause = f"`event_name` {exclude} IN UNNEST(@event_name_list)"
                events_param.append(
                    bigquery.ArrayQueryParameter(name="event_name_list", array_type="STRING", values=events)
                )

        # codes_clause : Optional[LiteralString] = None
        # codes_param  : List[BigQueryParameter] = []
        # if event_filter.EventCodeFilter:
        #     if isinstance(filters.Events.EventCodeFilter, SetFilter) and len(event_filter.EventCodeFilter.AsSet) > 0:
        #         exclude = "NOT" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #         codes_clause = f"`event_code` {exclude} IN UNNEST(@app_branchs)"
        #         codes_param.append(
        #             bigquery.ArrayQueryParameter(name="app_branchs", array_type="INT64", values=filters.Events.EventCodeFilter.AsList)
        #         )
        #     elif isinstance(event_filter.EventCodeFilter, RangeFilter):
        #         if filters.Events.EventCodeFilter.Min and event_filter.EventCodeFilter.Max:
        #             exclude = "NOT" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #             codes_clause = f"`event_code` {exclude} BETWEEN @event_codes_range"
        #             codes_param.append(
        #                 bigquery.RangeQueryParameter(name="event_codes_range", range_element_type="INT64", start=filters.Events.EventCodeFilter.Min, end=event_filter.EventCodeFilter.Max)
        #             )
        #         elif filters.Events.EventCodeFilter.Min:
        #             exclude = "<" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
        #             codes_clause = f"`event_code` {exclude} @event_codes_min"
        #             codes_param.append(
        #                 bigquery.ScalarQueryParameter(name="event_codes_min", type_="STRING", value=str(filters.Events.EventCodeFilter.Min))
        #             )
        #         else: # filters.Events.EventCodeFilter.Max is not None
        #             exclude = ">" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
        #             codes_clause = f"`event_code` {exclude} @event_codes_max"
        #             codes_param.append(
        #                 bigquery.ScalarQueryParameter(name="event_codes_max", type_="STRING", value=str(filters.Events.EventCodeFilter.Max))
        #             )

        # clause_list_raw : List[Optional[LiteralString]] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause, codes_clause]
        clause_list_raw : List[Optional[LiteralString]] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause]
        clause_list     : List[LiteralString]           = [clause for clause in clause_list_raw if clause is not None]
        where_clause    : LiteralString                 = f"WHERE {'\nAND '.join(clause_list)}" if len(clause_list) > 0 else ""

        # params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param, codes_param]
        params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param]
        params = list(chain.from_iterable(params_collection))

        return ParamaterizedClause(clause=where_clause, params=params)

    # *** PRIVATE METHODS ***
