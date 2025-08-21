"""
ebas/input_output/ebas_csv_write.py
$Id: write.py 2519 2020-10-30 16:13:09Z pe $

output functionality for EBAS CSV module

History:
V.1.0.0  2014-08-07  pe  initial version

"""

import sys
import os
from .base import EbasCSVBase
from ..base import FLAGS_ONE_OR_ALL, FLAGS_NONE
from ebas.domain.basic_domain_logic.time_period import estimate_period_code
from fileformats.CsvUnicode import CsvUnicodeWriter
from ...fileset.xmlwrap import xmlwrap_fileheader, xmlwrap_filetrailer
import textwrap

class EbasCSVPartialWrite(EbasCSVBase):  # pylint: disable=R0901
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    """
    CSV I/O object.

    This is one part of the partial class EbasCSV (output functionality).
    """
    
    def write(self, createfiles=False, destdir=None,  # pylint: disable=R0913
              xmlwrap=False, fileobj=None, flags=FLAGS_ONE_OR_ALL,
              datadef='EBAS_1.1', metadata_options=0, suppress=0):
        # R0913 Too many arguments
        """
        Writes the I/O object to a CSV file (or stdout)
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
        self.csv = CsvUnicodeWriter(fil, dialect="excel", encoding="utf-8")
        self.set_header(flags=flags)
        self.set_var_metadata()
        self.__write(flags=flags)
        if xmlwrap:
            xmlwrap_filetrailer()
        if createfiles:
            fil.close()
        self.write_indexdb()

    def set_header(self, flags=FLAGS_ONE_OR_ALL):
        """
        Gnereate the header block of the CSV file.
        Sets directly the CSV attributes.
        Parameters:
            None
        Returns
            None
        """
        self.header = []
        for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(
                self):
            self.header.append([meta[0], meta[1]])
        if flags == FLAGS_NONE:
            self.csv.writerow([
                'Technical note:',
                textwrap.dedent("""\
            !!! WARNING !!!
            This file has been extracted from EBAS without flag information.
            Data without flag information are easier to process by non expert
            users, but part of the information is lost!
            Changes on extract without flag information:
                - values flagged with at least one flag from the class of
                  invalid flags are changed to MISSING VALUE
                - values flagged with flag 781 ("Value below detection limit,
                  data element contains detection limit") are divided by 2""")])

    def set_var_metadata(self):
        """
        Generates a vname string for the measuremnt column and one for a
        possible flag column for variable vnum.
        Parameters:
            None
        Returns:
            tuple (vname_str, vname_str_flag)
        """
        # cache global metadata
        global_metadata = {
            meta[0]: meta[1]
            for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(
                self)}

        self.var_metadata = {
            'Variable type': ['Start Time UTC', 'End Time UTC']
        }
        self.var_meta_tags = set()
        self.var_meta_tags.add((-1, 'Variable type'))
        self.var_char_keys = set()
        self.var_characteristics = {}

        for vnum in range(len(self.variables)):
            self.var_metadata['Variable type'].append('Data')
            if 'characteristics' in self.variables[vnum].metadata:
                tags_added = []
                for char in self.variables[vnum].metadata.\
                                characteristics.sorted_order():
                    self.var_char_keys.add((char[0], char[1].CT_TYPE))
                    # tupel (sort_order, ct_type)
                    if char[1].CT_TYPE not in self.var_characteristics:
                        # new characteristic, fill previous vars with ''
                        # start- end time:
                        self.var_characteristics[char[1].CT_TYPE] = ['', '']
                        # other variables:
                        for vnum2 in range(vnum):
                            self.var_characteristics[char[1].CT_TYPE].append('')
                            if self.variables[vnum2].flagcol:
                                self.var_characteristics[char[1].CT_TYPE].\
                                    append('')
                    self.var_characteristics[char[1].CT_TYPE].append(
                        char[1].value_string())
                    tags_added.append(char[1].CT_TYPE)
                for tag in self.var_characteristics.keys():
                    if tag not in tags_added:
                        self.var_characteristics[tag].append('')
            tags_added = []
            for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(\
                    self, vnum):
                self.var_meta_tags.add((meta[2]['sortorder'], meta[0]))
                # tupel (sort_order, metadata-tag)
                if meta[0] not in self.var_metadata:
                    # new metadata element, fill values for all previous vars
                    self.var_metadata[meta[0]] = ['', '']  # start- and end time
                    # other vars:
                    for vnum2 in range(vnum):
                        if meta[0] in global_metadata:
                            self.var_metadata[meta[0]].append(
                                global_metadata[meta[0]])
                        else:
                            self.var_metadata[meta[0]].append('')
                        if self.variables[vnum2].flagcol:
                            if vnum2 >= 1 and \
                               not self.variables[vnum2-1].flagcol:
                                # make a general flag column
                                self.var_metadata[meta[0]].append('')
                            else:
                                # make a dedicated flag column
                                if meta[0] == 'Unit':
                                    self.var_metadata[meta[0]].append('no unit')
                                else:
                                    self.var_metadata[meta[0]].append(
                                        self.var_metadata[meta[0]][-1])

                self.var_metadata[meta[0]].append(meta[1])
                tags_added.append(meta[0])
            for tag in self.var_metadata.keys():
                if tag != 'Variable type' and tag not in tags_added:
                    if tag in global_metadata:
                        self.var_metadata[tag].append(global_metadata[tag])
                    else:
                        self.var_metadata[tag].append('')
            if self.variables[vnum].flagcol:
                self.var_metadata['Variable type'].append('Flag')
                for tag in self.var_metadata:
                    if tag != 'Variable type':
                        if vnum >= 1 and not self.variables[vnum-1].flagcol:
                            # make a general flag column
                            self.var_metadata[tag].append('')
                        else:
                            # make a dedicated flag column
                            if tag == 'Unit':
                                self.var_metadata[tag].append('no unit')
                            else:
                                self.var_metadata[tag].append(
                                    self.var_metadata[tag][-1])
                for tag in self.var_characteristics:
                    if vnum >= 1 and not self.variables[vnum-1].flagcol:
                        # make a general flag column
                        self.var_characteristics[tag].append('')
                    else:
                        # make a specific flag column (with all characteristics
                        # and metadata)
                        if 'characteristics' in \
                               self.variables[vnum].metadata and \
                           self.variables[vnum].metadata.characteristics \
                               is not None and \
                           self.variables[vnum].metadata.characteristics \
                               .dc_by_ct_type(tag) is not None:
                            self.var_characteristics[tag].append(
                                self.variables[vnum].metadata.characteristics.
                                dc_by_ct_type(tag).value_string())
                        else:
                            self.var_characteristics[tag].append('')


    def __write(self, flags=FLAGS_ONE_OR_ALL):
        """
        Sets the CSV data variables.
        Parameter:
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
        Returns:
            None
        """
        # remove from global header what's included as variable metadata:
        for i in reversed(range(len(self.header))):
            if self.header[i][0] in self.var_metadata:
                del self.header[i]
            else:
                self.header[i][0] += ':'
        # write header
        self.csv.writerow(['EBAS CSV',
                           3+len(self.header)+len(self.var_metadata)+
                           len(self.var_characteristics)+
                           len(self.sample_times)])
        self.csv.writerow(['GLOBAL METADATA', len(self.header)])
        for hea in self.header:
            self.csv.writerow(hea)
        self.csv.writerow(['VARIABLE METADATA AND DATA',
                           len(self.var_metadata)+len(self.var_characteristics),
                           len(self.sample_times)])
        # set the metadata
        for meta in sorted(list(self.var_meta_tags)):
            self.csv.writerow([meta[1]+':'] + self.var_metadata[meta[1]])
        # set the characteristics
        for char in sorted(list(self.var_char_keys)):
            self.csv.writerow([char[1]+':'] + self.var_characteristics[char[1]])

        # prepare values and flags
        values = []
        numflags = []
        for vnum in range(len(self.variables)):
            if flags == FLAGS_NONE:
                # clean values (set invalid to missing, set 781 to 1/2 value)
                # is done only for export - so the I/O object remains
                # fully valid!
                values.append(self.values_without_flags(vnum))
            else:
                values.append(self.variables[vnum].values_)
            if self.variables[vnum].flagcol:
                numflags.append(
                    [float('0.' +\
                           ''.join(["{0:03d}".format(flag)
                                    for flag in flags]))
                     for flags in self.variables[vnum].flags])
            else:
                numflags.append('')
        for i in range(len(self.sample_times)):
            row = ['', self.sample_times[i][0].strftime('%Y-%m-%dT%H:%M:%SZ'),
                   self.sample_times[i][1].strftime('%Y-%m-%dT%H:%M:%SZ')]
            for vnum in range(len(self.variables)):
                row.append(values[vnum][i])
                if self.variables[vnum].flagcol:
                    row.append(numflags[vnum][i])
            self.csv.writerow(row)
