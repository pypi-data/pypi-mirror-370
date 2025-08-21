"""
ebas/domain/masterdata/st.py
$Id: st.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for Flags

This module implements the class EbasMasterST.

History:
V.1.0.0  2014-02-25  pe  initial version

"""

from __future__ import absolute_import
# otherwise re is imported relative as masterdata.re
import re
import six
from .offline_masterdata import STOfflineMasterData
from .base import EbasMasterBase

class EbasMasterST(EbasMasterBase, STOfflineMasterData):
    """
    Domain Class for station masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for ST (stations)
    # Those are fallback values, will be read from database as soon as possible.
    STOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read st masterdata if dbh is provided.
        """
        STOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def lookup_stationcode(cls, match_strings):
        """
        Lookup a station code specification using regular expression match.
        Parameters:
            stationcode_string(s)    string with station code match string
                                     or list of strings
        Returns:
            generator, station dictionaries
        """
        if isinstance(match_strings, six.string_types):
            match_strings = [match_strings]
        for st_ in sorted(cls.META.keys()):
            for match_string in match_strings:
                if re.match('^' + match_string + '$', st_):
                    yield cls.META[st_]

