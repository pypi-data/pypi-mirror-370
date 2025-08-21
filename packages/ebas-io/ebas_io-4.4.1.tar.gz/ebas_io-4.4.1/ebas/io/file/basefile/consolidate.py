"""
ebas/io/base.py
$Id: consolidate.py 2731 2021-11-11 00:04:05Z pe $

Base classes for (file) I/O.

"""

import datetime
from nilutility.datatypes import Histogram
from .base import EbasFileBase
from ..base import FLAGS_ONE_OR_ALL, FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE, \
    FLAGS_AS_IS, \
    SUPPRESS_SORT_VARIABLES, SUPPRESS_METADATA_OCCURRENCE




class EbasFileConsolidate(EbasFileBase):  # pylint: disable=W0223
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Partial class for EbasFile (Base class for file objects).
    This part handles file consolidation (standardized reformatting before
    output)
    """

    def consolidate_metadata(self, flags=FLAGS_ONE_OR_ALL, suppress=0):
        """
        Optimize the metadata structure of the object.
        - Order variables
        - Move attibutes between global (NNCOM) and variable specific (VNAME)
        - Choose the maximum revdate of all variables and set as file revdate
        - Eliminate redundant flag columns
        - Generate the filename for metadata (according to all other metadata)
        Parameters:
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
            suppress      suppress selected consolidations (bitfield):
                              SUPPRESS_SORT_VARIABLES
                              SUPPRESS_METADATA_OCCURRENCE
        Returns:
            None
        """
        # set reference date if not set:
        if not self.metadata.reference_date and self.sample_times:
            self.metadata.reference_date = \
                datetime.datetime(self.sample_times[0][1].year, 1, 1)

        self._set_method_analytical()

        # strict_gloabl and SUPPRESS_METADATA_OCCURRENCE is a contradiction
        if self.strict_global and suppress & SUPPRESS_METADATA_OCCURRENCE:
            suppress &= ~SUPPRESS_METADATA_OCCURRENCE
            self.logger.warning(
                "SUPPRESS_METADATA_OCCURRENCE is overruled by strict_global")
        if not suppress & SUPPRESS_METADATA_OCCURRENCE:
            for key in self.metadata.keys():
                if key in ('title', 'revdate', 'characteristics', 'qa'):
                    # title: is a per variable metadata element
                    # revdate: special behaviour, see _consolidate_revdate()
                    # characteristics: maybe implement special behaviour later
                    # qa: special behaviour, see _consolidate_qa()
                    continue
                self._consolidate_metadata_occ(key)
        self._consolidate_revdate()
        if not suppress & SUPPRESS_METADATA_OCCURRENCE:
            self._consolidate_qa()
        if not suppress & SUPPRESS_SORT_VARIABLES:
            self._sort_variables()
        # set proper revdate
        self._consolidate_flagcolumns(flags)
        self._consolidate_title()
        self.gen_filename()

    def _sort_variables(self):
        """
        Resort variables according to standard.
        Sort order:
            A) categories
                1) auxiliary data
                2) comp = precipitation amount
                3) others
            B) instrument name
            C) sort order for special parameters (mainly aux data)
                start_time, end_time, number of size bins,
                latitude, longitude, altitude, other position
            D) rest is sorted by comp name, characteristics, statistics and
               variable metadata:
                comp name
                characteristics
                statistics
                local metadata
        """
        scorelist = []
        for i in range(len(self.variables)):
            score = []
            matrix = self.get_meta_for_var(i, 'matrix')
            comp = self.get_meta_for_var(i, 'comp_name')

            # A: categories
            if self.is_auxiliary(i):
                score.append(1)
            elif comp and comp.startswith('precipitation_amount'):
                score.append(2)
            else:
                score.append(100)

            # B: instrument name
            score.append(self.get_meta_for_var(i, 'instr_name'))

            # C: sort order for special parameters (mainly auxiliary variables)
            if comp == 'start_time':
                # skipped on import, but when creating file it still needs to
                # get the right order.
                score.append(1)
            elif comp == 'end_time':
                # skipped on import, but when creating file it still needs to
                # get the right order.
                score.append(2)
            elif comp == 'number of size bins':
                # skipped on import, but when creating file it still needs to
                # get the right order.
                score.append(3)
            elif comp == 'latitude':
                score.append(4)
            elif comp == 'longitude':
                score.append(5)
            elif comp == 'altitude':
                score.append(6)
            elif matrix == 'position':
                # position, but not lat, lon, alt?
                score.append(7)
            elif matrix == 'instrument':
                score.append(8)
            else:
                score.append(100)

            # D:
            score.append(comp)
            # append order number as well as tag, value and unit as a tuple
            # that way, the most important ct_type (by order number) gets
            # prioritized.
            characteristics = []
            if 'characteristics' in self.variables[i].metadata and \
                    self.variables[i].metadata.characteristics is not None:
                for ordered in self.variables[i].metadata.characteristics.\
                                                                sorted_order():
                    characteristics.append((ordered[0], ordered[1].tuple()))
            score.append(tuple(characteristics))
            score.append(self.get_meta_for_var(i, 'statistics'))
            metadata = []
            for meta in self.internal.ebasmetadata.metadata_list_tag_value(
                    self, i):
                metadata.append((meta[2]['sortorder'], meta[0], meta[1]))
            score.append(tuple(metadata))
            score.append(i)  # last element is index
            scorelist.append(score)
        scorelist.sort()
        new_variables = []
        for sort_var in scorelist:
            new_variables.append(self.variables[sort_var[-1]])
        self.variables = new_variables

    def _consolidate_revdate(self):
        """
        Set the maximum revdate of all variables as the default revdate for
        the file. This is the expected behaviour for EBAS NASA-Ames.
        Parameters:
            None
        Returns:
            None
        """
        # main revdate is maximum of variables revdate's
        lst = [v.metadata.revdate for v in self.variables \
               if 'revdate' in v.metadata] + \
              [self.metadata.revdate for v in self.variables \
               if 'revdate' not in v.metadata]
        lst = [x for x in lst if x]
        if lst:
            newvalue = max(lst)
        else:
            newvalue = None
        # set new value, change all var metadata if necessary
        # this should be done anyway, there could be some var metadata
        # equal default
        for var in self.variables:
            if 'revdate' in var.metadata and \
               var.metadata['revdate'] == newvalue:
                # var metadata is equal to new default
                del var.metadata['revdate']
            elif 'revdate' not in var.metadata and \
               self.metadata.revdate != newvalue:
                # Set old default to var metadata.
                # (this would also set it to None, in case the old default
                # was None and the new default is different)
                var.metadata.revdate = self.metadata.revdate
            # else: leave as is
        # set the new default:
        self.metadata.revdate = newvalue

    def _consolidate_metadata_occ(self, key):
        """
        Move attibutes between global (NNCOM) and variable specific (VNAME).
        Parameters:
            key           metadata key name
        Returns:
            None
        """
        # hist will be a histogram of used values
        hist = Histogram()
        hist_noaux = Histogram()  # histogram for auxiliary variables excluded
        cnt_noaux = 0
        for vnum, var in enumerate(self.variables):
            if key in var.metadata and \
               var.metadata[key] != self.metadata[key]:
                hist.increment(var.metadata[key])
                if not self.is_auxiliary(vnum):
                    hist_noaux.increment(var.metadata[key])
                    cnt_noaux += 1
            else:
                hist.increment(self.metadata[key])
                if not self.is_auxiliary(vnum):
                    hist_noaux.increment(self.metadata[key])
                    cnt_noaux += 1

        # check all vars have the same rescode
        # if it differs, it's probably a metadata error in the DB, throw warning
        (maxocc, values) = hist.get_max()
        if key == 'resolution' and maxocc != len(self.variables):
            self.warning('Different resolution codes in one file')
            # see below, we need to provide a value anyway!

        # hist_noaux should only be used, if there is at least one element:
        if not self.strict_global and hist_noaux.get_max()[0] > 0:
            hist = hist_noaux
            cnt = cnt_noaux
        else:
            cnt = len(self.variables)
        # now decide if there should be a "default" value (main metadata)
        # current criteria: must be used by more than half of the variables
        (maxocc, values) = hist.get_max()
        if maxocc == cnt:
            # this applies to strict_global == True
            newvalue = values[0]
        elif not self.strict_global and maxocc > cnt / 2:
            # more than halv the variables have the same metadata value:
            newvalue = values[0]
        elif key == 'resolution':
            # special case: resolution: __must__ by definition be file global
            # see above, this should never happen, but we need a value anyway
            newvalue = values[0]
        else:
            newvalue = None
        # set new value, change all var metadata if necessary
        # this should be done anyway, there could be some var metadata
        # equal default
        for var in self.variables:
            if key in var.metadata and \
               var.metadata[key] == newvalue:
                # var metadata is equal to new default
                if key not in ('comp_name', 'unit'):
                    # comp name and unit must occur in every variable)
                    del var.metadata[key]
            elif key not in var.metadata and self.metadata[key] != newvalue:
                # Set old default to var metadata.
                # (this would also set it to None, in case the old default
                # was None and the new default is different)
                var.metadata[key] = self.metadata[key]
            # else: leave as is
        # set the new default:
        self.metadata[key] = newvalue

    def _consolidate_qa(self):
        """
        Move QA attibutes between global (NNCOM) and variable specific (VNAME).
        Parameters:
            None
        Returns:
            None
        """
        for elem in self.internal.ebasmetadata.metadata:
            key = elem['key']
            if 'QA_block' in elem and elem['QA_block']:
                for qanum in self.get_qa_numbers():
                    hist = Histogram()
                    for vnum in range(len(self.variables)):
                        for qa_ in self.get_qa_for_var(vnum):
                            if qa_['qa_number'] == qanum and key in qa_:
                                hist.increment(qa_[key])

                    # now decide if there should be a "default" value (main
                    # metadata) current criteria: must be used by more than half
                    # of the variables
                    (maxocc, values) = hist.get_max()
                    if maxocc > len(self.variables) / 2:
                        newvalue = values[0]
                    else:
                        newvalue = None

                    # set new value, change all var metadata if necessary
                    # this should be done anyway, there could be some var
                    # metadata equal default
                    for vnum in range(len(self.variables)):
                        qa_ = self.get_qa_by_number(qanum, vnum)
                        if qa_ and key in qa_ and qa_[key] == newvalue:
                            # var metadata is equal to new default
                            self.unset_qa(key, qanum, vnum)
                        elif not qa_ or key not in qa_:
                            main_qa = self.get_qa_by_number(qanum, None)
                            if main_qa and key in main_qa and \
                               main_qa[key] != newvalue:
                                # Set old default to var metadata.
                                # (this would also set it to None, in case the
                                # old default was None and the new default is
                                # different)
                                self.set_qa(key, main_qa[key], qanum, vnum)
                        # else: leave as is
                    # set the new default:
                    self.set_qa(key, newvalue, qanum, None)


    def _consolidate_flagcolumns(self, flags=FLAGS_ONE_OR_ALL):
        """
        Eliminates redundantflag columns.
        Parameters:
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
        """
        _cleanflags = lambda flags: [sorted([y for y in x if y != 999])
                                     for x in flags]

        latestflags = None
        manual_latest = None
        for i in reversed(range(len(self.variables))):
            if flags == FLAGS_NONE:
                self.variables[i].flagcol = False
                # clean values (set invalid to missing, set 781 to 1/2 value)
                # is done only on export - so the IO object remains
                # fully valid!
                # see: nasa_ames_write:set_data()
            elif flags == FLAGS_ALL:
                self.variables[i].flagcol = True
            # for FLAGS_ONE_OR_ALL, FLAGS_COMPRESS and FLAGS_AS_IS:
            # The flags need to be modified in a special case on output:
            # When multiple variables share a flag column and the flag column
            # has a flag 999 in a sample where one of the variables has a valid
            # value: the 999 needs to be dropped in this case.
            # But we do not change the flag sequence of the valid I/O object
            # here, this is been taken care of on flag output (for nasa_ames in
            # the set_data / _gen_flags methods in ebas/io/nasa_ames/write.py
            elif flags == FLAGS_ONE_OR_ALL:
                if latestflags is None:
                    latestflags = _cleanflags(self.variables[i].flags)
                    self.variables[i].flagcol = True
                elif latestflags == _cleanflags(self.variables[i].flags):
                    self.variables[i].flagcol = False
                else:
                    # flaglist differs, recursive call with FLAGS_ALL and return
                    self._consolidate_flagcolumns(flags=FLAGS_ALL)
                    return
            elif flags == FLAGS_COMPRESS:
                if latestflags == _cleanflags(self.variables[i].flags):
                    self.variables[i].flagcol = False
                else:
                    latestflags = _cleanflags(self.variables[i].flags)
                    self.variables[i].flagcol = True
            elif flags == FLAGS_AS_IS:
                # The warnings here could be errors.
                # Not sure, if someone uses FLAGS_AS_IS and does not stick to
                # the flagging rules, should it fail?
                # For now, we are graceful and do the best we can to fix it.
                file_vnum, _, _ = self.msgref_vnum_lnum(i)
                if i == len(self.variables) - 1:
                    if not self.variables[i].flagcol:
                        self.warning(
                            "Variable {}: last variable must have a flag "
                            "column".format(file_vnum))
                        self.variables[i].flagcol = True
                    manual_latest = i
                    latestflags = _cleanflags(self.variables[i].flags)
                elif not self.variables[i].flagcol and \
                        latestflags != _cleanflags(self.variables[i].flags):
                    file_vnum_flagcol, _, _ = self.msgref_vnum_lnum(
                        manual_latest)
                    self.warning(
                        "Variable {}: flag sequence is not consistent with "
                        "flag sequence of variable {}. Adding flag column for "
                        "variable {}.".format(
                            file_vnum, file_vnum_flagcol, file_vnum))
                    self.variables[i].flagcol = True
                    manual_latest = i
                    latestflags = _cleanflags(self.variables[i].flags)
                else:
                    # self.variables[i].flagcol == True
                    manual_latest = i
                    latestflags = _cleanflags(self.variables[i].flags)

    def _consolidate_title(self):
        """
        Generates a title string if none is set already.
        """
        for i in range(len(self.variables)):
            if 'title' not in self.variables[i].metadata or \
               self.variables[i].metadata.title is None:
                self.variables[i].metadata.title = \
                    self.variables[i].metadata.comp_name \
                        if "comp_name" in self.variables[i].metadata else ''

    def _set_method_analytical(self):
        """
        Sets the method ref if not set and analytical metadata instrument are
        given.
        Parameters:
            None
        Returns:
            None
        """
        def _get_ana_meta(vnum, pure=True):
            """
            Helper for getting metadata for a specific variable number.
            Parameters:
                vnum     variable index (None = NNCOM metadata)
                pure     return pure vname specifications for a variable
                         (might be different from the effective metadata set)
            Returns
                metadata dict for variable
            """
            tags = (
                'method', 'ext_lab', 'ana_technique', 'ana_lab_code',
                'ana_instr_name', 'ana_instr_manufacturer', 'ana_instr_model',
                'ana_instr_serialno')
            if vnum != None and not pure:
                return {tag: self.get_meta_for_var(vnum, tag) for tag in tags}

            metadata = self.variables[vnum].metadata if vnum != None \
                           else self.metadata
            return {tag: metadata[tag] for tag in tags if tag in metadata}

        # check analytical metadata consistency in NCOM:
        nnmeta = _get_ana_meta(None)

        for vnum in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(vnum)
            meta = _get_ana_meta(vnum)
            if meta:
                # something has been defined on variable level: check again for
                # this variable
                meta = _get_ana_meta(vnum, False)
                if ('method' not in self.variables[vnum].metadata or \
                   not self.variables[vnum].metadata['method']) and \
                   meta['ana_lab_code']  and meta['ana_instr_name']:
                    self.variables[vnum].metadata['method'] = \
                        meta['ana_lab_code'] + '_' + meta['ana_instr_name']
                    self.warning(
                        "Variable {}: automatically generating 'Method ref' "
                        "from analytical metadata: {}".format(
                            file_vnum, self.variables[vnum].metadata['method']),
                        lnum=file_metalnum)

                elif meta['method'] is None:
                    self.error(
                        "Variable {}: Missing metadata 'Method ref'".format(
                            file_vnum), lnum=file_metalnum)

        if not nnmeta['method'] and nnmeta['ana_lab_code']  and \
           nnmeta['ana_instr_name']:
            self.metadata['method'] = \
                nnmeta['ana_lab_code'] + '_' + nnmeta['ana_instr_name']
            self.warning(
                "automatically generating 'Method ref' from analytical "
                "metadata: {}".format(self.metadata['method']))
