from typing import Any, Dict

from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.storage.interfaces.Interface import Interface
from ogd.common.storage.interfaces.CSVInterface import CSVInterface
from ogd.common.storage.interfaces.BigQueryInterface import BigQueryInterface
from ogd.common.storage.interfaces.BQFirebaseInterface import BQFirebaseInterface
from ogd.common.storage.interfaces.MySQLInterface import MySQLInterface
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema

class InterfaceFactory:
    @staticmethod
    def FromConfig(config:DataTableConfig, fail_fast:bool)-> Interface:
        if config.StoreConfig:
            match (config.StoreConfig.Type.upper()):
                # case "MYSQL":
                #     return MySQLInterface(config=config, fail_fast=fail_fast)
                # case "FIREBASE":
                #     return BQFirebaseInterface(config=config, fail_fast=fail_fast)
                case "BIGQUERY":
                    return BigQueryInterface(config=config, fail_fast=fail_fast)
                case "FILE" | "CSV" | "TSV":
                    return CSVInterface(config=config, fail_fast=fail_fast)
                case _:
                    raise ValueError(f"Could not generate Interface from DataTableConfig, the underlying StoreConfig was unrecognized type {config.StoreConfig.Type}!")
        else:
            raise ValueError("Could not generate Interface from DataTableConfig, the underlying StoreConfig was null!")
    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], fail_fast:bool)-> Interface:
        config = DataTableConfig.FromDict(name=name, unparsed_elements=all_elements)
        return InterfaceFactory.FromConfig(config=config, fail_fast=fail_fast)
