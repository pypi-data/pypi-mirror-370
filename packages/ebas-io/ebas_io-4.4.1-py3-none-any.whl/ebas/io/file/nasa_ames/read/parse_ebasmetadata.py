"""
ebas/nasa_ames/read/parse_ebasmetadata.py
$Id: parse_ebasmetadata.py 2035 2018-05-22 14:13:03Z pe $

parser for file input functionality for EBAS NASA Ames module
parses ebas tag=value pairs from NasaAmes1001 object and builds NasaAmes

The basic parsing (and very fundamental value checks) are done by this module.
What is not done here:
 - More advanced value checks that need validation data from the DB
   --> NasaAmesToDomain
 - Value checks which depend on other metadata elements can not be done, those
   need to be checked after reading the complete header; see:
   --> NasaAmesBase.check_interdependent_metadata

History:
V.1.0.0  2013-06-22  pe  initial version

"""

import re
import datetime
from .parse_base import NasaAmesPartialReadParserBase
# pylint: disable=F0401
# F0401: Unable to import 'ebasmetadata' (pylint problem)
from ....ebasmetadata import EbasMetadataError, EbasMetadataWarning, \
    DatasetCharacteristicList, DCError, DCWarning
from nilutility.datatypes import DataObject
from ...basefile.base import  EbasMetadataInvalid


