"""
ebas/nasa_ames/read/parse_variables.py
$Id: parse_variables.py 2734 2021-11-17 17:01:45Z pe $

parser for file input functionality for EBAS NASA Ames module
parses variables from NasaAmes1001 object and builds NasaAmes

History:
V.1.0.0  2013-06-22  pe  initial version

"""

import re
from nilutility.datatypes import DataObject
from nilutility.string_helper import list_splitter
from .parse_ebasmetadata import NasaAmesPartialReadParserEbasMetadata
from .legacy_vnames import NasaAmesPartialReadLegacyVnames

class NasaAmesPartialReadParserVariables(# pylint: disable=R0901, W0223,
        NasaAmesPartialReadLegacyVnames,
        NasaAmesPartialReadParserEbasMetadata):
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Parser for Nasa Ames I/O object.
    This is a base class for NasaAmesPartialRead
    """
    def _parse_variables(self, skip_variables=None, ignore_parameter=False):
        """
        Parse VNAME lines (variable names).
        Additionally checks the missing values for each variable.
        Syntax:
            "param_name, unit[,Keyword=Value,...]"
        Parameters:
            skip_variables    list of variable numbers to be skipped (variabzle
                              numbers start with 1 for the first variable after
                              end_time)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
        Returns:
            None
        """
        self._skip_variables(skip_variables)
        self.translate_legacy_vnames()
        self.parse_variable_endtime()

        i = 0
        for i in range(1, self.nasa1001.data.NV):
            if i in self.internal.read_tmp.var_skipped:
                continue
            vname = self.nasa1001.data.VNAME[i]
            vmiss = self.nasa1001.data.VMISS[i]
            if vname.startswith("numflag"):
                self._parse_variable_numflag(i, vname, vmiss)
            else:
                self._parse_variable_regular(i, vname, vmiss,
                                             ignore_parameter=ignore_parameter)
        # check if there's at least one variable
        if len(self.variables) < 1 and self.internal.read_tmp.var_skipped:
            self.warning('No variable found (all skipped)', lnum=13+i)
        elif len(self.variables) < 1:
            self.error('No variable found', lnum=13+i)
        # check if last variable has a flag
        elif not self.variables[-1].flagcol:
            self.error('Last variabe must have a flag', lnum=13+i)
            # This is a critical error, checking data crashes with empty flags!
            self.internal.read_tmp.hea_error = True

    def _skip_variables(self, skip_variables):
        """"
        Skip variables by caller.
        Parameters:
            skip_variables    list of variable numbers to be skipped (variabzle
                              numbers start with 1 for the first variable after
                              end_time)
        Returns:
            None
        """
        if skip_variables is None:
            return
        for i in skip_variables:
            if i < 1 or i >= self.nasa1001.data.NV:
                self.error("skip_variables: variable number {} is illegal "
                           "(must be between 1 and NV-1 (1..{} in this case))"
                           .format(i, self.nasa1001.data.NV-1))
            elif self.nasa1001.VNAME[i].startswith("numflag"):
                self.error("skip_variables: variable number {} is illegal "
                           "(flag variable may not be skipped)".format(i))
            else:
                self.internal.read_tmp.var_skipped.append(i)
                self.warning(
                    "VNAME[{}]: variable skipped: {}".format(
                        i, self.nasa1001.VNAME[i]),
                    lnum=13+i)

    def parse_variable_endtime(self):
        """
        Parse VNAME line for end_time variable (first dep. variable).
        Parameters:
            None
        Returns:
            None
        """
        vname = self.nasa1001.data.VNAME[0]
        if vname not in \
           ("end_time of measurement, days from the file reference point",
            "end_time, Julian date counted from the file reference point",
            "end_time, days from the file reference point"):
            self.error(
                "VNAME[0] is not a supported end_time definition: '{}', should "
                "be 'end_time, days from the file reference point'".
                format(vname), lnum=13)
            self.internal.read_tmp.hea_error = True
            return   # stop parsing
        if not re.match(r'^9+(\.9*)?$', self.nasa1001.data.VMISS[0]) and \
           not re.match(r'^9(\.9*)?E\+?9*$', self.nasa1001.data.VMISS[0], re.I):
            self.error(
                "VMISS[0]: format error: '{}'. Should be '9.9*E+99', '9*.9*' "
                "or similar. Variable skipped.".format(
                    self.nasa1001.data.VMISS[0]),
                lnum=12)
            self.internal.read_tmp.hea_error = True
            return   # stop parsing

    @staticmethod
    def _is_general_flagcolumn(vname):
        """
        Check if vname is a general flag column (i.e. no comp name)
        Parameters:
            vname    vname line of the flag column
        Returns:
            True/False
        """
        if vname == "numflag" or \
           vname == "numflag, no unit":
            return True
        return False

    def _is_dedicated_flagcolumn(self, vname):
        """
        Check if vname is a dedicated flag column (i.e. includes comp name)
        Parameters:
            vname    vname line of the flag column
        Returns:
            True/False
        """
        if vname.startswith("numflag " + \
                            self.variables[-1].metadata.comp_name + \
                            ", no unit"):
            return True
        return False

    def _parse_variable_numflag(self, vnum, vname, vmiss):
        """
        Parse VNAME line for a flag column.
        Parameters:
            vnum    variable number (in the file)
            vname   vname line read from file (str)
            vmiss   vmiss definition (str)
        Returns:
            None
        Variable number in the object differs from variable number in file
        (because the object only stores measurements as variables, having
        flags as an attribute)
        """
        if vnum-1 in self.internal.read_tmp.var_skipped and \
           (len(self.variables) == 0 or self.variables[-1].flagcol):
            # if prev variable has been skipped, the flag column must also be
            # skipped. there is no element for the variable in the list!
            self.warning(
                "VNAME[{}]: flag skipped (flag for skipped variable)".
                format(vnum), 13 + vnum)
            self.internal.read_tmp.var_skipped.append(vnum)
            return
        if len(self.variables) == 0 or \
           self.variables[-1].flagcol:
            self.error(
                'VNAME[{}]: numflag without preceding variable, flag skipped'.
                format(vnum), lnum=13+vnum)
            self.internal.read_tmp.var_skipped.append(vnum)
            return  # stop parsing

        if self.nasa1001.data.NV == 3:
            # this may be a general or a dedicated flag column
            if not self._is_general_flagcolumn(vname) and \
               not self._is_dedicated_flagcolumn(vname):
                self.warning(
                    u"VNAME[{}]: unconventional VNAME for flag column: '{}'. "
                    u"Should be 'numflag, no unit' or start with 'numflag {}, "
                    u"no unit'".format(vnum, vname,
                                       self.variables[-1].metadata.comp_name),
                    lnum=13+vnum)
        elif len(self.variables) > 1 and not self.variables[-2].flagcol:
            # this must be a general flag column
            if not self._is_general_flagcolumn(vname):
                self.warning(
                    u"VNAME[{}]: unconventional VNAME for flag column: '{}'. "
                    u"Should be 'numflag, no unit'".format(vnum, vname),
                    lnum=13+vnum)
        else:
            # this must be a dedicated flag column
            if not self._is_dedicated_flagcolumn(vname):
                self.warning(
                    u"VNAME[{}]: unconventional VNAME for flag column: '{}'. "
                    u"Should start with 'numflag {}, no unit'".format(
                        vnum, vname, self.variables[-1].metadata.comp_name),
                    lnum=13+vnum)

        self.variables[-1].flagcol = True
        # parse vmiss for this flag column
        reg = re.match(r"^9\.(9+)$", vmiss)
        if reg:
            flen = len(reg.group(1))
            if flen % 3 != 0:
                self.error(
                    "VMISS[{}]: illegal missing value for flag column: '{}'. "
                    "Should be 9.[999]... (groups of 3 digiits). Flag skipped".
                    format(vnum, vmiss), lnum=12)
                self._skip_last_flag(vnum)
        else:
            self.error(
                "VMISS[{}]: illegal missing value for flag column: '{}'. "
                "Should be 9.[999]... (groups of 3 digiits). Flag skipped".
                format(vnum, vmiss), lnum=12)
            self._skip_last_flag(vnum)

    def _skip_last_flag(self, vnum):
        """
        Skip a flag column (due to errors in the column definition)
        Skipped column is the flag column for the last variable in the object,
        the column number in the file is vnum.
        ParametersL
            vnum    variable number (in the file)
        Returns:
            None:
        """
        self.internal.read_tmp.var_skipped.append(vnum)  # skip flag var
        # additionally skip already existing data variables which
        # use this flag column
        skip = []
        self.variables[-1].flagcol = False
        for i in reversed(range(0, len(self.variables))):
            if self.variables[i].flagcol:
                break
            skip.append(self.internal.read_tmp.var_num[i])
            self._skip_existing_variable(i)
        self.error("skipped variables {} due to skipped flag variable {}".
                   format(", ".join([str(x) for x in sorted(skip)]), vnum),
                   lnum=12)


    def _skip_existing_variable(self, vnum):
        """
        Skips an already existing variables.
        Parameters:
            vnum   variable number (in i/o object)
        Returns:
            None
        """
        j = self.internal.read_tmp.var_num[vnum]  # pos in file
        self.internal.read_tmp.var_skipped.append(j)
        del self.internal.read_tmp.var_num[vnum]
        del self.internal.read_tmp.vmiss[vnum]
        del self.variables[vnum]


    def _parse_variable_regular(self, vnum, vname, vmiss,
                                ignore_parameter=False):
        """
        Parse VNAME line and VMISS specification for a regular variable.
        Parameters:
            vnum    variable number (in the file, 1=first var after endtime)
            vname   vname line read from file (str)
            vmiss   vmiss definition (str)
           ignore_parameters
                    ignore errors related to paramters and units this is needed
                    when a file with non standard vnames should be processed
                    without importing it into the ebas.domain.
        Returns:
            None
        Variable number in the object differs from variable number in file
        (because the object only stores measurements as variables, having
        flags as an attribute)
        """
        if not re.match(r'^9+(\.9*)?$', vmiss) and \
           not re.match(r'^9(\.9*)?E\+?9*$', vmiss, re.I) and \
           not re.match(r'^0x9+$', vmiss, re.I) and \
           not re.match(r'^0xF+$', vmiss, re.I):
            self.error(
                "VMISS[{}]: format error: '{}'. Should be '9.9*E+99', '9*.9*', "
                "'0x9*', '0xF*' or similar. Variable skipped."
                .format(vnum, vmiss), lnum=12)
            self.internal.read_tmp.var_skipped.append(vnum)
            return   # stop parsing
        if vmiss.lower().startswith('0x'):
            is_hex = True
        else:
            is_hex = False

        reg = re.match(r"^([^,]+),\s*([^,]+)(,\s*(.*))?$", vname)
        if not reg:
            self.error(
                "VNAME[{}]: illegal syntax for VNAME: '{}'. Should be "
                "'component_name, unit[, metadata=value]...'. Variable skipped"
                .format(vnum, vname), lnum=13+vnum)
            self.internal.read_tmp.var_skipped.append(vnum)
            return # stop parsing this line
        comp_name, unit = self._parse_ebasmetadata_vname_positional(
            reg.group(1).strip(), reg.group(2).strip(), 13+vnum, vnum,
            ignore_parameter=ignore_parameter)

        # append the variable:
        self.variables.append(
            DataObject(is_hex=is_hex,
                       values_=[], flags=[], flagcol=False,
                       metadata=DataObject(comp_name=comp_name,
                                           unit=unit)))
        self.internal.read_tmp.var_num.append(vnum)
        self.internal.read_tmp.vmiss.append(vmiss)

        if self.metadata.datadef == 'EBAS_1' and reg.group(4):
            self.warning(
                "VNAME[{}]: additional metadata in VNAME in EBAS_1".format(
                    vnum), lnum=13+vnum)

        def _resort_meta(metalist):
            """
            Special: instrument type must be processed first (some other
            parsers depend on it).
            """
            int_list = list(metalist)
            for elem in int_list:
                if elem.startswith('Instrument type'):
                    yield elem
            for elem in int_list:
                if not elem.startswith('Instrument type'):
                    yield elem

        # parse additional metadata (variable specific metadata, statistics,
        # characteristics)
        if reg.group(4):
            for add in _resort_meta(list_splitter(reg.group(4), ",")):
                try:
                    (tag, value) = list_splitter(add, "=")
                except ValueError:
                    self.error(
                        "VNAME[{}]: additional metadata element '{}' not in "
                        "'tag=value' syntax".format(vnum, add),
                        lnum=13+vnum)
                    continue
                tag = tag.strip()
                value = value.strip()
                if value == u'':
                    value = None
                var_index = len(self.variables)-1
                self._parse_ebasmetadata(tag, value, 13 + vnum,
                                         var_index=var_index)
