"""
$Id: file.py 2494 2020-09-16 12:31:19Z pe $

EBAS I/O file
"""

from .check_metadata import EbasFileCheckMetadata
from .check_data import EbasFileCheckData
from .write import EbasFileWrite
from nilutility.datatypes import DataObject
try:
    # pylint: disable=W0611
    # W0611: Unused import
    # used by client classes
    from ebas.domain.entities.interface_ebas_io.io_from_domain \
        import EbasFileFromDomain  #@UnusedImport
except ImportError:
    from .from_domain import EbasFileFromDomain
from .read import EbasFileRead


class EbasFile(EbasFileCheckMetadata, EbasFileCheckData, EbasFileFromDomain,
               EbasFileRead, EbasFileWrite):
    # pylint: disable=W0223
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    This is a base class for all types of Ebas IO files (nasa_ames, xml, csv).
    Its an abstract, partial class.
    """
    pass

class EbasJoinedFile(EbasFile):
    """
    This is a base class for Ebas IO files which can have multiple metadata
    intervals (e.g. OPeNDAP, NetCDF).
    The join method for those objects will generate an new object of the same
    type with aggregated key metadata and the original file objects in the
    _metadata_intervals attribute. This attribute will be transparently
    accessible as a property method.
    """
    def __init__(self, metadata_intervals=None, *args, **kwargs):
        """
        Class initialization.
        """
        EbasFile.__init__(self, *args, **kwargs)
        self._metadata_intervals = metadata_intervals
        self._prepare_write = False  # avoid multiple cascading down to kids

    @property
    def metadata_intervals(self):
        """
        Property for metadata intervals.
        List of lists ([[start, end, metadata],...]
        This method makes using the original file object or a joined file
        object (with multiple intervals) completely transparent.
        """
        if self._metadata_intervals is None:
            if not self.sample_times:
                self._metadata_intervals = []
            else:
                self._metadata_intervals = [
                    [self.sample_times[0][0], self.sample_times[-1][1], self]]
        return self._metadata_intervals

    def get_metadata_set(self, element, string=False, exclude_aux=False):
        """
        Generates a set of different values for one metadata element (value of
        global metadata and all values per variable).
        If emement is a tuple, a list of combinations of metadata elements
        is returned.
        Overriden in order to take care of multiple metadata intervals.
        This method is meant to give "all different" values for a metadata
        element.
        Parameter:
            element     metadata element (string or dict)
            string      whether the elements should be reresented as str
            exclude_aux
                        do not report meatdata for auxiliary variables
        Returns:
            list (list with unique elements, i.e. set)
        """
        # Because metadata values can be unhashable objects (dict, DataObject),
        # this method must be implemented as a list, not as a set.

        def _add(x):
            if x not in set_: set_.append(x)

        # do the base method (look in my own metadata, if set
        set_ = super(EbasJoinedFile, self).get_metadata_set(
            element, string=string, exclude_aux=exclude_aux)

        # look recursivly in all metadata intervals (which do not refer to self)
        for fil in [elem[2] for elem in self.metadata_intervals
                    if elem[2] is not self]:
            for elem in fil.get_metadata_set(element, string, exclude_aux):
                _add(elem)
        return set_

    def prepare_write(self, open_file, *args, **kwargs):
        """
        Prepare the IO object for writing.
        Parameters:
            open_file  wheter the oputut file should be opened and the file
                       handle be returned. (Should net be done for certain
                       types of output objects (e.g. EbasNetCDF) or on the
                       atomic files within an EbasJoinedFile container)
            datadef    data definition (EBAS_1 or EBAS_1.1)
        Returns
            None
        """
        super(EbasJoinedFile, self).prepare_write(open_file, *args,
                                                  **kwargs)
        self._prepare_write = True  # avoid multiple cascading to kids
        for obj in [x[2] for x in self.metadata_intervals if x[2] != self]:
            # call intervall object's method (but without opening the files!
            obj.prepare_write(False, *args, **kwargs)
        self._prepare_write = False

    def setup_ebasmetadata(self, *args, **kwargs):
        # call base class method for self:
        super(EbasJoinedFile, self).setup_ebasmetadata(*args, **kwargs)
        if self._prepare_write:
            return  # avoid multiple cascading (prepare_write cascades already)
        for obj in [x[2] for x in self.metadata_intervals if x[2] != self]:
            # call intervall object's method
            obj.setup_ebasmetadata(*args, **kwargs)
        
    def set_timespec_metadata(self, *args, **kwargs):
        # call base class method for self:
        super(EbasJoinedFile, self).set_timespec_metadata(*args, **kwargs)
        if self._prepare_write:
            return  # avoid multiple cascading (prepare_write cascades already)
        for obj in [x[2] for x in self.metadata_intervals if x[2] != self]:
            # call intervall object's method
            obj.set_timespec_metadata(*args, **kwargs)

    def set_default_metadata(self, *args, **kwargs):
        # call base class method for self:
        super(EbasJoinedFile, self).set_default_metadata(*args, **kwargs)
        if self._prepare_write:
            return  # avoid multiple cascading (prepare_write cascades already)
        for obj in [x[2] for x in self.metadata_intervals if x[2] != self]:
            # call intervall object's method
            obj.set_default_metadata(*args, **kwargs)

    def consolidate_metadata(self, *args, **kwargs):
        # call base class method for self:
        super(EbasJoinedFile, self).consolidate_metadata(*args, **kwargs)
        if self._prepare_write:
            return  # avoid multiple cascading (prepare_write cascades already)
        for obj in [x[2] for x in self.metadata_intervals if x[2] != self]:
            # call intervall object's method
            obj.consolidate_metadata(*args, **kwargs)

    def union_projects(self):
        """
        Get a union of all projects in the file.
        Base implementation in EbasFileBase, but here overridden for adequate
        handling of joined files.
        Parameters:
            None
        Returns:
            list of project acronyms
        """
        if len(self.metadata_intervals) == 1 and \
                self.metadata_intervals[0][2] is self:
            return super(EbasJoinedFile, self).union_projects()
        return sorted(
            {prj
             for x in self.metadata_intervals
             for prj in x[2].union_projects()})

    def common_glob_metadata(self, other):
        """
        Calculate the common metadata of two objects (or variables of two
        objects).
        Parameters:
            other     the other object (for comparison of the metadata)
        Returns:
            DataObject containing the common metadata
        """
        # merge global metadata, generally intersection of both files
        new_metadata = DataObject()
        for key in set(list(self.metadata.keys()) + \
                       list(other.metadata.keys())):
            if self.metadata[key] == other.metadata[key]:
                new_metadata[key] = self.metadata[key]
            elif key in ('submitter', 'originator'):
                # submitter, originator: union of both files:
                # (don't use set() here, we want to keep the order as good as
                # possible
                new_metadata[key] = self.metadata[key] + \
                                    [x for x in other.metadata[key]
                                     if x not in self.metadata[key]]
            else:
                new_metadata[key] = None
        return new_metadata


    def common_var_metadata(self, other, vnum, glob_metadata):
        """
        Calculate the common metadata of two objects (or variables of two
        objects).
        Parameters:
            other     the other object (for comparison of the metadata)
            vnum      the variable numbers in the file which should be compared
            glob_metadata
                      global metadata for the new, joined file (only needed
        Returns:
            DataObject containing the common variable metadata
        """
        res = DataObject()
        # iterate over all keys in both file's global and per variable metadata:
        for key in set(list(self.metadata.keys()) + \
                       list(other.metadata.keys()) + \
                       list(self.variables[vnum].metadata.keys()) + \
                       list(other.variables[vnum].metadata.keys())):
            if self.get_meta_for_var(vnum, key) == \
               other.get_meta_for_var(vnum, key) and \
               self.get_meta_for_var(vnum, key) != glob_metadata[key]:
                # only set variable metadata when not equal global metadata
                # otherwise problem: e.g. regime code is None in this stage
                # (only set in set_default later), thus var metadata would be
                # set None here. Later default would be set to IMG in global
                # metadata, but var metadata would still be None -> wrong.
                res[key] = self.get_meta_for_var(vnum, key)
            elif key in ['submitter', 'originator']:
                # submitter, originator: union of both files:
                # (don't use set() here, we want to keep the order as good as
                # possible
                val = self.get_meta_for_var(vnum, key) + \
                      [x for x in other.get_meta_for_var(vnum, key)
                       if x not in self.get_meta_for_var(vnum, key)]
                if val != glob_metadata[key]:
                    res[key] = val
            elif key == 'revdate':
                # special case for revdate: use maximum
                val1 = self.get_meta_for_var(vnum, key)
                val2 = other.get_meta_for_var(vnum, key)
                if val1 and not val2 and val1 != glob_metadata[key]:
                    res[key] = val1
                elif val2 and not val1 and val2 != glob_metadata[key]:
                    res[key] = val2
                elif val1 and val2:
                    val = max(val1, val2)
                    if val != glob_metadata[key]:
                        res[key] = val
                # else: not set for variable
            # else: not set for variable
        return res

    def join(self, other):
        """
        Join self with other if possible.
        Default implementation in EbasFile: do not join. This is overridden for
        EbasJoinedFile.
        Parameters:
            other    other EbasIO object
        Returns
            New, joined EbasIO object
            None (no join possible)
        """
        # check if objects can be joined:
        # same variables, same setkeys, data interval can be joined
        if len(self.variables) != len(other.variables) or \
           self.get_metadata_list_per_var('setkey') != \
               other.get_metadata_list_per_var('setkey'):
            return None
        # make a new object of the same class then self:
        new = self.__class__(
            indexdb=self.indexdb, metadata_intervals=sorted(
                self.metadata_intervals + other.metadata_intervals))
        new.from_domain = self.from_domain
        new.metadata = self.common_glob_metadata(other)
        new.sample_times = self.sample_times + other.sample_times
        new.variables = []
        for vnum in range(len(self.variables)):
            var1 = self.variables[vnum]
            var2 = other.variables[vnum]
            metadata = self.common_var_metadata(other, vnum, new.metadata)
            new.variables.append(
                DataObject(
                    is_hex=var1.is_hex,
                    values_=var1.values_ + var2.values_,
                    flags=var1.flags + var2.flags,
                    flagcol=True,
                    metadata=metadata,
                    ))            
            # characteristics will be copied as "common_metadata" above
            # because same setkey will produce same characteristics for all
            # intervals
        return new

    def _var_fits_in_file(self, di_obj, time):  # pylint: disable-msg=R0911
        # R0911: Too many return statements
        #  --> clear to read (better then more complex if clauses
        """
        Check whether the variable fits in this file (either same submission
        or all metadata and the timesseries must be matching).
        This is a less strict implementation for EbasJoinedFile which overrides
        the EbasFileFromDomain._var_fits_in_file implementation.
        Parameters:
            di_obj      di object to be processed
            time        time inteval to be processed (start, end)
        Returns:
            True/False (fits / does not)
            overlap (DatetimeInterval) if it partly fits
        """
        return self._var_fits_in_file_general(di_obj, time)
