"""
/NasaAmes1001/write.py
$Id: write.py 2566 2020-12-09 13:11:46Z pe $

Basic NASA Ames 1001 file writer class.
Handles low level file I/O.

History:
V.1.0.0  2013-10-24  pe  initial version

"""

import datetime
import re
import sys
import io
from six import PY2, string_types
from math import log
from nilutility.ndecimal import Decimal
from nilutility.datatypes import HexInt
from nilutility.numeric import digits_stat, digits
from .base import NasaAmes1001Error, NasaAmes1001Base

class NasaAmes1001Write(NasaAmes1001Base):
    """
    Partial class NasaAmes1001: Part for writing NasaAmes1001 files from object.
    """
    def write(self, filespec=None, encoding='utf-8'):
        """
        Reads the file according to NasaAmes 1001 standard.
        Parameters:
            filespec    file name (incl. path) or file like object (stream)
                        stdout if not passed
            encoding    unicode encoding for output
        Returns:
            None
        Raises:
            IOError           file open error
            NasaAmesError     on any unrecoverable write error
        """
        # reset the object state for writing
        self.init_state()
        self.finalize_data()

        self.encoding = encoding
        if filespec is None:
            if PY2:
                self.file = sys.stdout
            else:  # PY3
                from io  import _io
                if isinstance(sys.stdout, _io.TextIOWrapper):
                    # std stream in py3 is an encoding wrapper. We need to use
                    # the unencoded buffer directly in order to write bytes.
                    # We need to check if it's really a TextIOWrapper, otherwise
                    # we get problems with jupyter.
                    self.file = sys.stdout.buffer
                else:
                    self.file = sys.stdout
        elif isinstance(filespec, string_types):
            filename = filespec
            self.logger.info("writing file {}".format(filename))
            if PY2:
                mod = "w"
            else:
                mod = "wb"
            with open(filename, mod) as self.file:
                self._write()
        else:
            filename = None
            self.logger.debug("writing to stream")
            self.file = filespec
            self._write()

    def finalize_data(self):
        """
        Calculate data attributes that are not setable by the caller (not in
        SETABLE_DATA_ATTRIBS). These would be redundant if set by the caller.
        Set default values for unset attributes (initialized to None).
        Parameters:
            None
        Returns:
            None
        Raises:
            various builtin exceptions when data are not set correctly.
        """
        # first set DATA, SCOM and NCOM defaults, if not set
        if self.data.DATA is None:
            self.data.DATA = []
        if self.data.SCOML is None:
            self.data.SCOML = []
        if self.data.NCOML is None:
            self.data.NCOML = []
        # calculate unsetable attributes
        self.data.NV = max(len(self.data.DATA) - 1, 0)
        self.data.NLHEAD = \
            14 + self.data.NV + len(self.data.SCOML) + len(self.data.NCOML)

        self.variable_stat() # sets VMISS, VFORMAT, VREPR
        self.data.DX = self.dx_from_data()

        # set default values for the rest of unset attributes
        if self.data.IVOL is None:
            self.data.IVOL = 1
        if self.data.NVOL is None:
            self.data.NVOL = 1
        if self.data.DATE is None:
            raise NasaAmes1001Error('DATE must be set for writing NasaAmes1001')
        if self.data.RDATE is None:
            self.data.RDATE = datetime.datetime.utcnow()
        if self.data.VSCAL is None:
            self.data.VSCAL = [1 for _ in range(self.data.NV)]
        if self.data.VNAME is None:
            self.data.VNAME = ['' for _ in range(self.data.NV)]
        self._checkdims()

    def _checkdims(self):
        """
        Checks consistency of dimensions and extents in the data structure.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasAmes1001Error if inconsistent
        """
        # check dimension for VSCAL, VMISS, VNAME and DATA
        if len(self.data.VSCAL) != self.data.NV:
            raise NasaAmes1001Error(
                'VSCAL ({} values) inconsistent with NV ({})'
                .format(len(self.data.VSCAL), self.data.NV))
        if len(self.data.VMISS) != self.data.NV:
            raise NasaAmes1001Error(
                'VMISS ({} values) inconsistent with NV ({})'
                .format(len(self.data.VMISS), self.data.NV))
        if len(self.data.VNAME) != self.data.NV:
            raise NasaAmes1001Error(
                'VNAME ({} values) inconsistent with NV ({})'
                .format(len(self.data.VNAME), self.data.NV))
        if len(self.data.DATA)-1 != self.data.NV and \
           (self.data.NV != 0 or len(self.data.DATA) != 0):
            # rais error if #vars - 1 (== # dependent vars) != NV
            # special case: NV=0 and #vars = 0 (=> # dependent vars is -1!)
            raise NasaAmes1001Error(
                'DATA ({} dep. variables) inconsistent with NV ({})'
                .format(len(self.data.DATA)-1, self.data.NV))
        # check variable length
        for i in range(self.data.NV):
            if len(self.data.DATA[0]) != len(self.data.DATA[i+1]):
                raise NasaAmes1001Error(
                    'number of rows for variable[0] ({}) is different from '
                    'variable[{}] ({})'.format(len(self.data.DATA[0]), i+1,
                                               len(self.data.DATA[i+1])))

    def variable_stat(self):
        """
        Creates variable statistics.

        Parameters:
            var_index   variable index for which the statistics should be
                        gathered. None=all variables
        Returns:
            None

        These parameters are gathered/set:
         - VMISS: missing value
         - VFORMAT: output format for values
         - VREPR: data type for data variable
         - xformat
         - xmindig
         - minxmindig  (used when set from caller, not set)
         - maxxmindig  (used when set from caller, not set)
         - minvmindig  (used when set from caller, not set)
         - maxvmindig  (used when set from caller, not set)
        HexInt variables are checked for type
        """
        (self.data.VMISS, self.data.VFORMAT, self.data.VREPR) = ([], [], [])
        for i in range(len(self.data.DATA)):
            validvals = [x for x in self.data.DATA[i] if x is not None]
            if validvals:
                vrepr = type(validvals[0])
            else:
                vrepr = None
            (minval, maxval, mindig, maxdig, maxprec) = digits_stat(validvals)
            if mindig is None:
                # mindig and maxdig is None if all values are None
                # We handle this as if all values were 0
                (mindig, maxdig) = (0, 0)
