"""
/NasaAmes1001/read.py
$Id: read.py 2557 2020-12-02 23:54:45Z pe $

Basic NASA Ames 1001 file reader class.
Handles low level file I/O.

History:
V.1.0.0  2013-03-05  pe  initial version

"""

import re
import math
import sys
import datetime
from fileformats.AsciiRead import AsciiRead, BackposError
from nilutility.ndecimal import Decimal, InvalidOperation
from nilutility.datatypes import HexInt
from nilutility.logging_helper import INFO_MINUS
from nilutility.msg_condenser import MessageRecord, MessageCondenser
from .base import NasaAmes1001Error, NasaAmes1001Base


MSG_NUM_VAL_ERR = 0
MSG_CVT_ERR = 1
MSG_CVT2_ERR = 2
MSG_XINC_ERR = 3
MSG_XINCDX_ERR = 4
MSG_VMISS_ERR = 5
MSG_VFORMAT_ERR = 6


class NasaAmesMessageRecord(MessageRecord):
    """
    Derived MessageRecord class for EbasIO:
    Adds column number to keys and line number to data.
    """
    KEYS = ['msgfunc', 'msg_id', 'cnum']
    DATA = ['message', 'line']

class NasaAmesMessageCondenser(MessageCondenser):
    """
    Message condenser for NasaAmes logging
    """

    def deliver_msg(self, record, condensed):
        """
        Deliver a single message.
        Parameters:
            record     the message record
            condensed  bool, condensed message
        Returns:
            None
        """
        record.msgfunc(record.message, lnum_override=record.line)
        if condensed:
            lst = self.dict[record.key]
            record.msgfunc(
                "The previous message repeats {} times{}. "
                "First occurrences in lines: {}, ..."
                .format(
                    len(lst)-1,
                    " for DATA[{}]".format(record.cnum) \
                        if record.cnum is not None else "",
                    ", ".join(
                        [str(x.line) for x in lst[0:self.threshold]])),
                lnum_override=record.line, counter_increase=len(lst)-1)
            # use same lnum as above message, otherwise the lines get parted
            # in submit-tool


