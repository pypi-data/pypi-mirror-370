# import libraries
import logging
from datetime import datetime, time, timedelta
from itertools import chain
from typing import Dict, List, LiteralString, Optional, override, Tuple
# 3rd-party imports
from mysql.connector import cursor
# import locals
from ogd.common.filters import *
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.connectors.MySQLConnector import MySQLConnector
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.VersionType import VersionType
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Pair

class MySQLInterface(Interface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, store:Optional[MySQLConnector]=None):
        super().__init__(config=config, fail_fast=fail_fast)
        if store:
            self._store = store
        elif isinstance(self.Config.StoreConfig, MySQLConfig):
            self._store = MySQLConnector(config=self.Config.StoreConfig)
        else:
            raise ValueError(f"MySQLInterface config was for a connector other than MySQL! Found config type {type(self.Config.StoreConfig)}")
        self.Connector.Open()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def Connector(self) -> MySQLConnector:
        return self._store

    @override
    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        if self.Connector.Cursor is not None and isinstance(self.Config.StoreConfig, MySQLConfig):
            id_col : LiteralString       = "session_id" if mode==IDMode.SESSION else "user_id"
            # 1. If we're in shared table, then need to filter on game ID
            where_clause, params = self._generateWhereClause(filters=filters)
            app_ids = filters.IDFilters.AppIDs.AsList
            if app_ids and len(app_ids) > 0 and self.Config.TableName not in app_ids:
                if len(app_ids) == 1 and filters.IDFilters.AppIDs.FilterMode == FilterMode.INCLUDE:
                    where_clause += "\nAND `app_id`=%s"
                    params.append(app_ids[0])
                else:
                    exclude = "NOT" if filters.IDFilters.AppIDs.FilterMode == FilterMode.EXCLUDE else ""
                    app_param_string : LiteralString = ("%s, " * len(app_ids))[:-2] # take all but the trailing ', '.
                    where_clause += f"\nAND `app_id` {exclude} in ({app_param_string})"
                    params += app_ids
            query = f"""
                SELECT DISTINCT(`{id_col}`)
                FROM `{self.Config.Location.Location}`
                {where_clause}
            """
            data = MySQLInterface.Query(cursor=self.Connector.Cursor, query=query, params=tuple(params))
            return [str(id[0]) for id in data] if data != None else []
        else:
            Logger.Log(f"Could not get list of all session ids, MySQL connection is not open.", logging.WARN)
            return []

    @override
    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str, datetime] = {'min':datetime.now(), 'max':datetime.now()}

        if self.Connector.Cursor is not None and isinstance(self.Config.StoreConfig, MySQLConfig):
            where_clause, params = self._generateWhereClause(filters=filters)
            app_ids = filters.IDFilters.AppIDs.AsList
            if app_ids and len(app_ids) > 0 and self.Config.TableName not in app_ids:
                if len(app_ids) == 1 and filters.IDFilters.AppIDs.FilterMode == FilterMode.INCLUDE:
                    where_clause += "\nAND `app_id`=%s"
                    params.append(app_ids[0])
                else:
                    exclude = "NOT" if filters.IDFilters.AppIDs.FilterMode == FilterMode.EXCLUDE else ""
                    app_param_string : LiteralString = ("%s, " * len(app_ids))[:-2] # take all but the trailing ', '.
                    where_clause += f"\nAND `app_id` {exclude} in ({app_param_string})"
                    params += app_ids
            query = f"""
                SELECT MIN(`server_time`), MAX(`server_time`)
                FROM `{self.Config.Location.Location}`
                {where_clause}
            """

            # run query
            result = MySQLInterface.Query(cursor=self.Connector.Cursor, query=query, params=tuple(params))
            if result is not None:
                ret_val = {'min':result[0][0], 'max':result[0][1]}
        else:
            Logger.Log(f"Could not get full date range, MySQL connection is not open or config was not for MySQL.", logging.WARN)
        return ret_val

    def _availableVersions(self, mode:VersionType, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        ret_val : List[SemanticVersion | str] = []

        if self.Connector.Cursor is not None and isinstance(self.Config.StoreConfig, MySQLConfig):
            version_col  : LiteralString       = "log_version" if mode==VersionType.LOG else "app_version" if mode==VersionType.APP else "app_branch"

            where_clause, params = self._generateWhereClause(filters=filters)
            app_ids = filters.IDFilters.AppIDs.AsList
            if app_ids and len(app_ids) > 0 and self.Config.TableName not in app_ids:
                if len(app_ids) == 1 and filters.IDFilters.AppIDs.FilterMode == FilterMode.INCLUDE:
                    where_clause += "\nAND `app_id`=%s"
                    params.append(app_ids[0])
                else:
                    exclude = "NOT" if filters.IDFilters.AppIDs.FilterMode == FilterMode.EXCLUDE else ""
                    app_param_string : LiteralString = ("%s, " * len(app_ids))[:-2] # take all but the trailing ', '.
                    where_clause += f"\nAND `app_id` {exclude} in ({app_param_string})"
                    params += app_ids
            query = f"""
                SELECT DISTINCT({version_col})
                FROM `{self.Config.Location.Location}`
                {where_clause}
            """

            # run query
            result = MySQLInterface.Query(cursor=self.Connector.Cursor, query=query, params=tuple(params))
            if result is not None:
                ret_val = [str(row[0]) for row in result]
        else:
            Logger.Log(f"Could not get available versions, MySQL connection is not open or config was not for MySQL.", logging.WARN)
        return ret_val

    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        ret_val = []

        # grab data for the given session range. Sort by event time, so
        if self.Connector.Cursor is not None and isinstance(self.Config.StoreConfig, MySQLConfig):
            # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"

            where_clause, params = self._generateWhereClause(filters=filters)
            app_ids = filters.IDFilters.AppIDs.AsList
            if app_ids and len(app_ids) > 0 and self.Config.TableName not in app_ids:
                if len(app_ids) == 1 and filters.IDFilters.AppIDs.FilterMode == FilterMode.INCLUDE:
                    where_clause += "\nAND `app_id`=%s"
                    params.append(app_ids[0])
                else:
                    exclude = "NOT" if filters.IDFilters.AppIDs.FilterMode == FilterMode.EXCLUDE else ""
                    app_param_string : LiteralString = ("%s, " * len(app_ids))[:-2] # take all but the trailing ', '.
                    where_clause += f"\nAND `app_id` {exclude} in ({app_param_string})"
                    params += app_ids

            query = f"""
                SELECT *
                FROM `{self.Config.Location.Location}`
                {where_clause}
                ORDER BY `user_id`, `session_id`, `event_sequence_index` ASC
            """
            data = MySQLInterface.Query(cursor=self.Connector.Cursor, query=query, params=tuple(params))
            if data is not None:
                ret_val = data
            # self._select_queries.append(select_query) # this doesn't appear to be used???
        else:
            Logger.Log(f"Could not get data for {len(filters.IDFilters.Sessions.AsList or [])} requested sessions, MySQL connection is not open or config was not for MySQL.", logging.WARN)
        return ret_val

    def _getFeatureRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        return []

    # *** PUBLIC STATICS ***

    @staticmethod
    def Query(cursor:cursor.MySQLCursor, query:str, params:Optional[Tuple], fetch_results: bool = True) -> Optional[List[Tuple]]:
        ret_val : Optional[List[Tuple]] = None
        # first, we do the query.
        Logger.Log(f"Running query: {query}\nWith params: {params}", logging.DEBUG, depth=3)
        start = datetime.now()
        cursor.execute(query, params)
        time_delta = datetime.now()-start
        Logger.Log(f"Query execution completed, time to execute: {time_delta}", logging.DEBUG)
        # second, we get the results.
        if fetch_results:
            ret_val = cursor.fetchall()
            time_delta = datetime.now()-start
            Logger.Log(f"Query fetch completed, total query time:    {time_delta} to get {len(ret_val) if ret_val is not None else 0:d} rows", logging.DEBUG)
        return ret_val

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _generateWhereClause(filters:DatasetFilterCollection) -> Pair[str, List[str | int]]:
        exclude : LiteralString

        sess_clause : Optional[LiteralString] = None
        sess_param  : List[str] = []
        if filters.IDFilters.Sessions.Active:
            sess_param = filters.IDFilters.Sessions.AsList or []
            if len(sess_param) > 0:
                exclude = "NOT" if filters.IDFilters.Sessions.FilterMode == FilterMode.EXCLUDE else ""
                id_param_string : LiteralString = ("%s, " * len(sess_param))[:-2] # take all but the trailing ', '.
                sess_clause = f"`session_id` {exclude} IN ({id_param_string})"

        users_clause : Optional[LiteralString] = None
        users_param  : List[str] = []
        if filters.IDFilters.Players.Active:
            users_param = filters.IDFilters.Players.AsList or []
            if len(users_param) > 0:
                exclude = "NOT" if filters.IDFilters.Players.FilterMode == FilterMode.EXCLUDE else ""
                id_param_string : LiteralString = ("%s, " * len(users_param))[:-2] # take all but the trailing ', '.
                users_clause = f"`user_id` {exclude} IN ({id_param_string})"

        times_clause : Optional[LiteralString] = None
        times_param  : List[str] = []
        if filters.Sequences.Timestamps.Active:
            if filters.Sequences.Timestamps.Min and filters.Sequences.Timestamps.Max:
                exclude = "NOT" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ""
                times_clause = f"`client_time` {exclude} BETWEEN %s and %s"
                times_param = [filters.Sequences.Timestamps.Min.isoformat(), filters.Sequences.Timestamps.Max.isoformat()]
            elif filters.Sequences.Timestamps.Min:
                exclude = "<" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                times_clause = f"`client_time` {exclude} %s"
                times_param = [filters.Sequences.Timestamps.Min.isoformat()]
            elif filters.Sequences.Timestamps.Max:
                exclude = ">" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                times_clause = f"`client_time` {exclude} %s"
                times_param = [filters.Sequences.Timestamps.Max.isoformat()]

        indices_clause : Optional[LiteralString] = None
        indices_param  : List[int] = []
        if filters.Sequences.SessionIndices.Active:
            indices_param = filters.Sequences.SessionIndices.AsList or []
            if len(indices_param) > 0:
                exclude = "NOT" if filters.Sequences.SessionIndices.FilterMode == FilterMode.EXCLUDE else ""
                indices_param_string : LiteralString = ("%s, " * len(indices_param))[:-2] # take all but the trailing ', '.
                indices_clause = f"`event_session_index` {exclude} IN ({indices_param_string})"

        log_clause : Optional[LiteralString] = None
        log_param  : List[str] =  []
        if filters.Versions.LogVersions.Active:
            if isinstance(filters.Versions.LogVersions, SetFilter):
                log_param = [str(ver) for ver in filters.Versions.LogVersions.AsList] if filters.Versions.LogVersions.AsList else []
                if len(log_param) > 0:
                    exclude = "NOT" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_param_string : LiteralString = ("%s, " * len(log_param))[:-2] # take all but the trailing ', '.
                    log_clause = f"`log_version` {exclude} IN ({log_param_string})"
            elif isinstance(filters.Versions.LogVersions, RangeFilter):
                if filters.Versions.LogVersions.Min and filters.Versions.LogVersions.Max:
                    exclude = "NOT" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_clause = f"`log_version` {exclude} BETWEEN %s AND %s"
                    log_param = [str(filters.Versions.LogVersions.Min), str(filters.Versions.LogVersions.Max)]
                elif filters.Versions.LogVersions.Min:
                    exclude = "<" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    log_clause = f"`log_version` {exclude} %s"
                    log_param = [str(filters.Versions.LogVersions.Min)]
                else: # version_filter.LogVersionFilter.Max is not None
                    exclude = ">" if filters.Versions.LogVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    log_clause = f"`log_version` {exclude} %s"
                    log_param = [str(filters.Versions.LogVersions.Max)]

        app_clause : Optional[LiteralString] = None
        app_param  : List[str] = []
        if filters.Versions.AppVersions.Active:
            if isinstance(filters.Versions.AppVersions, SetFilter):
                app_param = [str(ver) for ver in filters.Versions.AppVersions.AsList] if filters.Versions.AppVersions.AsList else []
                if len(app_param) > 0:
                    exclude = "NOT" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_param_string : LiteralString = ("%s, " * len(app_param))[:-2] # take all but the trailing ', '.
                    app_clause = f"`app_version` {exclude} IN ({app_param_string})"
            elif isinstance(filters.Versions.AppVersions, RangeFilter):
                if filters.Versions.AppVersions.Min and filters.Versions.AppVersions.Max:
                    exclude = "NOT" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_clause = f"`app_version` {exclude} BETWEEN %s and %s"
                    app_param = [str(filters.Versions.AppVersions.Min), str(filters.Versions.AppVersions.Max)]
                elif filters.Versions.AppVersions.Min:
                    exclude = "<" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    app_clause = f"`app_version` {exclude} %s"
                    app_param = [str(filters.Versions.AppVersions.Min)]
                else: # version_filter.AppVersionFilter.Max is not None
                    exclude = ">" if filters.Versions.AppVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    app_clause = f"`app_version` {exclude} %s"
                    app_param = [str(filters.Versions.AppVersions.Max)]

        branch_clause : Optional[LiteralString] = None
        branch_param  : List[str] = []
        if filters.Versions.AppBranches.Active:
            if isinstance(filters.Versions.AppBranches, SetFilter):
                branch_param = [str(ver) for ver in filters.Versions.AppBranches.AsList] if filters.Versions.AppBranches.AsList else []
                if len(branch_param) > 0:
                    exclude = "NOT" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_param_string : LiteralString = ("%s, " * len(branch_param))[:-2] # take all but the trailing ', '.
                    branch_clause = f"`app_branch` {exclude} IN ({branch_param_string})"
            elif isinstance(filters.Versions.AppBranches, RangeFilter):
                if filters.Versions.AppBranches.Min and filters.Versions.AppBranches.Max:
                    exclude = "NOT" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_clause = f"`app_branch` {exclude} BETWEEN %s and %s"
                    app_param = [str(filters.Versions.AppBranches.Min), str(filters.Versions.AppBranches.Max)]
                elif filters.Versions.AppBranches.Min:
                    exclude = "<" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    branch_clause = f"`app_branch` {exclude} %s"
                    app_param = [str(filters.Versions.AppBranches.Min)]
                else: # version_filter.AppBranchFilter.Max is not None
                    exclude = ">" if filters.Versions.AppBranches.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    branch_clause = f"`app_branch` {exclude} %s"
                    app_param = [str(filters.Versions.AppBranches.Max)]

        events_clause : Optional[LiteralString] = None
        events_param  : List[str] = []
        if filters.Events.EventNames.Active:
            events_param = filters.Events.EventNames.AsList or []
            if len(events_param) > 0:
                exclude = "NOT" if filters.Events.EventNames.FilterMode == FilterMode.EXCLUDE else ""
                events_param_string : LiteralString = ("%s, " * len(events_param))[:-2] # take all but the trailing ', '.
                events_clause = f"`event_name` {exclude} IN ({events_param_string})"

        # codes_clause : Optional[LiteralString] = None
        # codes_param  : List[BigQueryParameter] = []
        # if event_filter.EventCodeFilter:
        #     if isinstance(filters.Events.EventCodeFilter, SetFilter) and len(event_filter.EventCodeFilter.AsSet) > 0:
        #         exclude = "NOT" if filters.Events.EventCodeFilter.FilterMode == FilterMode.EXCLUDE else ""
        #         codes_clause = f"`event_code` {exclude} IN @app_branchs"
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

        return (where_clause, params)


    # *** PRIVATE METHODS ***
