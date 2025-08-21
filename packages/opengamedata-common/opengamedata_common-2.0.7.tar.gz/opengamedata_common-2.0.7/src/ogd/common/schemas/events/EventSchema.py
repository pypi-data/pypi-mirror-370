# import standard libraries
import logging
from typing import Any, Dict, Final, Optional, Self
# import local files
from ogd.common.schemas.events.DataElementSchema import DataElementSchema
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class EventSchema(Schema):
    """
    Dumb struct to contain a specification of an Event in a LoggingSpecificationSchema file.

    These essentially are just a description of the event, and a set of elements in the EventData attribute of the Event.
    """
    _DEFAULT_DESCRIPTION : Final[str] = "Default event schema object. Does not relate to any actual data."
    _DEFAULT_EVENT_DATA  : Final[Dict[str, DataElementSchema]] = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, description:Optional[str], event_data:Optional[Dict[str, DataElementSchema]], other_elements:Optional[Map]=None):
        """Constructor for the `EventSchema` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "description": "Description of what the event is and when it occurs.",
            "event_data": {
                "data_element_name": {
                "type": "bool",
                "description": "Description of what the data element means or represents."
                }
            }
        },
        ```

        :param name: _description_
        :type name: str
        :param description: _description_
        :type description: Optional[str]
        :param event_data: _description_
        :type event_data: Optional[Dict[str, DataElementSchema]]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._description : str                          = description or self._parseDescription(unparsed_elements=unparsed_elements)
        self._event_data  : Dict[str, DataElementSchema] = event_data  or self._parseEventDataElements(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def Description(self) -> str:
        return self._description

    @property
    def EventData(self) -> Dict[str, DataElementSchema]:
        return self._event_data

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        return "\n\n".join([
            f"### **{self.Name}**",
            self.Description,
            "#### Event Data",
            "\n".join(
                  [elem.AsMarkdown for elem in self.EventData.values()]
                + (["- Other Elements:"] +
                   [f"  - **{elem_name}**: {elem_desc}" for elem_name,elem_desc in self.NonStandardElements]
                  ) if len(self.NonStandardElements) > 0 else []
            )
        ])

    @property
    def AsMarkdownTable(self) -> str:
        ret_val = [
            f"### **{self.Name}**",
            f"{self.Description}",
            "#### Event Data",
            "\n".join(
                ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                 "| ---      | ---      | ---             | ---         |"]
              + [elem.AsMarkdownRow for elem in self.EventData.values()]
            ),
        ]
        if len(self.NonStandardElements) > 0:
            ret_val.append("#### Other Elements")
            ret_val.append(
                "\n".join( [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.NonStandardElements] )
            )
        return "\n\n".join(ret_val)

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "EventSchema":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: EventSchema
        """
        return EventSchema(name=name, description=None, event_data=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "EventSchema":
        return EventSchema(
            name="DefaultEventSchema",
            description=cls._DEFAULT_DESCRIPTION,
            event_data=cls._DEFAULT_EVENT_DATA,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseEventDataElements(unparsed_elements:Map):
        ret_val : Dict[str, DataElementSchema]
        event_data : Dict[str, Any] = EventSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["event_data"],
            to_type=dict,
            default_value=EventSchema._DEFAULT_EVENT_DATA,
            remove_target=True
        )
        if isinstance(event_data, dict):
            ret_val = {
                name : DataElementSchema.FromDict(name=name, unparsed_elements=elems)
                for name,elems in event_data.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"event_data was unexpected type {type(event_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDescription(unparsed_elements:Map):
        return EventSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=EventSchema._DEFAULT_DESCRIPTION,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
