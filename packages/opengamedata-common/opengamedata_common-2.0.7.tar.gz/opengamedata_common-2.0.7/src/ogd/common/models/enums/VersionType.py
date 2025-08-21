"""VersionType Module
"""

# import standard libraries
from enum import IntEnum

class VersionType(IntEnum):
    """Enum representing the different kinds of versioning in OpenGameData.

    Namely:

    * Log Version
    * App Version
    * App Branch

    :param IntEnum: _description_
    :type IntEnum: _type_
    :return: _description_
    :rtype: _type_
    """
    LOG = 1
    APP = 2
    BRANCH = 3

    def __str__(self):
        return self.name