class NasaAmesPartialReadParserEbasMetadata(# pylint: disable=R0901, W0223,
        NasaAmesPartialReadParserBase):
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Parser for Nasa Ames I/O object.
    This is a base class for NasaAmesPartialReadParserVariables and
    NasaAmesPartialReadParser
    """

    def _parse_ebasmetadata_vname_positional(self, comp_name, unit, lnum,
                                             var_index, ignore_parameter=False):
        """
        Parse positional metadata elements from VNAME: comp_name, unit.
        Parameters:
            comp_name, unit   component name and unit from vname line
            lnum              line number (for error reporting)
            var_index         variable number in file
            ignore_parameter
                    ignore errors related to paramters and units this is needed
                    when a file with non standard vnames should be processed
                    without importing it into the ebas.domain.
        Returns:
            (comp_name, unit), invalid values are changed to EbasMetadataInvalid
        """
        # check component
        try:
            self.internal.ebasmetadata.parse_component(comp_name)
        except EbasMetadataError as excpt:
            msg = "Variable {}: {}".format(var_index, str(excpt))
            if ignore_parameter:
                self.warning(msg, lnum=lnum)
            else:
                self.error(msg, lnum=lnum)
                # set to EbasMetadataInvalid in order to avoid errors that
                # result from this one here.
                # E.g. mandatory missing, or things checked in
                # check_interdependent
                comp_name = EbasMetadataInvalid(comp_name)
        except EbasMetadataWarning as excpt:
            comp_name = excpt.retval
            msg = "Variable {}: {}".format(var_index, str(excpt))
            self.warning(msg, lnum=lnum)

        # check unit
        try:
            self.internal.ebasmetadata.parse_unit(unit)
        except EbasMetadataError as excpt:
            msg = "Variable {}: {}".format(var_index, str(excpt))
            if ignore_parameter:
                self.warning(msg, lnum=lnum)
            else:
                self.error(msg, lnum=lnum)
                # set to EbasMetadataInvalid in order to avoid errors that
                # result from this one here.
                # E.g. mandatory missing, or things checked in
                # check_interdependent
                unit = EbasMetadataInvalid(unit)

        return (comp_name, unit)

    def _parse_ebasmetadata(self, tag, value, lnum, var_index=None,
                            ignore_parameter=False):
        """
        Parse a tag=value pair from EBAS specific metadata.
        This can be either ebas core metadata or dataset characteristics.
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            None
        """
        metadata_tags = self.internal.ebasmetadata.metadata_tags
        # special case for QA metadata:
        if self._parse_ebasmetadata_qa(tag, value, lnum, var_index):
            pass
        elif tag in metadata_tags:
            # this is a core ebas metadata element (not a characteristic)
            if var_index != None and not metadata_tags[tag]['vname']:
                # [vname] == 0: not valid in VNAME
                self.error(tag + ": is not legal in VNAME", lnum=lnum)
                return # stop parsing this element
            elif var_index is None and not metadata_tags[tag]['main']:
                # [main] == 0: not valid for NCOML
                self.error(
                    tag + ": is not legal in main metadata block [NCOML]",
                    lnum=lnum)
                return # stop parsing this element
            if 'renamed_tag' in metadata_tags[tag] and \
               metadata_tags[tag]['renamed_tag']:
                self.warning(
                    "Legacy metadata element '{}' translated to '{}'"\
                    .format(tag, metadata_tags[tag]['renamed_tag']),
                    lnum=lnum)
            if self.metadata.datadef == 'EBAS_1' and value == 'NA':
                value = ''
            # Special Cases:
            parse_ebasmetadata_specific = {
                'Originator': self._parse_ebasmetadata_person,
                'Submitter': self._parse_ebasmetadata_person,
                'Timeref': self._parse_ebasmetadata_timeref,
                'Input dataset': self._parse_ebasmetadata_multiple_list,
                'Software': self._parse_ebasmetadata_multiple_list,
            }
            if tag in parse_ebasmetadata_specific:
                parse_ebasmetadata_specific[tag](tag, value, lnum, var_index)
            else:
                store_value = self._parse_ebasmetadata_generic(tag, value, lnum,
                                                               var_index)
                emptyval = None
                self._set_metadata(tag, store_value, lnum, var_index,
                                   emptyval=emptyval)
        else:
            # else, we assume it's a characteristic (validity can't be checked
            # without master data from database)
            self._parse_characteristics(tag, value, lnum, var_index,
                                        ignore_parameter=ignore_parameter)

    def _parse_ebasmetadata_qa(self, tag, value, lnum, var_index):
        """
        Parse tag=value pair from EBAS specific core metadata (one
        that can be processed generically by the ebasmetadata module).
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            True      was QA meatdata, parsed OK
            False     not QA metadata, caller needs to keep on processing
        """
        # get generic tag and QA number
        reg = re.match('^QA([0-9]*)( .*)$', tag)
        if reg:
            # this is a QA metadata element:
            generic_tag = "QA" + reg.group(2)
            qa_number = int(reg.group(1)) if reg.group(1) else -1
        else:
            return False  # not QA metadata

        metadata_tags = self.internal.ebasmetadata.metadata_tags
        if not generic_tag in metadata_tags:
            return False

        store_value = self._parse_ebasmetadata_generic(generic_tag, value, lnum,
                                                       var_index)

        key = self.internal.ebasmetadata.metadata_tags[generic_tag]['key']
        qa_ = self.get_qa_by_number(qa_number, var_index)
        if qa_ is not None and key in qa_ and qa_[key] is not None:
            self.error(
                "multiple definitions for '{}'".format(tag), lnum=lnum)
            return
        # set:
        self.set_qa(key, store_value, qa_number, var_index)

        return True

    def _parse_ebasmetadata_generic(self, tag, value, lnum, var_index):
        # pylint: disable-msg=R0912
        # R0912: Too many branches
        """
        Parse tag=value pair from EBAS specific core metadata (one
        that can be processed generically by the ebasmetadata module).
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            parsed (and converted, manipulated) value
        """
        occ = 'main' if var_index is None else 'vname'
        elem = self.internal.ebasmetadata.metadata_tags[tag]
        # parse value
        if value == '' or value is None:
            return None
        # check if some special params are set for default parsing
        params = {key+'_': elem[key] for key in ('unit', 'type', 'range', 'len')
                  if key in elem and elem[key] is not None}
        try:
            if 'parser' in elem and elem['parser']:
                value = elem['parser'](value)
            elif params:
                value = self.internal.ebasmetadata.parse_default(
                    value, **params)
            # else, just take the string as is
        except EbasMetadataError as excpt:
            self.error(tag + ": " + str(excpt), lnum=lnum)
            if elem[occ] & 8:
                self.internal.read_tmp.hea_error = True
            # set to EbasMetadataInvalid in order to avoid errors that
            # result from this one here.
            # E.g. mandatory missing, or things checked in
            # check_interdependent
            return EbasMetadataInvalid(value)
        except EbasMetadataWarning as excpt:
            value = excpt.retval
            self.warning(tag + ": " + str(excpt), lnum=lnum)
        return value

    def _parse_ebasmetadata_multiple_list(self, tag, value, lnum, var_index):
        # pylint: disable-msg=R0912
        # R0912: Too many branches
        """
        Parse tag=value pair for metadata which support multiple elements, but
        but only in global metadata.
        Currently only 'Input dataset'.
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
                          Not supported
        Returns:
            None
        """
        if value == '' or value is None:
            return
        if var_index is None:
            elem = self.internal.ebasmetadata.metadata_tags[tag]
            # check if some special params are set for default parsing
            params = {key+'_': elem[key]
                      for key in ('unit', 'type', 'range', 'len')
                      if key in elem and elem[key] is not None}
            try:
                if 'parser' in elem and elem['parser']:
                    value = elem['parser'](value)
                elif params:
                    value = self.internal.ebasmetadata.parse_default(
                        value, **params)
                # else, just take the string as is
            except EbasMetadataError as excpt:
                self.error(tag + ": " + str(excpt), lnum=lnum)
                if elem['main'] & 8:
                    self.internal.read_tmp.hea_error = True
            except EbasMetadataWarning as excpt:
                value = excpt.retval
                self.warning(tag + ": " + str(excpt), lnum=lnum)
            if not self.metadata[elem['key']]:
                self.metadata[elem['key']] = []
            self.metadata[elem['key']].append(value)
        else:
            # not supported, should not be set in ebasmetadata
            raise RuntimeError()

    def _set_metadata(self, tag, value, lnum, var_index, emptyval=None):
        """
        Set a metadata value for a generic ebas metadata element.
        Check if element has been set before (log error if set already)
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            None
        """
        key = self.internal.ebasmetadata.metadata_tags[tag]['key']
        if var_index is None:
            occurrence = 'main'
            metadata = self.metadata
        else:
            occurrence = 'vname'
            metadata = self.variables[var_index].metadata
        # check if multiply set:
        if key in metadata and \
             (metadata[key] != emptyval or occurrence == 'vname') and \
             (key != 'revdate' or
              (occurrence == 'main' and self.internal.read_tmp.revdate_read)):
            self.error(
                "multiple definitions for '{}'".format(tag), lnum=lnum)
        elif occurrence == 'main' and key == 'revdate':
            self.internal.read_tmp.revdate_read = True
            if isinstance(value, datetime.datetime) and \
               isinstance(self.metadata['revdate'], datetime.datetime) and \
               value.date() != self.metadata['revdate'].date():
                self.error(
                    "'{}' ({}...) must be the same day as RDATE specified in "
                    "line 7 ({})".format(
                        tag, datetime.datetime.strftime(value, "%Y%m%d"),
                        datetime.datetime.strftime(
                            self.metadata['revdate'], "%Y %m %d")),
                    lnum=lnum)
            if isinstance(value, datetime.datetime):
                metadata[key] = value
        elif key:
            metadata[key] = value

    def _parse_ebasmetadata_person(self, tag, value, lnum, var_index):
        """
        Parse EBAS person metadata (Submitter or Originator).
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            None
        """
        if value == '' or value is None:
            return None
        metadata_tags = self.internal.ebasmetadata.metadata_tags
        key = metadata_tags[tag]['key']
        if var_index is None:
            try:
                psd = metadata_tags[tag]['parser'](value)
            except EbasMetadataError as excpt:
                self.error(tag + ": " + str(excpt), lnum=lnum)
                return  # stop parsing this line
            except EbasMetadataWarning as excpt:
                psd = excpt.retval
                self.warning(tag + ": " + str(excpt), lnum=lnum)
            for pers in self.metadata[key]:
                if pers.PS_LAST_NAME == psd['PS_LAST_NAME'] and \
                   pers.PS_FIRST_NAME == psd['PS_FIRST_NAME']:
                    pers.update(psd)
                    self.logger.debug(u'{}={}'.format(tag, str(pers)))
                    break
            else:
                self.error(tag + u": '{}, {}'".\
                    format(psd['PS_LAST_NAME'], psd['PS_FIRST_NAME']) +\
                    u" not found in {} (line {})".\
                    format('ONAME' if tag == 'Originator' else 'SNAME',
                           2 if tag == 'Originator' else 4), lnum=lnum)
        else:
            # do we want to support Submitter / Originator in VNAME?
            raise NotImplementedError()

    def _parse_ebasmetadata_timeref(self, tag, value, lnum, var_index):
        """
        Parse an exceptional tag=value pair from EBAS specific metadata (one
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOM block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            None
        """
        if value == '' or value is None:
            return None
        metadata_tags = self.internal.ebasmetadata.metadata_tags
        if var_index != None:
            # this should have been caught by metadata_tags[tag]['vname']
            raise ValueError()
        try:
            (timeref, timeoffset) = metadata_tags[tag]['parser'](value)
        except EbasMetadataError as excpt:
            self.error(tag + ": " + str(excpt), lnum=lnum)
            occ = 'main' if var_index is None else 'vname'
            if metadata_tags[tag][occ] & 8:
                self.internal.read_tmp.hea_error = True
            if metadata_tags[tag][occ] & 4 or metadata_tags[tag][occ] & 8:
                # set to empty, in order to avoid 'mandatory missing' errors
                self._set_metadata(tag, '', lnum, var_index)
            return
        except EbasMetadataWarning as excpt:
            (timeref, timeoffset) = excpt.retval
            self.warning(tag + ": " + str(excpt), lnum=lnum)
        self._set_metadata(tag, timeref, lnum, var_index)
        self.internal.timeoffset = timeoffset

    def _parse_characteristics(self, tag, value, lnum, var_index=None,
                               ignore_parameter=False):
        """
        Parses and sets characteristics.
        Parameters:
            tag, value    tag=value pair from VNAME line or NCOML block
            lnum          line number (for error reporting)
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOML block)
        Returns:
            None
        """
        ft_type = ''
        co_comp_name = ''
        # get fi_type and co_comp_name from main metadata:
        if 'instr_type' in self.metadata:
            ft_type = self.metadata.instr_type
        if 'comp_name' in self.metadata:
            co_comp_name = self.metadata.comp_name
        # get the metadata set we should use for adding DC
        if var_index != None:
            metadata = self.variables[var_index].metadata
            # set variable_specific ft_type and co_comp_name
            if 'instr_type' in metadata:
                ft_type = metadata.instr_type
            if 'comp_name' in metadata:
                co_comp_name = metadata.comp_name
        else:
            metadata = self.metadata
            
        if isinstance(ft_type, EbasMetadataInvalid):
            ft_type = None  # set to none if EbasMetadataInvalid
        if isinstance(co_comp_name, EbasMetadataInvalid):
            co_comp_name = None  # set to none if EbasMetadataInvalid

        # init characteristics list if needed:
        if 'characteristics' not in metadata or \
           metadata.characteristics is None:
            metadata.characteristics = DatasetCharacteristicList()

        # create DC object (parse and validate)
        try:
            metadata.characteristics.add_parse(
                tag, value, ft_type, co_comp_name,
                data_level=self.metadata.datalevel)
        except DCError as excpt:
            if ignore_parameter:
                self.warning(str(excpt), lnum=lnum)
            else:
                self.error(str(excpt), lnum=lnum)
            return
        except DCWarning as excpt:
            self.warning(str(excpt), lnum=lnum)
            return
