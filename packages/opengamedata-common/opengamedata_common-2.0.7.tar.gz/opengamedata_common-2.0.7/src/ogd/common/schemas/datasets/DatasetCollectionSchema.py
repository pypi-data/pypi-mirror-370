# standard imports
from typing import Any, Dict, Final, Optional, Self

# ogd imports
from ogd.common.schemas.Schema import Schema

# local imports
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.utils.typing import Map

# Simple class to manage a mapping of dataset names to dataset schemas.
class DatasetCollectionSchema(Schema):
    """Simple class to manage a mapping of dataset names to dataset schemas.

    This exists separately from `DatasetCollectionSchema` because there is,
    in turn, a map of game IDs to these collections.
    It's obviously more convenient code-wise not to have a dict of dicts of datasets directly in `DatasetCollectionSchema`.
    """
    _DEFAULT_DATASETS : Final[Dict[str, DatasetSchema]] = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, datasets:Optional[Dict[str, DatasetSchema]], other_elements:Dict[str, Any]):
        """Constructor for the `DatasetCollectionSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "GAME_NAME_20250101_to_20250131": {
                "ogd_revision": "1234567",
                "start_date": "01/01/2025",
                "end_date": "01/31/2025",
                ...
                "all_events_template": "path/to/template
            },
            "GAME_NAME_20250201_to_20250228": {
                ...
            },
            ...
        },
        ```

        :param name: _description_
        :type name: str
        :param datasets: _description_
        :type datasets: Optional[Dict[str, DatasetSchema]]
        :param other_elements: _description_
        :type other_elements: Dict[str, Any]
        """
        unparsed_elements : Map = other_elements or {}

        self._datasets : Dict[str, DatasetSchema] = datasets or self._parseDatasets(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def Datasets(self) -> Dict[str, DatasetSchema]:
        return self._datasets

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "DatasetCollectionSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DatasetCollectionSchema
        """
        return DatasetCollectionSchema(name=name, datasets=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetCollectionSchema":
        return DatasetCollectionSchema(
            name="DefaultDatasetCollectionSchema",
            datasets=cls._DEFAULT_DATASETS,
            other_elements={}
        )

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseDatasets(unparsed_elements:Map) -> Dict[str, DatasetSchema]:
        ret_val : Dict[str, DatasetSchema]

        ret_val = {
            key : DatasetSchema.FromDict(name=key, unparsed_elements=val)
            for key,val in unparsed_elements.items()
        }

        return ret_val

    # *** PRIVATE METHODS ***
