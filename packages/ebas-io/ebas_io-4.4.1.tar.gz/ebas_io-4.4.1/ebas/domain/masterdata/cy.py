"""
$Id: cy.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for component synonym masterdata

This module implements the class EbasMasterCY.

"""

from .. import EbasDomainError
from .offline_masterdata import CYOfflineMasterData
from .co import EbasMasterCO
from .base import EbasMasterBase

class EbasMasterCY(EbasMasterBase, CYOfflineMasterData):
    """
    Domain Class for component synonym masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for CO (components)
    # Those are fallback values, will be read from database as soon as possible.
    CYOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        CYOfflineMasterData.__init__(self)
        self._co = EbasMasterCO(dbh)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def lookup_synonym_strict(self, name, case_sensitive=True,
                              only_historic=False):
        """
        Lookup a strict synonym.
        Try CO_COMP_NAME first, then try strict synonyms, at last try case
        insensitive Lookup Name search (strict).
        Parameters:
            name     string with component name that should be identified
        Returns:
            CO_COMP_NAME (must always be max hit when using strict synonyms!)
        Raises:
            DoaminError if not found
            RuntimeError when strictness is inconsistent
        """
        try:
            return self._co[name].CO_COMP_NAME
        except KeyError:
            pass

        # lookup case sensitive
        hits = [x for x in list(self.__class__.META.keys())
                if any(
                    [True for y in self.__class__.META[x]
                     if y['CY_STRICT'] == 1 and y['CY_SYNONYM'] == name and
                        (only_historic == False or \
                             y['CN_SCHEMA'] == 'Historic EBAS Name')])]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            raise RuntimeError()

        if case_sensitive == False:
            # lookup case insensitive
            hits = [x for x in list(self.__class__.META.keys())
                    if any(
                        [True for y in self.__class__.META[x]
                         if y['CY_STRICT'] == 1 and \
                            y['CN_SCHEMA'] == 'Lookup Name' and \
                            y['CY_SYNONYM'].lower() == name.lower()])]
            # special cases: case insensitive lookup led to multiple hits
            # e.g.: co and CO
            if len(hits) > 1:
                amb = ["{} ({})".format(y['CY_SYNONYM'], y['CO_COMP_NAME'])
                       for x in list(self.__class__.META.values()) for y in x
                       if y['CY_STRICT'] == 1 and \
                          y['CN_SCHEMA'] == 'Lookup Name' and \
                          y['CY_SYNONYM'].lower() == name.lower()]
                raise EbasDomainError(
                    "component lookup name '{}' is ambiguous for case insensitive "
                    "lookup - may be {}".format(name, ', '.join(amb)))
            if len(hits) == 1:
                return hits[0]
        raise EbasDomainError("unknown component '{}'".format(name))

    @staticmethod
    def get_schema_ordered(cy_list):
        """
        Get an ordered list of elements with schema.
        """
        order = ('CAS Number', 'IUPAC Name', 'Historic EBAS Name',
                 'Molecular Formula', 'Condensed Formula', 'Lookup Name')
        retlist = []
        for elem in order:
            synlist = []
            for syn in cy_list:
                # there may be actually more then one synonym for one schema and
                # one component...
                # so make a list and sort it afterwards
                if syn['CN_SCHEMA'] == elem:
                    synlist.append(syn)
            retlist += sorted(synlist, key=lambda x: x['CY_SYNONYM'])
        synlist = []
        for syn in cy_list:
            # other synonyms with schema: sort by schama, synonym
            if syn['CN_SCHEMA'] is not None and syn['CN_SCHEMA'] not in order:
                synlist.append(syn)
        retlist += sorted(synlist,
                          key=lambda x: (x['CN_SCHAMA'], x['CY_SYNONYM']))
        return retlist

    @staticmethod
    def get_noschema_ordered(cy_list):
        """
        Get an ordered list of elements without schema.
        """
        return sorted([x for x in cy_list if x['CN_SCHEMA'] is None],
                      key=lambda x: x['CY_SYNONYM'])

    @staticmethod
    def get_all_ordered(cy_list):
        """
        Get an ordered list of elements without schema.
        """
        return EbasMasterCY.get_schema_ordered(cy_list) + \
            EbasMasterCY.get_noschema_ordered(cy_list)
