"""
ebas/io/nasa_ames/write.py
$Id: write.py 2769 2021-12-08 22:35:41Z pe $

output functionality for EBAS NASA Ames module
"""

import re
import sys
import os
import textwrap
from nilutility.string_helper import list_joiner
from .base import EbasNasaAmesBase
from ..base import FLAGS_ONE_OR_ALL, FLAGS_NONE
from fileformats.NasaAmes1001 import NasaAmes1001


class NasaAmesPartialWrite(EbasNasaAmesBase):  # pylint: disable=R0901, W0223
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: '_read' is abstract in class 'EbasFileRead' but is not overridden
    # This class is also abstract.
    """
    Nasa Ames I/O object.

    This is one part of the partial class NasaAmes (output functionality).
    """

    def write(self, createfiles=False, destdir=None,  # pylint: disable=R0913
              xmlwrap=False, fileobj=None, flags=FLAGS_ONE_OR_ALL,
              datadef='EBAS_1.1', metadata_options=0, suppress=0):
        # R0913 Too many arguments
        """
        Writes the I/O object to a NASA Ames file (or stdout)
        Parameters:
            createfiles   write to file? else write to stdout
                          (special case for fileobj)
            destdir       destination directory path for files
            xmlwrap       wrap output in xml container
            fileobj       write to filehandle
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
            datadef       ebas data definition (EBAS_1 or EBAS_1.1)
            metadata_options
                          options for output, bitfield:
                          currently only EBAS_IOMETADATA_OPTION_SETKEY
            suppress      suppress selected consolidations (bitfield):
                              SUPPRESS_SORT_VARIABLES
                              SUPPRESS_METADATA_OCCURRENCE
        Returns:
            None
        """
        fil = self.prepare_write(
            True, createfiles=createfiles, destdir=destdir, xmlwrap=xmlwrap,
            fileobj=fileobj, flags=flags, datadef=datadef,
            metadata_options=metadata_options, suppress=suppress)

        self.nasa1001 = NasaAmes1001()
        self.set_header(flags=flags)
        self.set_data(flags=flags)
        self.nasa1001.write(fil)
        self.finish_write(createfiles, xmlwrap)
        if createfiles:
            fil.close()
        self.write_indexdb()

    def set_header(self, flags=FLAGS_ONE_OR_ALL):
        """
        Gnereate the header block of the NASA Ames file.
        Sets directly the NasaAmes1001 attributes.
        Parameters:
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
        Returns
            None
        """
        self.nasa1001.ONAME = self.gen_oname_str()
        self.nasa1001.ORG = self.gen_org_str()
        self.nasa1001.SNAME = self.gen_sname_str()
        self.nasa1001.MNAME = self.gen_mname_str()
        self.nasa1001.IVOL = 1
        self.nasa1001.NVOL = 1
        self.nasa1001.DATE = self.metadata.reference_date
        self.nasa1001.RDATE = self.metadata.revdate
        self.nasa1001.XNAME = "days from file reference point"
        # VSCAL defaults to 1 in NasaAmes1001
        self.nasa1001.VNAME = list(self.gen_vname_str())
        self.nasa1001.NCOML = list(self.gen_nncom_str())
        if flags == FLAGS_NONE:
            self.nasa1001.SCOML = textwrap.dedent("""\
            !!! WARNING !!!
            This file has been extracted from EBAS without flag information.
            Data without flag information are easier to process by non expert
            users, but part of the information is lost!
            Changes on extract without flag information:
                - values flagged with at least one flag from the class of
                  invalid flags are changed to MISSING VALUE
                - values flagged with flag 781 ("Value below detection limit,
                  data element contains detection limit") are divided by 2""").\
            split('\n')

    def gen_oname_str(self):
        """
        Generates output string for ONAME line.
        Parameter:
            None
        Returns:
            ONAME line (str)
        """
        return self._gen_persname_str(self.metadata.originator)

    def gen_sname_str(self):
        """
        Generates output string for SNAME line.
        Parameter:
            None
        Returns:
            SNAME line (str)
        """
        return self._gen_persname_str(self.metadata.submitter)

    @staticmethod
    def _gen_persname_str(perslist):
        """
        Creates output string for SNAME or ONAME line.
        Parameters:
            perslist   list of person metadata (submitter or originator)
        Returns:
            str    First Name, Last Name; First Name, Last Name; ...
        """
        if not perslist:
            return "MISSING INFORMATION"
        return list_joiner([list_joiner([pers.PS_LAST_NAME, pers.PS_FIRST_NAME],
                                        ',', insert_space=True)
                            for pers in perslist],
                           ';', insert_space=True)

    def gen_org_str(self):
        """
        Generates output string for ORG line.
        Parameter:
            None
        Returns:
            ORG line (str)
        """
        def _comma_escape(elem):
            """
            Helper: escape comma in strings of a list (wrap in double quotes)
            Parameters:
                elem    list of strings
            Returns:
                None
            """
            for i in range(len(elem)):
                if elem[i] and re.search(",", elem[i]):
                    elem[i] = '"' + re.sub('"', '""', elem[i]) +'"'

        def _none_to_empty(elem):
            """
            Helper: substitute None by empty string in a list.
            Parameters:
                elem    list of strings (or None)
            Returns:
                None
            """
            for i in range(len(elem)):
                if elem[i] is None:
                    elem[i] = ''

        elem = [self.metadata.org['OR_CODE'],
                self.metadata.org['OR_NAME'],
                self.metadata.org['OR_ACRONYM'],
                self.metadata.org['OR_UNIT'],
                self.metadata.org['OR_ADDR_LINE1'],
                self.metadata.org['OR_ADDR_LINE2'],
                self.metadata.org['OR_ADDR_ZIP'],
                self.metadata.org['OR_ADDR_CITY'],
                self.metadata.org['OR_ADDR_COUNTRY']] \
            if 'org' in self.metadata and self.metadata.org is not None \
            else [None] * 9
        _none_to_empty(elem)
        _comma_escape(elem)
        return u"{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(*elem)

    def gen_mname_str(self):
        """
        Generates output string for MNAME line.
        Parameter:
            None
        Returns:
            MNAME line (str)
        """
        return ' '.join(self.metadata.projects)

    def gen_vname_str(self):
        """
        Generates output strings for VNAME lines.
        Parameters:
            None
        Returns:
            generator (str):
                VNAME lines
        """
        yield "end_time of measurement, days from the file reference point"
        for i in range(len(self.variables)):
            comp, flag = self.vname(i)
            yield comp
            if self.variables[i].flagcol:
                if i == 0 or self.variables[i-1].flagcol:
                    yield flag
                else:
                    yield "numflag, no unit"

    def vname(self, vnum):
        """
        Generates a vname string for the measuremnt column and one for a
        possible flag column for variable vnum.
        Parameters:
            vnum   variable index
        Returns:
            tuple (vname_str, vname_str_flag)
        """
        comp = ''
        flag = 'numflag '
        if 'comp_name' in self.variables[vnum].metadata:
            comp = '{}, '.format(
                self.variables[vnum].metadata.comp_name \
                    if self.variables[vnum].metadata.comp_name is not None \
                    else '')
            flag += '{}, no unit'.format(
                self.variables[vnum].metadata.comp_name \
                    if self.variables[vnum].metadata.comp_name is not None \
                    else '')
        else:
            comp = '{}, '.format(
                self.metadata.comp_name if self.metadata.comp_name is not None \
                else '')
            flag += '{}, no unit'.format(
                self.metadata.comp_name if self.metadata.comp_name is not None \
                else '')
        if 'unit' in self.variables[vnum].metadata:
            comp += self.variables[vnum].metadata.unit \
                if self.variables[vnum].metadata.unit != None else ''
        else:
            comp += self.metadata.unit if self.metadata.unit is not None else ''
        # characteristics
        if 'characteristics' in self.variables[vnum].metadata and \
                self.variables[vnum].metadata.characteristics is not None:
            for char in self.variables[vnum].metadata.characteristics.sorted():
                comp += ', {}={}'.format(char.CT_TYPE, char.value_string())
                flag += ', {}={}'.format(char.CT_TYPE, char.value_string())
        for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(\
                self, vnum):
            value = meta[1]
            if '=' in value:
                value = u'"' + re.sub('"', '""', value) + u'"'
            tag_value = u"{0}={1}".format(meta[0], value)
            if ',' in tag_value:
                tag_value = u'"' + re.sub('"', '""', tag_value) + u'"'
            comp += u", {0}".format(tag_value)
            flag += u", {0}".format(tag_value)
        return (comp, flag)

    def gen_nncom_str(self):
        """
        Generates output strings for NNCOM lines.
        Parameter:
            None
        Returns:
            generator (str):
                NNCOM lines
        """
        # set the lable width:
        lable_width = 29
        for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(
                self):
            if ':' in meta[1] or '"' in meta[1]:
                val = u'"' + re.sub('"', '""', meta[1]) + u'"'
            else:
                val = meta[1]
            yield u"{0:{width}s} {1}".format(meta[0]+':', val,
                                             width=lable_width)

        yield self.gen_title_str()


    def gen_title_str(self):
        """
        Generates output string for TITLE line.
        Parameter:
            None
        Returns:
            TITLE line (str)
        """
        title = ["starttime", "endtime"]
        for i in range(len(self.variables)):
            title.append(
                self.variables[i].metadata.title \
                    if self.variables[i].metadata.title else '')
            if self.variables[i].flagcol:
                if ('flagtitle' in self.variables[i] and
                    self.variables[i].flagtitle):
                    # flagtitle is an attribute of the variable, not in the
                    # metadata of the variable. This seems more natural, because
                    # it should for example not be stored when reading and
                    # writing files (the flag title should change then because
                    # of possible reorganisations and variable rearangements).
                    # In contrast, the metadata.title should be stored when
                    # reading a file, and then be reused when writing.
                    title.append(self.variables[i].flagtitle)
                elif i == 0 or self.variables[i-1].flagcol:
                    title.append("flag_" + \
                        self.variables[i].metadata.title \
                        if self.variables[i].metadata.title else '')
                else:
                    title.append("flag")
        return " ".join(title)

    def set_data(self, flags=FLAGS_ONE_OR_ALL):
        """
        Sets the NasaAmes1001 data variables.
        Parameter:
            None
        Returns:
            None
        """
        self.nasa1001.DATA = []
        offset = self.metadata.reference_date + self.internal.timeoffset
        # int(x/0.0086400)/10000000.0  --> round to 6 digits (< 1s)
        self.nasa1001.DATA.append(
            [(start - offset).total_seconds() / 86400.
             for start, _ in self.sample_times])
        self.nasa1001.DATA.append(
            [(end - offset).total_seconds() / 86400.0
             for _, end in self.sample_times])
        # restrict x and first dep.var output format to 999.999999 at most
        self.nasa1001.minxmindig = -6
        self.nasa1001.minvmindig = [-6]  # same for endtime
        self.nasa1001.maxvmindig = [None]  # no maximum vmindig for endtime
        self.nasa1001.minvmiss = [True] # use minimal VMISS value for endtime
        self.nasa1001.vmiss = [None]  # no explicit vmiss for end_time
        for j in range(len(self.variables)):
            self.nasa1001.minvmiss.append(False)
            self.nasa1001.maxvmindig.append(None)
            if 'vmiss' in self.variables[j] and self.variables[j].vmiss:
                self.nasa1001.vmiss.append(self.variables[j].vmiss)
            else:
                self.nasa1001.vmiss.append(None)
            if flags == FLAGS_NONE:
                # clean values (set invalid to missing, set 781 to 1/2 value)
                # is done only for export - so the NasaAmes object remains
                # fully valid!
                self.nasa1001.DATA.append(self.values_without_flags(j))
            else:
                self.nasa1001.DATA.append(self.variables[j].values_)
            if self.variables[j].flagcol:
                genflags = self._gen_flags(j)
                flagstrings = [''.join(["{0:03d}".format(flag)
                                        for flag in flags])
                               for flags in genflags]
                flagvar = [float("0." + flagstr)
                           for flagstr in flagstrings]
                # forrce to use n digits after, but at least 3 (if no flags at
                # all)
                flaglen = max([len(flagstr) for flagstr in flagstrings] + [3])
                self.nasa1001.maxvmindig.append(-1 * flaglen)
                # use minimal VMISS value for flags:
                self.nasa1001.minvmiss.append(True)
                if 'flag_vmiss' in self.variables[j] and \
                   self.variables[j].flag_vmiss:
                    if not re.match(r'9\.(999)+', self.variables[j].flag_vmiss):
                        raise ValueError("illegal vmiss for flag: {}".format(
                            self.variables[j].flag_vmiss))
                    self.nasa1001.vmiss.append(self.variables[j].flag_vmiss)
                else:
                    self.nasa1001.vmiss.append(None)
                self.nasa1001.DATA.append(flagvar)

    def _gen_flags(self, vnum):
        """
        Generate the flag sequence to be printed. Take care of this special
        case:
        A flag column applies to multiple data columns, the flag sequence
        contains flag 999 for a sample where one of the other variables
        conatin a valid value (and thus no flag 999).
        This special case has been taken into account for consolidate_flags, but
        the flag sequence itself was NOT changed there (the I/O object should
        remain valid all the time, it should be just done on write).
        """
        # find other variable which use the same flag column:
        othervars = []
        for i in reversed(range(vnum)):
            if self.variables[i].flagcol:
                break
            othervars.append(i)
        if othervars == []:
            # no other variables use the same flag sequence
            return self.variables[vnum].flags
        return [[self.variables[vnum].flags[j][k]
                 for k in range(len(self.variables[vnum].flags[j]))
                 if self.variables[vnum].flags[j][k] != 999 or
                 [self.variables[o].values_[j] for o in othervars
                  if self.variables[o].values_[j] is not None] == []]
                for j in range(len(self.variables[vnum].flags))]
