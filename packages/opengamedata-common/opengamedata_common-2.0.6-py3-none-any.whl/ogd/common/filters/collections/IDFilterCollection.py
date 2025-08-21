## import standard libraries
from typing import List, Optional, Set, Tuple
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode

class IDFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self,
                 session_filter : Optional[SetFilter[str] | NoFilter] = None,
                 player_filter  : Optional[SetFilter[str] | NoFilter] = None,
                 app_filter     : Optional[SetFilter[str] | NoFilter] = None):
        self._session_filter : SetFilter[str] | NoFilter = session_filter or NoFilter()
        self._player_filter  : SetFilter[str] | NoFilter = player_filter  or NoFilter()
        self._app_filter     : SetFilter[str] | NoFilter = app_filter     or NoFilter()

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.Sessions or self.Players:
            _app_str = f"app(s) {self.AppIDs}" if self.AppIDs else None
            _sess_str = f"session(s) {self.Sessions}" if self.Sessions else None
            _ply_str = f"player(s) {self.Players}" if self.Players else None
            _ver_strs = ", ".join([elem for elem in [_app_str, _sess_str, _ply_str] if elem is not None])
            ret_val = f"event filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.Sessions or self.Players:
            _app_str = f"app(s) {self.AppIDs}" if self.AppIDs else None
            _sess_str = f"session(s) {self.Sessions}" if self.Sessions else None
            _ply_str = f"player(s) {self.Players}" if self.Players else None
            _ver_strs = " ^ ".join([elem for elem in [_app_str, _sess_str, _ply_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def Sessions(self) -> SetFilter[str] | NoFilter:
        return self._session_filter
    @Sessions.setter
    def Sessions(self, included_sessions:Optional[SetFilter | NoFilter | Set[str] | List[str] | Tuple[str] | str]) -> None:
        if included_sessions is None or isinstance(included_sessions, NoFilter):
            self._app_filter = NoFilter()
        else:
            self._session_filter = SetFilter[str](mode=self.Sessions.FilterMode, set_elements=included_sessions)

    @property
    def Players(self) -> SetFilter[str] | NoFilter:
        return self._player_filter
    @Players.setter
    def Players(self, included_players:Optional[SetFilter | NoFilter | Set[str] | List[str] | Tuple[str] | str]) -> None:
        if included_players is None or isinstance(included_players, NoFilter):
            self._app_filter = NoFilter()
        else:
            self._player_filter = SetFilter[str](mode=self.Players.FilterMode, set_elements=included_players)

    @property
    def AppIDs(self) -> SetFilter[str] | NoFilter:
        return self._app_filter
    @AppIDs.setter
    def AppIDs(self, included_apps:Optional[SetFilter | NoFilter | Set[str] | List[str] | Tuple[str] | str]) -> None:
        if included_apps is None or isinstance(included_apps, NoFilter):
            self._app_filter = NoFilter()
        else:
            self._app_filter = SetFilter[str](mode=self.AppIDs.FilterMode, set_elements=included_apps)

    @property
    def any(self) -> bool:
        return self.Sessions.Active or self.Players.Active

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
