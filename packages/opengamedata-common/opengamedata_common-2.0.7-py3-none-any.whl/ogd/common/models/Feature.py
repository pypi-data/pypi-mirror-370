from typing import Any, Dict, List, Optional

from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.models.GameData import GameData

class Feature(GameData):
    """
    
    .. todo:: Add element to track the feature extractor version in some way.

    :param GameData: _description_
    :type GameData: _type_
    """
    def __init__(self, name:str, feature_type:str,
                 game_unit:Optional[str], game_unit_index:Optional[int],
                 app_id:str, user_id:Optional[str], session_id:str,
                 subfeatures:List[str], values:List[Any]):
        """_summary_

        :param name: _description_
        :type name: str
        :param feature_type: _description_
        :type feature_type: str
        :param game_unit: _description_
        :type game_unit: Optional[str]
        :param game_unit_index: _description_
        :type game_unit_index: Optional[int]
        :param app_id: _description_
        :type app_id: str
        :param user_id: _description_
        :type user_id: Optional[str]
        :param session_id: _description_
        :type session_id: str
        :param subfeatures: _description_
        :type subfeatures: List[str]
        :param values: _description_
        :type values: List[Any]
        """
        super().__init__(app_id=app_id, user_id=user_id, session_id=session_id)
        self._name = name
        self._feature_type = feature_type
        self._game_unit = game_unit
        self._game_unit_index = game_unit_index
        self._subfeatures = subfeatures
        self._values  = values

    def __str__(self) -> str:
        return f"Name: {self.Name}\tGame Unit: {self.GameUnit}{self.GameUnitIndex}\nValue: {self._values}\nPlayer: {self.PlayerID}\tSession: {self.SessionID}"

    def __repr__(self) -> str:
        return self.Name

    @staticmethod
    def ColumnNames() -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["name",   "feature_type", "game_unit",  "game_unit_index", 
                "app_id", "user_id",      "session_id", "subfeatures", "values"]

    @property
    def ColumnValues(self) -> List[str | int | List[Any] | None]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, Map, int, None]]
        """
        return [self.Name,  self.FeatureType, self.GameUnit,  self.GameUnitIndex,
                self.AppID, self.UserID,      self.SessionID, self.Subfeatures, self.Values]

    @property
    def ExportMode(self) -> ExportMode:
        if self.PlayerID == "*" and self.SessionID == "*":
            return ExportMode.POPULATION
        elif self.SessionID == "*":
            return ExportMode.PLAYER
        else:
            return ExportMode.SESSION

    @property
    def Name(self) -> str:
        return self._name

    @property
    def FeatureType(self) -> str:
        return self._feature_type

    @property
    def GameUnit(self) -> str:
        return self._game_unit or "*"

    @property
    def GameUnitIndex(self) -> str | int:
        return self._game_unit_index or "*"
    @property
    def CountIndex(self) -> str | int:
        return self.GameUnitIndex

    @property
    def Subfeatures(self) -> List[str]:
        return self._subfeatures

    @property
    def FeatureNames(self) -> List[str]:
        return [self.Name] + self._subfeatures

    @property
    def Values(self) -> List[Any]:
        """Ordered list of values from the feature.

        The first is the base value, and each value after corresponds to the subfeature in the same order in Subfeatures.

        :return: _description_
        :rtype: List[Any]
        """
        return self._values
    @property
    def FeatureValues(self) -> List[Any]:
        """Alias for `Values` property

        Ordered list of values from the feature.
        The first is the base value, and each value after corresponds to the subfeature in the same order in Subfeatures.

        :return: _description_
        :rtype: List[Any]
        """
        return self.Values

    @property
    def ValueMap(self) -> Dict[str, Any]:
        ret_val : Dict[str, Any]

        if len(self.Subfeatures) != len(self.Values):
            raise ValueError(f"For {self.Name}, number of subfeatures (+1) did not match number of values!")
        else:
            ret_val = {self.FeatureNames[i] : self.Values[i] for i in range(len(self.FeatureNames))}
        
        return ret_val