class NasaAmes1001Read(NasaAmes1001Base):  # pylint: disable=R0902
    # R0902: Too many instance attributes
    """
    Partial class NasaAmes1001: Part for reading NasaAmes1001 files into object.
    """

    def __init__(self, *args, **kwargs):
        """
        Paramaters:
            *args, **kwargs, passd through to base class
        Returns:
            None
        """
        super(NasaAmes1001Read, self).__init__(*args, **kwargs)
        self.nbsp_warned = False
        self.msg_condenser = None
        self.vmiss_vals = None

    def read(self, filespec, encoding=None, skip_data=False,
             condense_messages=0):
        """
        Reads the file according to NasaAmes 1001 standard.
        Parameters:
            filespec    file name (incl. path) or file like object (stream)
            encoding    force a specific encoding to be used
            skip_data   skip reading of data (speedup, if data are not needed at
                        application level). First and last line are read.
        Returns:
            None
        Raises:
            IOError           file open error
            NasaAmesError     on any unrecoverable read error
        """
        # reset the object for reading
        self.init_state()
        self.init_data()

        self.encoding = encoding
        self.enc_line = None

        self.msg_condenser = NasaAmesMessageCondenser(
            threshold=condense_messages, record_cls=NasaAmesMessageRecord)

        with AsciiRead(
            filespec, encodings=('ascii', 'utf-8', 'utf-16', 'utf-32'),
            fallback_encoding='iso8859-15', strict_enc=True,
            ignore_bom=2, cvt_nbsp=2, strip=True, tabsize=1,
            error_callback=self.ascii_read_error_callback,
            warning_callback=self.ascii_read_warning_callback) as self.file:
            self._read(skip_data)

    def _read(self, skip_data):
        """
        Reads the file from opened file handle.
        This method is only needed to extract the reading functionality in order
        to wrap the 'with open(filename)' around it in the read() method.
        Parameters:
            skip_data   skip reading of data (speedup, if data are not needed at
                        application level). First and last line are read.
        Returns:
            None
        Raises:
            NasaAmesError     on any unrecoverable read error
        """
        for self.state in range(len(self.__class__.SECTIONS)):
            statename = self.curr_state_name()
            try:
                method = getattr(self, '_read_' + statename.lower())
            except AttributeError:
                # If no dedicated _read method exists: store one line as string\
                # Those are: ONAME, ORG, SNAME, MNAME, XNAME
                self.data[statename] = self._read_header_line()
                self.logger.debug(u'%s=%s', statename, self.data[statename])
            else:
                if statename != 'DATA' or not skip_data:
                    method()
                else:
                    method(skip_data)
        # check dx:
        if self.data.DATA != []  and len(self.data.DATA[0]) > 1 and \
           self.data.DX != None:
            # dx is only valid, if number of samples is greater 1
            # also make sure there was no syntax error in DX (!=None)
            dx_ = self.dx_from_data()
            if not skip_data and not self._dx_equal(self.data.DX, dx_):
                if self.data.DX == 0 and \
                   not self.strictness & self.__class__.STRICT_DX:
                    # if DX=0 and not strict: warning and set correctly
                    self.warning("DX ({}) ".format(self.data.DX) + \
                        "specified in line 8 is inconsistent with data"
                        " - setting {}".format(dx_))
                    self.data.DX = dx_
                else:
                    # if DX!=0 or strictness is requested: error
                    # (a set DX != 0 must always be obeyed!)
                    self.error("DX ({}) ".format(self.data.DX) + \
                        "specified in line 8 is inconsistent with data"
                        " - should be {}".format(dx_))
        if self.errors:
            raise NasaAmes1001Error("Exiting because of previous errors")

    def _read_nlhead(self):
        """
        Read the first line from a NASA Ames 1001 file: Check for 1001 specifier
        and store NLHEAD.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmes1001Error   on syntax error
        """
        try:
            line = self._readline()
        except EOFError:
            self.error("unexpected end of file", exception=True)
        reg = re.match(r'^(\d+) +1001$', line)
        if not reg:
            self.error("this is not a NASA Ames 1001 file", exception=True)
        self.data.NLHEAD = int(reg.group(1))
        if self.data.NLHEAD < 15:
            self.warning('NLHEAD < 15 seems too little, expect '+\
                '"incomplete NASA Ames header" error to follow')
        self.logger.debug('NLHEAD=%s', self.data.NLHEAD)

    def _read_ivol_nvol(self):
        """
        Read the IVOL/NVOL line from a NASA Ames 1001 file.
        Parameters:
            None
        Returns:
            None
        """
        reg = re.match(r'^(\d+) +(\d+)$', self._read_header_line())
        if not reg:
            self.error("IVOL/NVOL syntax error")
        else:
            self.data.IVOL = int(reg.group(1))
            self.data.NVOL = int(reg.group(2))
        self.logger.debug('IVOL=%s, NVOL=%s',
                          # use %s instead of %d (else None fails)
                          self.data.IVOL, self.data.NVOL)

    def _read_date_rdate(self):
        """
        Read the DATE/RDATE line from a NASA Ames 1001 file: Check syntax and
        store DATE and RDATE as datetime.datetime objects.
        Parameters:
            None
        Returns:
            None
        """
        reg = re.match(
            r'^(\d\d\d\d) +(\d\d) +(\d\d) +(\d\d\d\d) +(\d\d) +(\d\d) *$',
            self._read_header_line())
        if not reg:
            self.error('DATE/RDATE syntax error')
            return # stop parsing of this line
        (dyyyy, dmo, ddd, ryyyy, rmo, rdd) = reg.groups()
        try:
            self.data.DATE = datetime.datetime(year=int(dyyyy), month=int(dmo),
                                               day=int(ddd))
        except ValueError as excpt:
            self.error('DATE error: ' + str(excpt))
        self.logger.debug('DATE=%s', self.data.DATE)
        try:
            self.data.RDATE = datetime.datetime(year=int(ryyyy), month=int(rmo),
                                                day=int(rdd))
        except ValueError as excpt:
            self.error('RDATE error: ' + str(excpt))
        self.logger.debug('RDATE=%s', self.data.RDATE)

    def _read_dx(self):
        """
        Read the DX line from a NASA Ames 1001 file.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmes1001Error   on syntax error
        """
        reg = re.match(r'^(\d*(\.\d*)?)$', self._read_header_line())
        if not reg:
            # this is a non recoverable error
            self.error('DX syntax error')
            return
        if not reg.group(1):
            self.error('DX may not be empty')
            return
        try:
            self.data.DX = float(reg.group(1))
        except ValueError:
            self.error('DX syntax error')
            return
        self.logger.debug('DX=%f', self.data.DX)

    def _read_nv(self):
        """
        Read the NV line from a NASA Ames 1001 file.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmes1001Error   on syntax error
        """
        reg = re.match(r'^(\d+)$', self._read_header_line())
        if not reg:
            # this is a non recoverable error
            self.error('NV syntax error', exception=True)
        self.data.NV = int(reg.group(1))
        self.logger.debug('NV=%d', self.data.NV)

    def _read_vscal(self):
        """
        Read the VSACL line from a NASA Ames 1001 file.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmes1001Error   on syntax error
        """
        self.data.VSCAL = []
        vscal = self._read_header_line().split()
        if len(vscal) != self.data.NV:
            self.error('number of VSCAL elements ({}) does not match NV ({})'.\
                        format(len(vscal), self.data.NV))
        for i in range(max(len(vscal), self.data.NV)):
            value = None
            if i < len(vscal):
                try:
                    value = float(vscal[i])
                except ValueError:
                    self.error('VSCAL[{}]: not a float value'.format(i))
            if i < self.data.NV:
                self.data.VSCAL.append(value)
        self.logger.debug('VSCAL=%s', self.data.VSCAL)

    def _read_vmiss(self):
        """
        Read the VMISS line from a NASA Ames 1001 file.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmes1001Error   on syntax error
        """
        self.data.VMISS = []
        self.data.VFORMAT = []
        self.data.VFORMAT2 = []
        self.data.VREPR = []   # representation: float or Decimal
        vmiss = self._read_header_line().split()
        if len(vmiss) != self.data.NV:
            self.error('number of VMISS elements ({}) does not match NV ({})'.\
                        format(len(vmiss), self.data.NV))
        for i in range(max(len(vmiss), self.data.NV)):
            (val, fmt, fmt2, rep) = (None, None, None, float)
            if i < len(vmiss):
                try:
                    (val, fmt, fmt2, rep) = self._get_vmiss_fmt(vmiss[i])
                except ValueError as excpt:
                    self.error("VMISS[{}]: {}".format(
                        i, str(excpt)))
            if i < self.data.NV:
                self.data.VMISS.append(val)
                self.data.VFORMAT.append(fmt)
                self.data.VFORMAT2.append(fmt2)
                self.data.VREPR.append(rep)
        self.logger.debug('VMISS=%s', self.data.VMISS)
        self.logger.debug('VFORMAT=%s', self.data.VFORMAT)

    @staticmethod
    def _get_vmiss_fmt(vmiss_str):
        """
        Analyzes the vmiss string and returns information on it.
        Parameters:
            vmiss_str    string containing one vmiss value
        Returns:
            tupel: (val, fmt, fmt2, rep)
                value of the vmiss value (str)
                format string for the data variable (str)
                short format string for the data variable, (without padding,
                    just number of digits after comma) (str)
                representation of the data variable (data type)
        """
        (val, fmt, fmt2, rep) = (None, None, None, float)
        reg = re.match('^-?0[xX]([0-9a-fA-F]+)$', vmiss_str.strip())
        if reg:
            # hex format
            try:
                _ = HexInt(vmiss_str)
            except ValueError:
                raise ValueError("'{}: illegal number format".format(vmiss_str))
            vk_ = len(reg.group(1))
            if vk_ > math.log(sys.float_info.epsilon)/math.log(16)*-1:
                raise ValueError(
                    "'{}': long hex (>13 digits) is not supported".format(
                        vmiss_str))
            else:
                val = vmiss_str.strip()
                fmt = '#0{}x'.format(vk_ + 2)
                fmt2 = '#0{}X'.format(vk_ + 2)
                # fmt2: must be upper case X, that way we can avoid one upper()
                # when checking the data format
                rep = HexInt
        else:
            try:
                _ = float(vmiss_str)
            except ValueError:
                raise ValueError("'{}': illegal number format".format(
                    vmiss_str))
            val = vmiss_str.strip()
            reg = re.match(r"^-?(\d*)(\.(\d*))?$", val)
            if reg:
                vk_ = len(reg.group(1))
                nk_ = len(reg.group(3)) if reg.group(3) else 0
                kk_ = len(reg.group(2)) if reg.group(2) else 0
                fmt = '{}.{}f'.format(vk_ + kk_ + 1, nk_)
                fmt2 = '.{}f'.format(nk_)
            else:
                reg = re.match(r"^-?(\d*)(\.(\d*))?((e|E)[+-]?(\d+))$", val)
                if reg:
                    vk_ = len(reg.group(1))
                    nk_ = len(reg.group(3)) if reg.group(3) else 0
                    kk_ = len(reg.group(2)) if reg.group(2) else 0
                    exp = len(reg.group(6)) if reg.group(6) else 2
                    if exp < 2:
                        exp = 2
                    fmt = '{}.{}E'.format(vk_ + kk_ + exp + 3, nk_)
                    fmt2 = '.{}E'.format(nk_)
                    # fmt2: must be upper case E, that way we can avoid one
                    # upper() when checking the data format
                else:
                    raise ValueError("'{}': illegal number format".format(val))
            if vk_ + nk_ > math.log10(sys.float_info.epsilon)*-1:
                # this variable can not be accurately expressed as
                # float
                rep = Decimal
        return (val, fmt, fmt2, rep)

    def _read_vname(self):
        """
        Reads the VNAME lines from a NASA Ames 1001 file.
        Parameters:
            None
        Returns:
            None
        Raises:
            NasaAmes1001Error   on syntax error
        """
        self.data.VNAME = []
        for i in range(self.data.NV):
            self.data.VNAME.append(self._read_header_line())
            if re.match(r"^\d$", self.data.VNAME[-1]):
                # this is a "fuzzy" error: this is mainly for cases where NV is
                # set too low, and NSCOM is interpreted as variable name
                # (which really messes up the whole parsing after this point)
                self.error(
                    "VNAME[{}]: variable name syntax error. '{}' is not a "
                    "valid VNAME (check if NV in line 10 is set correctly)".\
                        format(i, self.data.VNAME[-1]))
                raise NasaAmes1001Error("Exiting because of previous errors")
        self.logger.debug('VNAME=%s', self.data.VNAME)

    def _read_scoml(self):
        """
        Read the complete SCOML comment block.
        Parameters:
            None
        Returns:
            None
        """
        line = self._read_header_line()
        if not re.match(r'^\d+$', line):
            self.error('NSCOML: syntax error', exception=True)
        nscoml = int(line)
        self.data.SCOML = []
        for _ in range(nscoml):
            self.data.SCOML.append(self._read_header_line())
        self.logger.debug('SCOML=%s', self.data.SCOML)

    def _read_ncoml(self):
        """
        Read the complete NCOML comment block.
        Parameters:
            None
        Returns:
            None
        """
        line = self._read_header_line()
        if not re.match(r'^\d+$', line):
            self.error('NNCOML: syntax error', exception=True)
        nncoml = int(line)
        if self.data.NLHEAD != self.lnum + nncoml:
            self.error('NLHEAD and NNCOM are inconsistent', exception=True)
        self.data.NCOML = []
        for _ in range(nncoml):
            self.data.NCOML.append(self._read_header_line())
        self.logger.debug('NCOML=%s', self.data.NCOML)

    def _read_data(self, skip_data=False):
        """
        Read the complete data block.
        Parameters:
            skip_data   skip reading of data (speedup, if data are not needed at
                        application level). First and last line are read.
        Returns:
            None
        """
        self.data.DATA = []
        for _ in range(self.data.NV + 1):
            self.data.DATA.append([])
        skipped = False

        self.vmiss_vals = [_typeconvert(self.data.VMISS[i], self.data.VREPR[i])
                           if self.data.VMISS[i] is not None else None
                           for i in range(self.data.NV)]
        while True:
            if self.lnum % 1000 == 0:
                self.logger.log(INFO_MINUS, "reading line %d", self.lnum)
            try:
                line = self._readline()
            except EOFError:
                break
            self._add_data(line, skip_data)
            if skip_data and not skipped:
                try:
                    self.file.goto_line(-2, allow_backpos=False)
                except BackposError:
                    return
                skipped = True
        self.vmiss_vals = None
        # write all condensed messages and reset condenser object:
        self.msg_condenser.deliver()

    def _add_data(self, line, skip_data=False):
        """
        Add 1 line of data to internal store.
        Parameters:
            line     line of data from file (str)
            skip_data    only read first and last line (speedup, if data are not
                         needed on application level)
        Returns:
            None
        """
        def strip(val):
            """
            Strip a leading + sign, then substitute all 0 if not like "0.".
            This is needed for the number format check below.
            """
            # optimize runtime: quickly return in usual cases, and do not copy
            if val[0] not in ('+', '0') or val[0:2] == '0.':
                return val
            # else: not so performant...
            i = 0
            if val[0] == '+':
                i = 1
            while val[i] == '0' and len(val) > i+1:
                i += 1
            if i > 0 and val[i-1] == '0' and val[i] in ('.', 'x', 'X'):
                i -= 1
            return val[i:]

        if self.strictness & self.__class__.STRICT_NUMFORMAT:
            values = [strip(val) for val in line.split()]
        else:
            values = line.split()
        if len(values) != self.data.NV + 1:
            self.msg_condenser.add(
                self.error, MSG_NUM_VAL_ERR, None,
                'data line does not contain {} values'.format(self.data.NV + 1),
                self.lnum)
        if not values:
            return
        try:
            self._add_x_value(values[0], skip_data)
        except ValueError:
            return  # error parsing x-value: skip this data line
        for cnum in range(1, self.data.NV + 1):
            value = None
            if cnum < len(values):
                try:
                    value = _typeconvert(values[cnum], self.data.VREPR[cnum-1])
                except ValueError as excpt:
                    self.msg_condenser.add(
                        self.error, MSG_CVT_ERR, cnum,
                        "DATA[{}]: {}".format(cnum, str(excpt)),
                        self.lnum)

            if value is not None:
                if self.vmiss_vals[cnum-1] is not None and \
                   value == self.vmiss_vals[cnum-1]:
                    value = None
                # check dependent variable:
                elif self.vmiss_vals[cnum-1] is not None and \
                   value > self.vmiss_vals[cnum-1]:
                    self.msg_condenser.add(
                        self.error, MSG_VMISS_ERR, cnum,
                        "DATA[{}]: value ({}) > VMISS ({}, missing value "
                        "specified in line 12) is not allowed."
                        .format(cnum, value, self.data.VMISS[cnum-1]),
                        self.lnum)
                # number format checks:
                # convert the numeric value back to string using the format
                # specifier based on the VMISS. The strings should be identical
                # This is a very expansive operation, and it's performed for
                # each value!
                # 2018/07: PE: optimizations:
                #  - used the new VFORMAT2 instead of VFORMAT (which spared a
                #    strip operation)
                #  - used capital E (exponent) and X (HexInt) in VFORMAT2 and
                #    uses upper on the right hand comparison argument,
                #    So instead of .lower() != .lower, we need just one upper()
                #  - unfortunately found no way to avoid the expansove string
                #    operations
                elif (self.strictness & self.__class__.STRICT_NUMFORMAT) and \
                    self.data.VFORMAT2[cnum-1] and \
                    '{:{}}'.format(value, self.data.VFORMAT2[cnum-1]) != \
                        values[cnum].upper():
                    self.msg_condenser.add(
                        self.error, MSG_VFORMAT_ERR, cnum,
                        "DATA[{}]: value ({}) does not match VMISS format "
                        "({}, missing value specified in line 12)".format(
                            cnum, values[cnum], self.data.VMISS[cnum-1]),
                        self.lnum)
            self.DATA[cnum].append(value)

    def _add_x_value(self, valuestr, skip_data=False):
        """
        Adds next x value to the internal data structure.
        Parameters:
            valuestr    the value to be added (as string read from the file)
            skip_data   only read first and last line (speedup, if data are not
                        needed on application level)
        Returns:
            None
        Raises:
            ValueError   if string is malformatted (can not be interpreted as
                         float)
        """
        # generate xmindig while reading line by line
        try:
            mindig = minmaxdig(valuestr)[0]
        except ValueError:
            self.msg_condenser.add(
                self.error, MSG_CVT_ERR, 0,
                "DATA[0]: '{}' is not a float value. Skipping this "
                "data line".format(valuestr), self.lnum)
            raise
        if self.xmindig is None:
            self.xmindig = mindig
        else:
            self.xmindig = min(self.xmindig, mindig)

        value = None
        try:
            value = _typeconvert(valuestr, float)
        except ValueError as excpt:
            self.msg_condenser.add(
                self.error, MSG_CVT2_ERR, 0,
                'DATA[0]: ' + str(excpt) + ". Skipping this data line",
                self.lnum)
            raise

        if self.data.DATA[0] and self.data.DATA[0][-1] >= value:
            self.msg_condenser.add(
                self.error, MSG_XINC_ERR, 0,
                'DATA[0]: independent variable must be strictly increasing',
                self.lnum)
        if not skip_data and self.data.DX != None and self.data.DX != 0 and \
           self.data.DATA[0] and \
           not self._dx_equal(self.data.DX, abs(value-self.data.DATA[0][-1])):
            self.msg_condenser.add(
                self.error, MSG_XINCDX_ERR, 0,
                'DATA[0]: independent variable does not increase by specified '
                'DX', self.lnum)
        self.data.DATA[0].append(value)

    def _read_header_line(self):
        """
        Reads next header line from file.
        Raises Exceptions if number of header lines is not correct.
        Parameters:
            None
        Returns:
            header line (string)
            None if EOF
        Raises:
            NasaAmesError  if not enough lines in header (according to NLHEAD)
            EOFError       on unexpected EOF
        """
        if self.lnum >= self.data.NLHEAD:
            self.error("incomplete NASA Ames header (missing from " +\
                       "{}, NLHEAD was {})".format(self.curr_state_name(),
                                                   self.data.NLHEAD))
        try:
            return self._readline()
        except EOFError:
            self.error("unexpected end of file", exception=True)

    def _readline(self):
        """
        Reads one line from file and fills the objects line attribute.
        Parameters:
            None
        Returns:
            line read (str)
        Raises:
            EOFError
        """
        self.lnum += 1
        return self.file.readline()

    def ascii_read_error_callback(self, msg):
        """
        Callback method for AsciiRead error message handling.
        Parameters:
            msg    message
        Returns:
            False: prevent AsciiRead from handling the error by itself
        """
        self.error(msg, lnum=True, exception=True)
        return False

    def ascii_read_warning_callback(self, msg):
        """
        Callback method for AsciiRead warning message handling.
        Parameters:
            msg    message
        Returns:
            False: prevent AsciiRead from handling the warning by itself
        """
        self.warning(msg, lnum=True)
        return False

