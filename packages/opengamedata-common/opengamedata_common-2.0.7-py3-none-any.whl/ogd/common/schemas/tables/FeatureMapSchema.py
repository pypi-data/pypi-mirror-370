"""EventTableSchema Module"""
# import standard libraries
from typing import Dict, Optional, Self

# import local files
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema, ColumnMapElement
from ogd.common.utils.typing import Map

## @class TableSchema
class FeatureMapSchema(ColumnMapSchema):
    """Dumb struct to hold useful info about the structure of database data for a particular game.

    This includes the indices of several important database columns, the names
    of the database columns, the max and min levels in the game, and a list of
    IDs for the game sessions in the given requested date range.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 feature_name:Optional[ColumnMapElement], feature_type:Optional[ColumnMapElement],
                 game_unit:Optional[ColumnMapElement],    game_unit_index:Optional[ColumnMapElement],
                 app_id:Optional[ColumnMapElement],       user_id:Optional[ColumnMapElement],         session_id:Optional[ColumnMapElement],
                 subfeatures:Optional[ColumnMapElement],  values:Optional[ColumnMapElement],
                 other_elements:Optional[Map]=None):
        """Constructor for the TableSchema class.
        
        If optional params are not given, data is searched for in `other_elements`.

        The structure is assumed to be as follows:

        ```python
        
            "feature_type"    : "feature_type",
            "game_unit"       : "game_unit",
            "game_unit_index" : "game_unit_index",
            "app_id"          : null,
            "user_id"         : "user_id",
            "session_id"      : "session_id",
            "subfeatures"     : "subfeatures",
            "values"          : "values",
        }
        ```

        :param name: _description_
        :type name: str
        :param feature_type: _description_
        :type feature_type: Optional[str]
        :param game_unit: _description_
        :type game_unit: Optional[ColumnMapElement]
        :param game_unit_index: _description_
        :type game_unit_index: Optional[ColumnMapElement]
        :param app_id: _description_
        :type app_id: Optional[ColumnMapElement]
        :param user_id: _description_
        :type user_id: Optional[ColumnMapElement]
        :param session_id: _description_
        :type session_id: Optional[ColumnMapElement]
        :param subfeatures: _description_
        :type subfeatures: Optional[ColumnMapElement]
        :param values: _description_
        :type values: Optional[ColumnMapElement]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._feature_name    : ColumnMapElement = feature_name    or self._parseFeatureName(unparsed_elements=unparsed_elements)
        self._feature_type    : ColumnMapElement = feature_type    or self._parseFeatureType(unparsed_elements=unparsed_elements)
        self._game_unit       : ColumnMapElement = game_unit       or self._parseGameUnit(unparsed_elements=unparsed_elements)
        self._game_unit_index : ColumnMapElement = game_unit_index or self._parseGameUnitIndex(unparsed_elements=unparsed_elements)
        self._subfeatures     : ColumnMapElement = subfeatures     or self._parseSubfeatures(unparsed_elements=unparsed_elements)
        self._values          : ColumnMapElement = values          or self._parseValues(unparsed_elements=unparsed_elements)

        super().__init__(name=name, app_id=app_id, user_id=user_id, session_id=session_id,
                         other_elements=unparsed_elements)

    @property
    def FeatureNameColumn(self) -> ColumnMapElement:
        return self._feature_name

    @property
    def FeatureTypeColumn(self) -> ColumnMapElement:
        return self._feature_type

    @property
    def GameUnitColumn(self) -> ColumnMapElement:
        return self._game_unit

    @property
    def GameUnitIndexColumn(self) -> ColumnMapElement:
        return self._game_unit_index

    @property
    def SubfeaturesColumn(self) -> ColumnMapElement:
        return self._subfeatures

    @property
    def ValuesColumn(self) -> ColumnMapElement:
        return self._values

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def Default(cls) -> "FeatureMapSchema":
        return FeatureMapSchema(
            name="DefaultEventTableSchema",
            feature_name="feature_name",
            feature_type="feature_type",
            game_unit="game_unit",
            game_unit_index="game_unit_index",
            app_id="app_id",
            user_id="user_id",
            session_id="session_id",
            subfeatures="subfeatures",
            values="values",
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "FeatureMapSchema":
        """Function to generate an EventMapSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "session_id"           : "session_id",
            "app_id"               : null,
            "timestamp"            : "client_time",
            "event_name"           : "event_name",
            "event_data"           : "event_data",
            "event_source"         : "event_source",
            "app_version"          : "app_version",
            "app_branch"           : "app_branch",
            "log_version"          : "log_version",
            "time_offset"          : "client_offset",
            "user_id"              : "user_id",
            "user_data"            : "user_data",
            "game_state"           : "game_state",
            "event_sequence_index" : "event_sequence_index"
        }
        ```

        The specific handling of the column map will be determined by the specific TableSchema subclass on which the FromDict feature is called.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Map
        :param key_overrides: _description_, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :param default_override: _description_, defaults to None
        :type default_override: Optional[Self], optional
        :return: _description_
        :rtype: EventMapSchema
        """
        return FeatureMapSchema(name=name, feature_name=None, feature_type=None,
                                game_unit=None, game_unit_index=None,
                                app_id=None, user_id=None, session_id=None,
                                subfeatures=None, values=None,
                                other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseFeatureName(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["feature_name", "name", "feature"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseFeatureType(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["feature_type", "type"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseGameUnit(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_unit", "prefix"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseGameUnitIndex(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["game_unit_index", "unit", "level"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseSubfeatures(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["subfeatures"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )

    @staticmethod
    def _parseValues(unparsed_elements:Map) -> Optional[ColumnMapElement]:
        return ColumnMapSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["values", "value"],
            to_type=[str, list, dict],
            default_value=None,
            remove_target=False
        )
