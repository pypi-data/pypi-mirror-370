import json
import logging
from datetime import datetime
from typing import Dict, Final, List, LiteralString, Tuple, Optional
# 3rd-party imports
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
# import locals
from ogd.common.filters import *
from ogd.common.filters.collections import *
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.SemanticVersion import SemanticVersion
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.storage.interfaces.BigQueryInterface import BigQueryInterface, ParamaterizedClause
from ogd.common.storage.connectors.BigQueryConnector import BigQueryConnector
from ogd.common.utils.Logger import Logger

AQUALAB_MIN_VERSION : Final[float] = 6.2

class BQFirebaseInterface(BigQueryInterface):
    """Subclass of the general BigQueryInterface, with re-implemented queries to handle old Firebase unnest bullshit.
    """

    # *** BUILT-INS ***

    def __init__(self, config:DataTableConfig, fail_fast:bool, store:Optional[BigQueryConnector]=None):
        super().__init__(config=config, fail_fast=fail_fast, store=store)

    # *** RE-IMPLEMENT ABSTRACT FUNCTIONS ***

    def _availableIDs(self, mode:IDMode, filters:DatasetFilterCollection) -> List[str]:
        ret_val = []

        if self.Connector.Client:
            suffix : ParamaterizedClause = self._generateSuffixClause(date_filter=filters.Sequences)
            suffix_clause = f"AND {suffix.clause}" if suffix.clause is not None else ""
            query = f"""
                SELECT DISTINCT param.value.int_value AS session_id
                FROM `{self.DBPath}`,
                UNNEST(event_params) AS param
                WHERE param.key = "ga_session_id"
                {suffix_clause}
            """
            cfg = bigquery.QueryJobConfig(query_parameters=suffix.params)

            # 2. Actually run the thing
            Logger.Log(f"BQ-Firebase: Running query for all ids:\n{query}", logging.DEBUG, depth=3)
            try:
                data = self.Connector.Client.query(query, cfg)
            except BadRequest as err:
                Logger.Log(f"In _availableIDs, got a BadRequest error when trying to retrieve data from BigQuery, defaulting to empty result!\n{err}")
            else:
                ret_val = [str(row['session_id']) for row in data]
                Logger.Log(f"Found {len(ret_val)} {mode} ids. {ret_val if len(ret_val) <= 5 else ''}", logging.DEBUG, depth=3)
        else:
            Logger.Log(f"Can't retrieve list of {mode} IDs from {self.Connector.ResourceName}, the storage connection client is null!", logging.WARNING, depth=3)

        return ret_val

    def _availableDates(self, filters:DatasetFilterCollection) -> Dict[str,datetime]:
        ret_val : Dict[str, datetime] = {}

        if self.Connector.Client:
            where_clause = self._generateWhereClause(filters=filters)
            query = f"""
                WITH datetable AS
                (
                    SELECT event_date, event_timestamp,
                    FORMAT_DATE('%m-%d-%Y', PARSE_DATE('%Y%m%d', event_date)) AS date, 
                    FORMAT_TIME('%T', TIME(TIMESTAMP_MICROS(event_timestamp))) AS time,
                    FROM `{self.DBPath}`
                    {where_clause.clause}
                )
                SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
                FROM datetable
            """
            cfg = bigquery.QueryJobConfig(query_parameters=where_clause.params)

            Logger.Log(f"BQ-Firebase: Running query for full date range:\n{query}", logging.DEBUG, depth=3)
            data = list(self.Connector.Client.query(query, job_config=cfg))
            ret_val = {'min':data[0][0], 'max':data[0][1]}
        return ret_val
        # from dates-from-IDs
        # match id_mode:
        #     case IDMode.SESSION:
        #         id_string = ','.join([f"{x}" for x in id_list])
        #         where_clause = f"""
        #             WHERE param.key = "ga_session_id"
        #             AND param.value.int_value IN ({id_string})
        #         """
        #     case IDMode.USER:
        #         id_string = ','.join([f"'{x}'" for x in id_list])
        #         where_clause = f"""
        #             WHERE param.key = "user_code"
        #             AND param.value.string_value IN ({id_string})
        #         """
        #     case _:
        #         Logger.Log(f"Invalid ID mode given (name={id_mode.name}, val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
        #         id_string = ','.join([f"{x}" for x in id_list])
        #         where_clause = f"""
        #             WHERE param.key = "ga_session_id"
        #             AND param.value.int_value IN ({id_string})
        #         """
        # query = f"""
        #     WITH datetable AS
        #     (
        #         SELECT event_date, event_timestamp, event_params,
        #         FORMAT_DATE('%m-%d-%Y', PARSE_DATE('%Y%m%d', event_date)) AS date, 
        #         FORMAT_TIME('%T', TIME(TIMESTAMP_MICROS(event_timestamp))) AS time,
        #         FROM `{self.DBPath()}`
        #     )
        #     SELECT MIN(concat(date, ' ', time)), MAX(concat(date, ' ', time))
        #     FROM datetable,
        #     UNNEST(event_params) AS param
        #     {where_clause}
        # """
        # Logger.Log(f"BQ-Firebase: Running query for dates from IDs:\n{query}", logging.DEBUG, depth=3)
        # data = list(self._client.query(query))
        # ret_val : Dict[str, datetime] = {}
        # if len(data) == 1:
        #     dates = data[0]
        #     if len(dates) == 2 and dates[0] is not None and dates[1] is not None:
        #         ret_val = {'min':datetime.strptime(dates[0], "%m-%d-%Y %H:%M:%S"), 'max':datetime.strptime(dates[1], "%m-%d-%Y %H:%M:%S")}
        #     else:
        #         Logger.Log(f"BQFirebaseInterface query did not give both a min and a max, setting both to 'now'", logging.WARNING, depth=3)
        #         ret_val = {'min':datetime.now(), 'max':datetime.now()}
        # else:
        #     Logger.Log(f"BQ-Firebase: Query did not return any results, setting both min and max to 'now'", logging.WARNING, depth=3)
        #     ret_val = {'min':datetime.now(), 'max':datetime.now()}
        # return ret_val

    def _availableVersions(self, filters:DatasetFilterCollection) -> List[SemanticVersion | str]:
        return []

    def _getEventRows(self, filters:DatasetFilterCollection) -> List[Tuple]:
        events = None
        if self._client != None:
            query = self._generateRowFromIDQuery(id_list=id_list, id_mode=id_mode, exclude_rows=exclude_rows)
            Logger.Log(f"BQ-Firebase: Running query for rows from IDs:\n{query}", logging.DEBUG, depth=3)
            data = self._client.query(query)
            events = []
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
                events.append(tuple(event))
        return events if events != None else []


    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _generateRowFromIDQuery(self, id_list:List[str], id_mode:IDMode, exclude_rows:Optional[List[str]]=None) -> str:
    # 2) Set up clauses to select based on Session ID or Player ID.
        session_clause : str = ""
        player_clause  : str = ""
        match id_mode:
            case IDMode.SESSION:
                id_string = ','.join([f"{x}" for x in id_list])
                session_clause = f"param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})"
                player_clause  = f"(param_user.key   = 'user_code'     OR  param_user.key = 'undefined')"
            case IDMode.USER:
                id_string = ','.join([f"'{x}'" for x in id_list])
                session_clause = f"param_session.key = 'ga_session_id'"
                player_clause  = f"(param_user.key   = 'user_code' OR param_user.key = 'undefined') AND param_user.value.string_value IN ({id_string})"
            case _:
                Logger.Log(f"BQ-Firebase: Invalid ID mode given (name={id_mode.name}, val={id_mode.value}), defaulting to session mode.", logging.WARNING, depth=3)
                id_string = ','.join([f"{x}" for x in id_list])
                session_clause = f"param_session.key = 'ga_session_id' AND param_session.value.int_value IN ({id_string})"
                player_clause  = f"(param_user.key   = 'user_code' OR param_user.key = 'undefined')"
    # 3) Set up WHERE clause based on whether we need Aqualab min version or not.
        match self._game_id:
            case "SHADOWSPECT" | "SHIPWRECKS":
                where_clause = \
                f"WHERE {session_clause}"
            case _:
                where_clause = \
                f"""WHERE param_app_version.key = 'app_version'
                    AND   param_log_version.key = 'log_version'
                    AND   {session_clause}
                    AND   {player_clause}"""
    # 4) Set up actual query
        query = ""
        match self._game_id:
            case "SHADOWSPECT" | "SHIPWRECKS":
                query = f"""
                    SELECT event_name, event_params, device, platform,
                    concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%S.00', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                    null as app_version,
                    null as log_version,
                    param_session.value.int_value as session_id,
                    null as fd_user_id
                    FROM `{self.DBPath()}`
                    CROSS JOIN UNNEST(event_params) AS param_session
                    {where_clause}
                    ORDER BY `session_id`, `timestamp` ASC;
                """
            case _:
                # TODO Order by user_id, and by timestamp within that.
                # Note that this could prove to be wonky when we have more games without user ids,
                # will need to really rethink this when we start using new system.
                # Still, not a huge deal because most of these will be rewritten at that time anyway.
                query = f"""
                    SELECT event_name, event_params, device, platform,
                    concat(FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)), FORMAT_TIME('T%H:%M:%S.00', TIME(TIMESTAMP_MICROS(event_timestamp)))) AS timestamp,
                    param_app_version.value.string_value as app_version,
                    param_log_version.value.int_value as log_version,
                    param_session.value.int_value as session_id,
                    param_user.value.string_value as fd_user_id
                    FROM `{self.DBPath()}`
                    CROSS JOIN UNNEST(event_params) AS param_app_version
                    CROSS JOIN UNNEST(event_params) AS param_log_version
                    CROSS JOIN UNNEST(event_params) AS param_session
                    CROSS JOIN UNNEST(event_params) AS param_user
                    {where_clause}
                    ORDER BY `fd_user_id`, `timestamp` ASC;
                """
        return query

    @staticmethod
    def _generateWhereClause(filters:DatasetFilterCollection) -> ParamaterizedClause:
        exclude : LiteralString

        sess_clause : Optional[LiteralString] = None
        sess_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.IDFilters.Sessions and len(filters.IDFilters.Sessions.AsSet) > 0:
            exclude = "NOT" if filters.IDFilters.Sessions.FilterMode == FilterMode.EXCLUDE else ""
            sess_clause = f"`session_id` {exclude} IN @session_list"
            sess_param.append(
                bigquery.ArrayQueryParameter(name="session_list", array_type="STRING", values=filters.IDFilters.Sessions.AsList)
            )

        users_clause : Optional[LiteralString] = None
        users_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.IDFilters.Players and len(filters.IDFilters.Players.AsSet) > 0:
            exclude = "NOT" if filters.IDFilters.Players.FilterMode == FilterMode.EXCLUDE else ""
            users_clause = f"`user_id` {exclude} IN @user_list"
            users_param.append(
                bigquery.ArrayQueryParameter(name="user_list", array_type="STRING", values=filters.IDFilters.Players.AsList)
            )

        times_clause : Optional[LiteralString] = None
        times_param  : List[bigquery.RangeQueryParameter | bigquery.ScalarQueryParameter] = []
        if filters.Sequences.Timestamps:
            if filters.Sequences.Timestamps.Min and filters.Sequences.Timestamps.Max:
                exclude = "NOT" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ""
                times_clause = f"`client_time` {exclude} BETWEEN @timestamp_range"
                times_param.append(
                    bigquery.RangeQueryParameter(name="timestamp_range", range_element_type="TIMESTAMP", start=filters.Sequences.Timestamps.Min, end=filters.Sequences.Timestamps.Max)
                )
            elif filters.Sequences.Timestamps.Min:
                exclude = "<" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                times_clause = f"`client_time` {exclude} @timestamp_min"
                times_param.append(
                    bigquery.ScalarQueryParameter(name="timestamp_min", type_="TIMESTAMP", value=filters.Sequences.Timestamps.Min)
                )
            else: # filters.Sequences.Timestamps.Max is not None
                exclude = ">" if filters.Sequences.Timestamps.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                times_clause = f"`client_time` {exclude} @timestamp_max"
                times_param.append(
                    bigquery.ScalarQueryParameter(name="timestamp_max", type_="TIMESTAMP", value=filters.Sequences.Timestamps.Max)
                )

        indices_clause : Optional[LiteralString] = None
        indices_param  : List[bigquery.ArrayQueryParameter] = []
        if filters.Sequences.SessionIndexFilter and len(filters.Sequences.SessionIndexFilter.AsSet) > 0:
            exclude = "NOT" if filters.Sequences.SessionIndexFilter.FilterMode == FilterMode.EXCLUDE else ""
            indices_clause = f"`event_session_index` {exclude} IN @sess_index_list"
            indices_param.append(
                bigquery.ArrayQueryParameter(name="sess_index_list", array_type="INT64", values=filters.Sequences.SessionIndexFilter.AsList)
            )

        log_clause : Optional[LiteralString] = None
        log_param  : List[BigQueryParameter] = []
        if version_filter.LogVersions:
            if isinstance(version_filter.LogVersions, SetFilter) and len(version_filter.LogVersions.AsSet) > 0:
                exclude = "NOT" if version_filter.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                log_clause = f"`log_version` {exclude} IN @log_versions"
                log_param.append(
                    bigquery.ArrayQueryParameter(name="log_versions", array_type="INT64", values=version_filter.LogVersions.AsList)
                )
            elif isinstance(version_filter.LogVersions, RangeFilter):
                if version_filter.LogVersions.Min and version_filter.LogVersions.Max:
                    exclude = "NOT" if version_filter.LogVersions.FilterMode == FilterMode.EXCLUDE else ""
                    log_clause = f"`log_version` {exclude} BETWEEN @log_version_min AND @log_version_max"
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value=str(version_filter.LogVersions.Min))
                    )
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value=str(version_filter.LogVersions.Max))
                    )
                elif version_filter.LogVersions.Min:
                    exclude = "<" if version_filter.LogVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    log_clause = f"`log_version` {exclude} @log_version_min"
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_min", type_="STRING", value=str(version_filter.LogVersions.Min))
                    )
                else: # version_filter.LogVersionFilter.Max is not None
                    exclude = ">" if version_filter.LogVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    log_clause = f"`log_version` {exclude} @log_version_max"
                    log_param.append(
                        bigquery.ScalarQueryParameter(name="log_version_max", type_="STRING", value=str(version_filter.LogVersions.Max))
                    )

        app_clause : Optional[LiteralString] = None
        app_param  : List[BigQueryParameter] = []
        if version_filter.AppVersions:
            if isinstance(version_filter.AppVersions, SetFilter) and len(version_filter.AppVersions.AsSet) > 0:
                exclude = "NOT" if version_filter.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                app_clause = f"`app_version` {exclude} IN @app_versions"
                app_param.append(
                    bigquery.ArrayQueryParameter(name="app_versions", array_type="INT64", values=version_filter.AppVersions.AsList)
                )
            elif isinstance(version_filter.AppVersions, RangeFilter):
                if version_filter.AppVersions.Min and version_filter.AppVersions.Max:
                    exclude = "NOT" if version_filter.AppVersions.FilterMode == FilterMode.EXCLUDE else ""
                    app_clause = f"`app_version` {exclude} BETWEEN @app_version_range"
                    app_param.append(
                        bigquery.RangeQueryParameter(name="app_version_range", range_element_type="INT64", start=version_filter.AppVersions.Min, end=version_filter.AppVersions.Max)
                    )
                elif version_filter.AppVersions.Min:
                    exclude = "<" if version_filter.AppVersions.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    app_clause = f"`app_version` {exclude} @app_version_min"
                    app_param.append(
                        bigquery.ScalarQueryParameter(name="app_version_min", type_="STRING", value=str(version_filter.AppVersions.Min))
                    )
                else: # version_filter.AppVersionFilter.Max is not None
                    exclude = ">" if version_filter.AppVersions.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    app_clause = f"`app_version` {exclude} @app_version_max"
                    app_param.append(
                        bigquery.ScalarQueryParameter(name="app_version_max", type_="STRING", value=str(version_filter.AppVersions.Max))
                    )

        branch_clause : Optional[LiteralString] = None
        branch_param  : List[BigQueryParameter] = []
        if version_filter.AppBranches:
            if isinstance(version_filter.AppBranches, SetFilter) and len(version_filter.AppBranches.AsSet) > 0:
                exclude = "NOT" if version_filter.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                app_clause = f"`app_branch` {exclude} IN @app_branchs"
                app_param.append(
                    bigquery.ArrayQueryParameter(name="app_branchs", array_type="INT64", values=version_filter.AppBranches.AsList)
                )
            elif isinstance(version_filter.AppBranches, RangeFilter):
                if version_filter.AppBranches.Min and version_filter.AppBranches.Max:
                    exclude = "NOT" if version_filter.AppBranches.FilterMode == FilterMode.EXCLUDE else ""
                    branch_clause = f"`app_branch` {exclude} BETWEEN @app_branch_range"
                    branch_param.append(
                        bigquery.RangeQueryParameter(name="app_branch_range", range_element_type="INT64", start=version_filter.AppBranches.Min, end=version_filter.AppBranches.Max)
                    )
                elif version_filter.AppBranches.Min:
                    exclude = "<" if version_filter.AppBranches.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    branch_clause = f"`app_branch` {exclude} @app_branch_min"
                    branch_param.append(
                        bigquery.ScalarQueryParameter(name="app_branch_min", type_="STRING", value=str(version_filter.AppBranches.Min))
                    )
                else: # version_filter.AppBranchFilter.Max is not None
                    exclude = ">" if version_filter.AppBranches.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    branch_clause = f"`app_branch` {exclude} @app_branch_max"
                    branch_param.append(
                        bigquery.ScalarQueryParameter(name="app_branch_max", type_="STRING", value=str(version_filter.AppBranches.Max))
                    )

        events_clause : Optional[LiteralString] = None
        events_param  : List[bigquery.ArrayQueryParameter] = []
        if event_filter.EventNames and len(event_filter.EventNames.AsSet) > 0:
            exclude = "NOT" if event_filter.EventNames.FilterMode == FilterMode.EXCLUDE else ""
            events_clause = f"`event_name` {exclude} IN @event_name_list"
            events_param.append(
                bigquery.ArrayQueryParameter(name="event_name_list", array_type="STRING", values=event_filter.EventNames.AsList)
            )

        codes_clause : Optional[LiteralString] = None
        codes_param  : List[BigQueryParameter] = []
        if event_filter.EventCodes:
            if isinstance(event_filter.EventCodes, SetFilter) and len(event_filter.EventCodes.AsSet) > 0:
                exclude = "NOT" if event_filter.EventCodes.FilterMode == FilterMode.EXCLUDE else ""
                codes_clause = f"`app_branch` {exclude} IN @app_branchs"
                codes_param.append(
                    bigquery.ArrayQueryParameter(name="app_branchs", array_type="INT64", values=event_filter.EventCodes.AsList)
                )
            elif isinstance(event_filter.EventCodes, RangeFilter):
                if event_filter.EventCodes.Min and event_filter.EventCodes.Max:
                    exclude = "NOT" if event_filter.EventCodes.FilterMode == FilterMode.EXCLUDE else ""
                    codes_clause = f"`app_branch` {exclude} BETWEEN @event_codes_range"
                    codes_param.append(
                        bigquery.RangeQueryParameter(name="event_codes_range", range_element_type="INT64", start=event_filter.EventCodes.Min, end=event_filter.EventCodes.Max)
                    )
                elif event_filter.EventCodes.Min:
                    exclude = "<" if event_filter.EventCodes.FilterMode == FilterMode.EXCLUDE else ">" # < if we're excluding this min, or > if we're including this min
                    codes_clause = f"`app_branch` {exclude} @event_codes_min"
                    codes_param.append(
                        bigquery.ScalarQueryParameter(name="event_codes_min", type_="STRING", value=str(event_filter.EventCodes.Min))
                    )
                else: # event_filter.EventCodeFilter.Max is not None
                    exclude = ">" if event_filter.EventCodes.FilterMode == FilterMode.EXCLUDE else "<" # > if we're excluding this max, or < if we're including this max
                    codes_clause = f"`app_branch` {exclude} @event_codes_max"
                    codes_param.append(
                        bigquery.ScalarQueryParameter(name="event_codes_max", type_="STRING", value=str(event_filter.EventCodes.Max))
                    )

        clause_list_raw : List[Optional[LiteralString]] = [sess_clause, users_clause, times_clause, indices_clause, log_clause, app_clause, branch_clause, events_clause, codes_clause]
        clause_list     : List[LiteralString]           = [clause for clause in clause_list_raw if clause is not None]
        where_clause    : LiteralString                 = f"WHERE {'\nAND '.join(clause_list)}" if len(clause_list) > 0 else ""

        params_collection = [sess_param, users_param, times_param, indices_param, log_param, app_param, branch_param, events_param, codes_param]
        params = list(chain.from_iterable(params_collection))

        return ParamaterizedClause(clause=where_clause, params=params)
