"""
$Id: base.py 2088 2018-06-29 13:46:38Z pe $

Base class for EBAS Masterdata Classes
"""

class EbasMasterBase(object):
    """
    Domain Class for statistics codes masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling statistics codes and checking them against master data.
    Statistics codes master data are retrieved from database or from offline
    storage when no database access is possible.
    """

    def __getitem__(self, key):
        """
        Allows dictionary like access to metadata
        """
        return self.__class__.META[key]

    def __iter__(self):
        """
        Iterator for statistics codes masterdata
        """
        for key in sorted(self.__class__.META.keys()):
            yield self.__class__.META[key]

