## import standard libraries
from typing import List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair, Version

class VersioningFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self,
                 log_ver_filter : Optional[SetFilter[Version] | RangeFilter[Version] | NoFilter] = None,
                 app_ver_filter : Optional[SetFilter[Version] | RangeFilter[Version] | NoFilter] = None,
                 branch_filter  : Optional[SetFilter[str] | NoFilter]                            = None):
        """Constructor for the VersioningFilter structure.

        Accepts a collection of filters to be applied on versioning of data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param log_ver_filter: The filter to apply to log version, defaults to NoFilter()
        :type log_ver_filter: LogFilterType
        :param app_ver_filter: The filter to apply to app version, defaults to NoFilter()
        :type app_ver_filter: VersionFilterType
        :param branch_filter: The filter to apply to app branch, defaults to NoFilter()
        :type branch_filter: BranchFilterType
        """
        self._log_filter    : SetFilter[Version] | RangeFilter[Version] | NoFilter = log_ver_filter or NoFilter()
        self._app_filter    : SetFilter[Version] | RangeFilter[Version] | NoFilter = app_ver_filter or NoFilter()
        self._branch_filter : SetFilter[str] | NoFilter                            = branch_filter  or NoFilter()

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.LogVersions or self.AppVersions or self.AppBranches:
            _log_str = f"log version(s) {self.LogVersions}" if self.LogVersions else None
            _app_str = f"app version(s) {self.AppVersions}" if self.AppVersions else None
            _bnc_str = f"app branch(es) {self.AppBranches}"  if self.AppBranches else None
            _ver_strs = ", ".join([elem for elem in [_log_str, _app_str, _bnc_str] if elem is not None])
            ret_val = f"versioning filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.LogVersions or self.AppVersions or self.AppBranches:
            _log_str = f"log version(s) {self.LogVersions}" if self.LogVersions else None
            _app_str = f"app version(s) {self.AppVersions}" if self.AppVersions else None
            _bnc_str = f"app branch(es) {self.AppBranches}"  if self.AppBranches else None
            _ver_strs = " ^ ".join([elem for elem in [_log_str, _app_str, _bnc_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def LogVersions(self) -> Filter[Version]:
        return self._log_filter
    @LogVersions.setter
    def LogVersions(self, allowed_versions:Optional[SetFilter[Version] | RangeFilter[Version] | NoFilter | List[Version] | Set[Version] | slice | Pair[Version, Version]]) -> None:
        if allowed_versions is None or isinstance(allowed_versions, NoFilter):
            self._log_filter = NoFilter()
        elif isinstance(allowed_versions, Filter):
            self._log_filter = allowed_versions
        elif isinstance(allowed_versions, list) or isinstance(allowed_versions, set):
            self._log_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_versions))
        elif isinstance(allowed_versions, slice):
            self._log_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, range_slice=allowed_versions)
        elif isinstance(allowed_versions, tuple):
            self._log_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_versions[0], maximum=allowed_versions[1])

    @property
    def AppVersions(self) -> Filter[Version]:
        return self._app_filter
    @AppVersions.setter
    def AppVersions(self, allowed_versions:Optional[SetFilter[Version] | RangeFilter[Version] | NoFilter | List[Version] | Set[Version] | slice | Pair[Version, Version]]) -> None:
        if allowed_versions is None or isinstance(allowed_versions, NoFilter):
            self._app_filter = NoFilter()
        elif isinstance(allowed_versions, Filter):
            self._app_filter = allowed_versions
        elif isinstance(allowed_versions, list) or isinstance(allowed_versions, set):
            self._app_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_versions))
        elif isinstance(allowed_versions, slice):
            self._app_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, range_slice=allowed_versions)
        elif isinstance(allowed_versions, tuple):
            self._app_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_versions[0], maximum=allowed_versions[1])

    @property
    def AppBranches(self) -> Filter[str]:
        return self._branch_filter
    @AppBranches.setter
    def AppBranches(self, allowed_branches:Optional[SetFilter[str] | NoFilter | List[str] | Set[str]]) -> None:
        if allowed_branches is None or isinstance(allowed_branches, NoFilter):
            self._branch_filter = NoFilter()
        elif isinstance(allowed_branches, SetFilter):
            self._branch_filter = allowed_branches
        elif isinstance(allowed_branches, list) or isinstance(allowed_branches, set):
            self._branch_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(allowed_branches))

    @property
    def any(self) -> bool:
        return self.LogVersions.Active or self.AppVersions.Active or self.AppBranches.Active

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
