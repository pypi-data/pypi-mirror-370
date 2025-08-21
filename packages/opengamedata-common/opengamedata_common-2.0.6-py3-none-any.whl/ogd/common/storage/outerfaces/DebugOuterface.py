"""Module for a debugging outerface."""

# import standard libraries
import json
import logging
from typing import List, override, Set

# import OGD files
from ogd.common.configs.DataTableConfig import DataTableConfig
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class DebugOuterface(Outerface):
    """Outerface used for debugging purposes.

    Its destination is standard output; all values are output via print statements.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, table_config:DataTableConfig, export_modes:Set[ExportMode]):
        super().__init__(export_modes=export_modes, table_config=table_config)
        # self.Open()

    # *** IMPLEMENT ABSTRACTS ***

    @property
    def Connector(self) -> None:
        return None

    def _removeExportMode(self, mode:ExportMode):
        match mode:
            case ExportMode.EVENTS:
                self._display("No longer outputting raw event data to debug stream.")
            case ExportMode.DETECTORS:
                self._display("No longer outputting processed event data to debug stream.")
            case ExportMode.SESSION:
                self._display("No longer outputting session data to debug stream.")
            case ExportMode.PLAYER:
                self._display("No longer outputting player data to debug stream.")
            case ExportMode.POPULATION:
                self._display("No longer outputting population data to debug stream.")

    def _writeGameEventsHeader(self, header:List[str]) -> None:
        self._display("Raw events header:")
        self._display(header)

    def _writeAllEventsHeader(self, header:List[str]) -> None:
        self._display("Processed events header:")
        self._display(header)

    def _writeSessionHeader(self, header:List[str]) -> None:
        self._display("Sessions header:")
        self._display(header)

    def _writePlayerHeader(self, header:List[str]) -> None:
        self._display("Player header:")
        self._display(header)

    def _writePopulationHeader(self, header:List[str]) -> None:
        self._display("Population header:")
        self._display(header)

    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        self._display("Raw event data:")
        _lengths = [len(elem) for elem in events]
        self._display(f"{len(events)} raw events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        self._display("Processed event data:")
        _lengths = [len(elem) for elem in events]
        self._display(f"{len(events)} processed events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writeSessionLines(self, session_lines:List[ExportRow]) -> None:
        self._display("Session data:")
        _lengths = [len(elem) for elem in session_lines]
        self._display(f"{len(session_lines)} events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writePlayerLines(self, player_lines:List[ExportRow]) -> None:
        self._display("Player data:")
        _lengths = [len(elem) for elem in player_lines]
        self._display(f"{len(player_lines)} events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    def _writePopulationLines(self, population_lines:List[ExportRow]) -> None:
        self._display("Population data:")
        _lengths = [len(elem) for elem in population_lines]
        self._display(f"{len(population_lines)} events, average length {sum(_lengths) / len(_lengths) if len(_lengths) > 0 else 'N/A'}")

    @override
    def _writeMetadata(self, dataset_schema:DatasetSchema):
        self._display("Metadata:")
        self._display(json.dumps(dataset_schema.AsMetadata))
    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _display(self, msg):
        Logger.Log(f"DebugOuterface: {msg}", logging.DEBUG)
