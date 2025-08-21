from pathlib import Path
from typing import Any, Dict, Optional

from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.utils.fileio import loadJSONFile

class TableSchemaFactory:
    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any])-> TableSchema:
        table_type = str(all_elements.get("table_type", "NOT FOUND"))
        match (table_type.upper()):
            case "EVENT":
                return EventTableSchema.FromDict(name=name, unparsed_elements=all_elements)
            case "FEATURE":
                return FeatureTableSchema.FromDict(name=name, unparsed_elements=all_elements)
            case _:
                raise ValueError(f"Could not generate TableSchema from dictionary, table_type had invalid value {table_type}")

    @staticmethod
    def FromFile(filename:str, path:Optional[Path|str]=None)-> TableSchema:
        path = path or TableSchema._DEFAULT_SCHEMA_PATH
        all_elements = loadJSONFile(filename=filename, path=Path(path))
        table_type = str(all_elements.get("table_type", "NOT FOUND"))
        match (table_type.upper()):
            case "EVENT":
                return EventTableSchema.FromDict(name=filename, unparsed_elements=all_elements)
            case "FEATURE":
                return FeatureTableSchema.FromDict(name=filename, unparsed_elements=all_elements)
            case _:
                raise ValueError(f"Could not generate TableSchema from dictionary, table_type had invalid value {table_type}")