#             if maxdig == 0:
#                 maxdig = 1
#             if mindig == 0:
#                 mindig = 1
#             if maxprec == 0:
#                 maxprec = 1
            if i == 0:
                # independent variable (start_time)
                if self.minxmindig != None and mindig < self.minxmindig:
                    mindig = self.minxmindig
                if self.maxxmindig != None and mindig > self.maxxmindig:
                    mindig = self.maxxmindig
                self.xmindig = mindig
                self.xformat = self.gen_vformat(vrepr, mindig, maxdig, maxprec,
                                                minval, True)
            else:
                # dependent variables (first is usually end_time)
                # collect some config parameters for this variable...
                vpar_minvmiss = False
                if self.minvmiss and len(self.minvmiss) >= i:
                    vpar_minvmiss = self.minvmiss[i-1]
                vpar_minvmindig = None
                if self.minvmindig and len(self.minvmindig) >= i:
                    vpar_minvmindig = self.minvmindig[i-1]                
                vpar_maxvmindig = None
                if self.maxvmindig and len(self.maxvmindig) >= i:
                    vpar_maxvmindig = self.maxvmindig[i-1]                
                vpar_vmiss = None
                if self.vmiss and len(self.vmiss) >= i:
                    vpar_vmiss = self.vmiss[i-1]                
                
                if not vpar_minvmiss or \
                   (maxval is not None and \
                    maxval >= type(maxval)(self.gen_vmiss(
                        type(maxval), mindig, maxdig, maxprec, 0, False))):
                    # add one order of magnitude (standard VMISS)
                    # exceptions are the x value or if minvmiss is set and
                    # the respective missing value does not appear in the data)
                    maxdig += 1
                    # correct minvmiss if maxval would be equal missing value:
                    vpar_minvmiss = False
                if vpar_minvmindig is not None and \
                   mindig < vpar_minvmindig:
                    mindig = vpar_minvmindig
                if vpar_maxvmindig is not None and \
                   mindig > vpar_maxvmindig:
                    mindig = vpar_maxvmindig
                force_scientific = None
                # a given vmiss from the caller can only extend the format:
                if vpar_vmiss:
                    if vrepr is None and vpar_vmiss.startswith('0x'):
                        # all values are None, miss is set to hex:
                        # change output format to hex
                        vrepr = HexInt
                    if vrepr == HexInt:
                        if not re.match(r'^0x(f+)$', vpar_vmiss, re.IGNORECASE):
                            raise ValueError(
                                "illegal vmiss for HexInt: {}".format(
                                    vpar_vmiss))
                        # the provided vmiss is HexInt and we have a HexInt
                        # series
                        (vmiss_mindig, vmiss_maxdig) = \
                            digits(HexInt(vpar_vmiss))
                        if vmiss_maxdig >= maxdig:
                            # use the provided vmiss value
                            maxdig = vmiss_maxdig
                            # mindig is alays 1 for HexInt
                    else:                        
                        reg = re.match(r"^([9]*)(\.([9]*))?([Ee](\+99))?$",
                                       self.vmiss[i-1])
                            # exponent in scientific notation must be +99
                            # there is no way to specify the number of digits in
                            # exponent in a format string (see gen_vformay), so
                            # it makes no sense to allow missing values other
                            # than E+99
                        if not reg:
                            raise ValueError(
                                "illegal vmiss for float/Decimal: {}".format(
                                    vpar_vmiss))
                        (vmiss_mindig, vmiss_maxdig) = \
                            digits(Decimal(vpar_vmiss))
                        if reg.group(4):
                            # scientific format missing value
                            if len(reg.group(1)) != 1:
                                raise ValueError(
                                    "vmiss in scientific notation must use one "
                                    "digit before comma: {}".format(
                                        vpar_vmiss))
                            # vmiss_maxdig is the highest possible digit value
                            # for the pattern. must not bee smaller than the
                            # highest digit value in the values.
                            # additionally the precision must be higher or equal
                            if maxdig-mindig <= vmiss_maxdig-vmiss_mindig and \
                                    maxdig < vmiss_maxdig:
                                # use the specified vmiss
                                mindig = vmiss_mindig
                                maxdig = vmiss_maxdig
                                maxprec = vmiss_maxdig - vmiss_mindig
                                if (vmiss_maxdig > 0 and vmiss_mindig > 0) or \
                                   (vmiss_maxdig < 0 and vmiss_mindig < 0):
                                    maxprec += 1
                            # else: don't use the actual vmiss, but still force
                            # scientific notation
                            force_scientific = True  # force scientific frmt
                        else:
                            # decimal format
                            if ((vmiss_mindig <= mindig or  # normal case
                                 (vmiss_mindig == 1 and mindig == 0))
                                 # special case mindig==0 if all None or all 0
                                and vmiss_maxdig >= maxdig):
                                # use the provided vmiss value
                                mindig = vmiss_mindig
                                maxdig = vmiss_maxdig
                            # else: don't use the actual vmiss, but still force
                            # decimal notation
                            force_scientific = False  # force decimal format
                self.data.VREPR.append(vrepr)
                self.data.VMISS.append(self.gen_vmiss(
                    vrepr, mindig, maxdig, maxprec, minval, vpar_minvmiss,
                    force_scientific=force_scientific))
                self.data.VFORMAT.append(self.gen_vformat(
                    vrepr, mindig, maxdig, maxprec, minval, vpar_minvmiss,
                    force_scientific=force_scientific))

    @staticmethod
    def gen_vmiss(vrepr, mindig, maxdig, maxprec, minval, minvmiss,
                  force_scientific=None):
        """
        Generates vmiss string for one variable.
        Parameters:
            vrepr         type of data variable (HexInt, float, Decimal)
            mindig        minimum digit used in the data
            maxdig        maximum digit used in the data
            maxprec       maximum precision used in a single value (important
                          for scientific notation)
            minval        minimum value used (important for accommodating a
                          minus sign)
            minvmiss      bool: uses minimal vmiss values (spare one digit)
                          in this case, the decimal format must be one char
                          wider (to accommodate a negative sign, which is else
                          wise accommodated by the longer pattern)
            force_scientific
                          True (force), False (force decimal),
                          None (do automatic)
        """
        if vrepr == HexInt:
            return "{}0x{}".format(
                " " if minval is not None and minval < 0 else "",
                "f" * maxdig)
        elif force_scientific is True or \
             (force_scientific is not False and
              NasaAmes1001Write._prefer_scientific(mindig, maxdig, maxprec)):
            return "{}9{}{}E+99".format(
                " " if minval is not None and minval < 0 else "",
                "." if maxprec > 1 else "",
                "9"*(maxprec-1))
        else:
            # decimal output format
            if minvmiss and minval is not None and minval < 0 and \
                    digits(minval)[1] == maxdig:
                # if minimal vmiss should be used and a negative minimum
                # value uses the maximum digit, we need to add one character
                # for the negative sign
                vmiss = " "
            else:
                vmiss = ""
            if maxdig > 0:
                vmiss += "9"*(maxdig)
            else:
                vmiss = "9"
            if mindig < 0:
                vmiss += "." + "9"*(-1*mindig)
            return vmiss

    @staticmethod
    def gen_vformat(vrepr, mindig, maxdig, maxprec, minval, minvmiss,
                    force_scientific=None):
        """
        Generates format string for one variable.
        Parameters:
            vrepr         type of data variable (HexInt, float, Decimal)
            mindig        minimum digit used in the data
            maxdig        maximum digit used in the data
            maxprec       maximum precision used in a single value (important
                          for scientific notation)
            minval        minimum value used (important for accommodating a
                          minus sign)
            minvmiss      bool: uses minimal vmiss values (spare one digit)
                          in this case, the decimal format must be one char
                          wider (to accommodate a negative sign, which is else
                          wise accommodated by the longer pattern)
            force_scientific
                          True (force), False (force decimal),
                          None (do automatic)
        """
        maxprec = max(maxprec, 1)
        if vrepr == HexInt:
            return "{}#0{:d}x".format(
                " " if minval is not None and minval < 0 else "",
                maxdig + (3 if minval is not None and minval < 0 else 2))
        if force_scientific is True or \
             (force_scientific is not False and
              NasaAmes1001Write._prefer_scientific(mindig, maxdig, maxprec)):
            width = maxprec+6 if minval is not None and minval < 0 \
                else maxprec+5
            if maxprec == 1:
                # format will be .0 --> no comma, one less wide
                width -= 1
            return "{:d}.{:d}E".format(width, maxprec-1)
        # decimal format
        maxdig = max(maxdig, 1)
        mindig = min(mindig, 0)
        if minvmiss and minval is not None and minval < 0 and \
                digits(minval)[1] == maxdig:
            # if minimal vmiss should be used and a negative minimum
            # value uses the maximum digit, we need to add one character
            # for the negative sign
            maxdig += 1
        if mindig < 0:
            return "{:d}.{:d}f".format(maxdig-mindig+1, -1*mindig)
        return "{0:d}.0f".format(maxdig)

    @staticmethod
    def _prefer_scientific(mindig, maxdig, maxprec):
        """
        Decides whether scientific representation should be preferred for
        for float/Decimal output.
        Parameters:
            maxdig   maximum digit used in variable (order of magnitude)
            mindig   minimum digit used in variable (order of magnitude)
            maxprec  maximum precision used in one value
        """
        # calculate the deciamls used in decimal notations:
        if mindig < 0:
            decused = max(maxdig, 1)-mindig
        else:
            decused = maxdig - min(mindig, 1)
        if (maxdig < -3 or mindig > 3 or decused > 7) and \
            decused-4 > maxprec:
            # if numbers are more than 3 orders of magnitude off E00 or
            # the range spans more than 9 orders of magnitudes, it's
            # reasonable to use scientifig format.
            # but only if scientific mantissa (maxprec) is reasonably shorter
            # then the decimal representation (basically, it must compensate for
            # additional "E..."
            return True
        return False

    def _write(self):
        """
        Writes the file to opened file handle.
        This method is only needed to extract the write functionality in order
        to wrap the 'with open(filename)' around it in the read() method.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmesError     on any unrecoverable read error
        """
        for self.state in range(len(self.__class__.SECTIONS)):
            statename = self.curr_state_name()
            try:
                method = getattr(self, '_write_' + statename.lower())
            except AttributeError:
                # If no dedicated _write method exists: write one line as
                # string.
                # Those are: ONAME, ORG, SNAME, MNAME, XNAME
                self.logger.debug(u'write {}: {}'.format(statename,
                                                         self.data[statename]))
                self.writeline(self.data[statename])
            else:
                method()

    def _write_nlhead(self):
        """
        Writes the NLHEAD line to file.
        """
        self.writeline('{0:d} 1001'.format(self.data.NLHEAD))


    def _write_ivol_nvol(self):
        """
        Writes the IVOL/NVOL line to file.
        """
        self.writeline('{0:d} {1:d}'.format(self.data.IVOL, self.data.NVOL))

    def _write_date_rdate(self):
        """
        Writes the DATE/RDATE line to file.
        """
        self.writeline(self.data.DATE.strftime("%Y %m %d ") +\
                       self.data.RDATE.strftime("%Y %m %d"))

    def _write_dx(self):
        """
        Writes DX to the file.
        """
        if self.data.DX == 0.0:
            self.writeline('0')
        elif self.xmindig != None and self.xmindig < 0:
            self.writeline('{:.{}f}'.format(self.data.DX,
                                            self.xmindig * -1))
        elif self.xmindig != None and self.xmindig >= 0:
            self.writeline('{:.0f}'.format(self.data.DX))
        else:
            self.writeline('{:f}'.format(self.data.DX))

    def _write_vscal(self):
        """
        Writes the VSCAL line to file.
        """
        self.writeline(" ".join([str(vscal) for vscal in self.data.VSCAL]))

    def _write_vmiss(self):
        """
        Writes the VMISS line to file.
        """
        self.writeline(" ".join([x.lstrip() for x in self.data.VMISS]))

    def _write_vname(self):
        """
        Writes the VMISS line to file.
        """
        for vname in self.data.VNAME:
            self.writeline(vname)

    def _write_scoml(self):
        """
        Writes the VMISS line to file.
        """
        self.writeline(len(self.data.SCOML))
        for scom in self.data.SCOML:
            self.writeline(scom)

    def _write_ncoml(self):
        """
        Writes the VMISS line to file.
        """
        self.writeline(len(self.data.NCOML))
        for ncom in self.data.NCOML:
            self.writeline(ncom)

    def _write_data(self):
        """
        Writes data lines to files.
        """
        if len(self.data.DATA) == 0:
            return
        fmt = ['{{:{}}}'.format(self.xformat)]
        miss = [None]
        for j in range(self.data.NV):
            fmt.append("{{0:{0}}}".format(self.data.VFORMAT[j]))
            miss.append(self.data.VMISS[j])

        for i in range(len(self.data.DATA[0])):
            line = fmt[0].format(self.data.DATA[0][i])
            for j in range(1, len(self.data.DATA)):
                if self.data.DATA[j][i] is None:
                    line += ' ' + miss[j]
                else:
                    line += ' ' + fmt[j].format(self.data.DATA[j][i])
            self.writeline(line)

    def writeline(self, line):
        """
        Writes one line to the file and increases the objects lnum attribute.
        Parameters:
            line     line of text to write
        Returns:
            None
        """
        self.lnum += 1
        if line is None:
            line = ''
        elif not isinstance(line, string_types):
            line = unicode(line) if PY2 else str(line)
        line += '\n'
        if PY2:
            self.file.write(line.encode(self.encoding))
        else:
            # still some encoding chaos...
            # later we should just use a text mode for the file.
            # after dropping support for py2
            if isinstance(self.file, io.BufferedIOBase):
                self.file.write(line.encode(self.encoding))
            else:
                self.file.write(line)
        self.logger.debug(u"write line {}: {}".format(self.lnum, line))
