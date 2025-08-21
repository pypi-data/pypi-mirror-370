"""
ebas/input_output/ebas_xml/write.py
$Id: write.py 2519 2020-10-30 16:13:09Z pe $

output functionality for EBAS XML module

History:
V.1.0.0  2014-08-05  toh  initial version

"""

import sys
import os
from six import PY2
from .base import EbasXMLBase
from ..base import FLAGS_ONE_OR_ALL, FLAGS_NONE
from ...ebasmetadata import EbasMetadata
from ebas.domain.basic_domain_logic.time_period import estimate_period_code
from nilutility.datatypes import DataObject
from fileformats.Xml.ebas import Xml
from ...fileset.xmlwrap import xmlwrap_fileheader, xmlwrap_filetrailer
from ..base import EBAS_IOFORMAT_XML

class EbasXMLPartialWrite(EbasXMLBase):  # pylint: disable=R0901, W0223,
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    XML I/O object.

    This is one part of the partial class EbasXML (output functionality).
    """

    def write(self, createfiles=False, destdir=None,  # pylint: disable=R0913
              xmlwrap=False, fileobj=None, flags=FLAGS_ONE_OR_ALL,
              datadef='EBAS_1.1', metadata_options=0, suppress=0):
        # R0913 Too many arguments
        # W0613 (unused metadata_options): need to be fixed? implement?
        """
        Writes the I/O object to an XML file (or stdout)
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
                          (ignored in XML, setkey is written anyway)
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
        if  createfiles:
            fil.write('<?xml version="1.0" encoding="utf-8"?>\n')
            fil.write('<ebas:Result xmlns:ebas="http://ebas.nilu.no/EBAS">\n')
        self.xml = Xml(self.result_id)
        self.set_attribs(flags=flags)
        self.set_times(flags=flags)
        self.set_data(flags=flags)
        self.set_flags(flags=flags)
        self.xml.write(fil)
        if  createfiles:
            fil.write('</ebas:Result>\n')
        if xmlwrap:
            xmlwrap_filetrailer()
        self.write_indexdb()

    def set_datadef(self, datadef):
        """
        Set the EBAS data definition (metadata standard).
        Parameters:
            datadef    data definition (EBAS_1 or EBAS_1.1)
        Returns
            None
        """
        # must be implemented here, because ebasmetadata can't be imported in
        # ..base
        self.metadata.datadef = datadef
        self.internal.ebasmetadata = EbasMetadata(
            self.metadata.datadef, data_format=EBAS_IOFORMAT_XML,
            data_level=self.metadata.datalevel)

    def set_attribs(self, flags=FLAGS_ONE_OR_ALL):
        """
        Sets directly the non-data Xml attributes.
        Parameters:
            None
        Returns
            None
        """
        self.xml.STATION_CODE = self.get_metadata_list_per_var('station_code')
        self.xml.STATION_NAME = self.get_metadata_list_per_var('station_name')
        self.xml.INST_TYPE = self.get_metadata_list_per_var('instr_type')
        self.xml.COMP_NAME = self.get_metadata_list_per_var('comp_name')
        self.xml.MATRIX_NAME = self.get_metadata_list_per_var('matrix')
        self.xml.UNIT = self.get_metadata_list_per_var('unit')
        self.xml.STATISTIC_CODE = self.get_metadata_list_per_var('statistics')
        self.xml.RESCODE = self.get_metadata_list_per_var('resolution')
        self.xml.DATA_LEVEL = self.get_metadata_list_per_var('datalevel')
        self.xml.HEIGHT_AGL = self.get_metadata_list_per_var('mea_height')
        self.xml.SETKEY = self.get_metadata_list_per_var('setkey')

        self.xml.UNCERTAINTY = self.get_metadata_list_per_var('uncertainty') # tupel

        self.xml.POSITION = list(zip(self.get_metadata_list_per_var('station_latitude'),
                                self.get_metadata_list_per_var('station_longitude'),
                                self.get_metadata_list_per_var('station_altitude')))

        # dictionary
        self.xml.CHARACTERISTICS = self.get_metadata_list_per_var('characteristics')

    def set_times(self, flags=FLAGS_ONE_OR_ALL):
        """
        Set time attributes.
        Parameter:
            None
        Returns:
            None
        """
        self.xml.SAMPLE_TIMES = self.sample_times

    def set_data(self, flags=FLAGS_ONE_OR_ALL):
        """
        Sets data attributes.
        Parameter:
            None
        Returns:
            None
        """
        self.xml.DATA = []
        for j in range(len(self.variables)):
            self.xml.DATA.append(self.values_without_flags(j))
            # clean values (set invalid to missing, set 781 to 1/2 value)
            # is done only for export - so the XML object remains
            # fully valid!

    def set_flags(self, flags=FLAGS_ONE_OR_ALL):
        """
        Sets data attributes.
        Parameter:
            None
        Returns:
            None
        """
        self.xml.FLAGS = []
        for j in range(len(self.variables)):
            if self.variables[j].flagcol:
                if flags == FLAGS_NONE:
                    # clean values (set invalid to missing, set 781 to 1/2
                    # value) is done only for export - so the NasaAmes object
                    # remains fully valid!
                    self.xml.FLAGS.append('')
                else:
                    flagstrings = [','.join(["{0:03d}".format(flag)
                                             for flag in flags])
                                   for flags in self.variables[j].flags]
                    self.xml.FLAGS.append(flagstrings)

    def join(self, other):
        """
        Join self with other if possible.
        Default implementation: do not join
        Parameters:
            other    other EbasIO object
        Returns
            New, joined EbasIO object
            None (no join possible)
        """
        # check if objects can be joined:
        # same variables, same setkeys, data interval can be joined,
        # and ALL metadata that are reported in the XML format must be the same:
        #    mea_height
        # Most depend on setkey (DS or HDS) and do not need to be checked:
        #  station_code
        #  station_name
        #  instr_type
        #  comp_name
        #  matrix
        #  unit
        #  statistics
        #  resolution
        #  datalevel
        #  characteristics
        if len(self.variables) != len(other.variables) or \
           self.get_metadata_list_per_var('setkey') != \
               other.get_metadata_list_per_var('setkey') or \
           self.sample_times[-1][1] > other.sample_times[0][0] or \
           self.get_metadata_list_per_var('mea_height') != \
               other.get_metadata_list_per_var('mea_height') or \
           self.get_metadata_list_per_var('uncertainty') != \
               other.get_metadata_list_per_var('uncertainty'):
            return None
        from .xml import EbasXML
        new = EbasXML(result_id=self.result_id, indexdb=self.indexdb)
        metadata = ['station_code', 'station_name', 'station_latitude',
                    'station_longitude', 'station_altitude']
        for meta in metadata:
            if self.metadata[meta] is not None:
                new.metadata[meta] = self.metadata[meta]
        new.sample_times = self.sample_times + other.sample_times
        new.variables = []
        for vnum in range(len(self.variables)):
            var1 = self.variables[vnum]
            var2 = other.variables[vnum]
            new.variables.append(
                DataObject(
                    is_hex=var1.is_hex,
                    values_=var1.values_ + var2.values_,
                    flags=var1.flags + var2.flags,
                    flagcol=True,
                    metadata=DataObject(
                        setkey=var1.metadata.setkey,
                        comp_name=var1.metadata.comp_name,
                        unit=var1.metadata.unit,
                        )))
            char = self.get_characteristics_for_var(vnum)
            if char:
                new.variables[vnum].metadata.characteristics = char
            metadata = [
                'instr_type', 'matrix', 'statistics', 'datalevel',
                'characteristics', 'resolution', 'mea_height', 'uncertainty',
                # plus some that are used for filename generation
                # (must be the same in both because they only depend on DS)
                'lab_code', 'instr_name', 'method']
            for meta in metadata:
                val = self.get_meta_for_var(vnum, meta)
                if val is not None:
                    new.variables[vnum].metadata[meta] = val
        return new