def _typeconvert(value, targettype):
    """
    Type conversion for data values. float, Decimal and HexInt are supported.
    Parameters:
        value        source value (str)
        targettype   target data type (float, Decimal, HexInt)
    """
    try:
        conv = targettype(value)
    except (ValueError, InvalidOperation):
        # float raises ValueError, Decimal raises InvalidOperation
        # we always raise ValueError:
        raise ValueError("'{}' is not a {} value"
                         .format(value, targettype.__name__))
    if math.isnan(conv) or math.isinf(conv):
        # Problem: different string representations of inf, -inf and nan are
        # possible in float and Decimal (e.g. Inf, -inf, infinity, NaN, nan).
        # Solution: check after conversion with math.isinf and math.isnan
        # instead of parsing the string representation.
        # math does support all used types: int (HexInt based on int), float
        # and Decimal.
        raise ValueError("'{}' is not allowed as {} value in NasaAmes1001".\
              format(value, targettype.__name__))
    return conv

def minmaxdig(floatstr):
    """
    Calculates the minimum and maximum digit for a float value represented in
    a string.
    Parameters:
        floatstr    string representing a float number
    Returns:
        magnitude of minimum and maximum digit used in the number
    Raises:
        ValueError   if string is malformatted (can not be interpreted as float)
    """
    reg = re.match(r'^-?([0-9]*)(\.([0-9]*))?((E|e)(([+-])?[0-9]*))?$',
                   floatstr)
    if not reg:
        raise ValueError('string is not a float representation')
    maxdig = len(reg.group(1)) if reg.group(1) else 0
    maxdig += int(reg.group(6)) if reg.group(6) else 0
    mindig = len(reg.group(3)) * -1 if reg.group(3) else 0
    mindig += int(reg.group(6)) if reg.group(6) else 0
    return (mindig, maxdig)
