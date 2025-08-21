"""
EANET precipitation chemistry file read
"""

import os
import re
import datetime
from fileformats.CsvUnicode import CsvUnicodeReader
from nilutility.datetime_helper import DatetimeInterval
from nilutility.numeric import digits_stat
from .base import EanetPrecipBase, EanetPrecipForm, EanetPrecipVariable, \
    EanetError, \
    from_address


class EanetPrecipRead(EanetPrecipBase):  # pylint: disable=R0902
    # R0902: Too many instance attributes
    """
    Class for reading EANET precip files
    """

    def __init__(self):
        """
        Initialize class.
        """
        EanetPrecipBase.__init__(self)
        self._rawdata = None
        self._merge_samples = []

    def read(self, filename):
        """
        Read from file.
        Parameters:
            filename    path and file name
        Returns:
            None
        Raises:
            IOError     in case of I/O issues
            EanetError  other raeding errors
        """
        self.logger.info('reading file %s', filename)
        self.file_name = os.path.basename(filename)
        self.parse_filename()
        self._read_file()

    def parse_filename(self):
        """
        Parses site code from filename, warnings if filename is not standard.
        Parameters:
            None
        Returns:
            None
        """
        reg = re.match(
            '([A-Z]{3}[0-9]{3})_([0-9]{4})_(wet_deposition).(csv)',
            self.file_name)
        if not reg:
            self.warning("Unconventional file name '%s'.",
                         self.file_name)
            reg = re.match('([A-Z]{3}[0-9]{3})_', self.file_name)
            if not reg:
                self.warning(
                    "Unable to parse site code from file name.")
                return
        self.site_code = reg.group(1)

    def _read_file(self):
        """
        Read the file content.
        Parameters:
            None
        Returns:
            None
        Raises: EanetError in case of errors
        """
        with open(self.file_name, 'rb') as fil:
            rdr = CsvUnicodeReader(fil)
            self._rawdata = [x for x in rdr]
        self._check_dimensions()
        self._read_metadata()
        self._check_form_headers()
        self._read_form_sample()
        self._read_form_data()

    def _check_dimensions(self):
        """
        Truncat empty lines, check number of columns.
        """
        # truncate empty lines at the end:
        chomp = 0
        while self._rawdata[-1] == [u'' for x in range(len(self._rawdata[-1]))]:
            del self._rawdata[-1]
            chomp += 1
        if chomp:
            self.warning("Ignored %s empty lines", chomp,
                         row=len(self._rawdata)-1, col=0)

        # check all lines have 252 columns:
        problems = [i for i, x in enumerate(self._rawdata) if len(x) != 252]
        if problems:
            txt = ', '.join(
                ["line {} [{} cols]".format(i+1, len(self._rawdata[i]))
                 for i in problems[:5]])
            if len(problems) > 5:
                txt += "..."
            self.error(
                "File contains %s lines with not exactly 252 columns: %s",
                len(problems), txt)
            raise  EanetError("Exiting because of previous errors")

    def _read_metadata(self):
        """
        Read metadata from the file. Check consistency of retundant metadata.
        """
        self.country_name = None
        self.site_name = None
        self.laboratory = None
        self.reporter = None
        self.funnel_diameter = None

        metadata_positions = [
            ['Country', 'country_name',
             ("B4", "D4"),
             ("AX4", "AZ4"),
             ("CH4", "CJ4"),
             ("DO4", "DQ4"),
             ("EQ3", "ER3"),
             ("FB3", "FC3"),
             ("GG3", "GH3"),
             ("HK3", "HL3")],
            ['Laboratory', 'laboratory',
             ("B6", "D6"),
             ("AX6", "AZ6"),
             ("CH6", "CJ6"),
             ("DO6", "DQ6")],
            ['Site', 'site_name',
             ("Q4", "S4"),
             ("BI4", "BK4"),
             ("CS4", "CU4"),
             ("DX4", "DY4"),
             ("EV3", "EW3"),
             ("FH3", "FI3"),
             ("GN3", "GO3"),
             ("HR3", "HS3")],
            ['Reporter', 'reporter',
             ("Q6", "T6"),
             ("BI6", "BL6"),
             ("CS6", "CV6"),
             ("DX6", "DZ6")],
            ['Funnel diameter', 'funnel_diameter',
             ("AG4", "AK4", "AM4"),
             ("BY4", "CC4", "CE4"),
             ("DF4", "DJ4", "DL4"),
             ("EH4", "EL4", "EN4")]]
        for meta in metadata_positions:
            for pos in meta[2:]:
                # lable:
                row, col = from_address(pos[0])
                if self._rawdata[row][col].strip() != meta[0]+' :':
                    self.error(
                        "expected '%s', found '%s'", meta[0]+' :',
                        self._rawdata[row][col], row=row, col=col)
                # value:
                target = meta[1]
                row, col = from_address(pos[1])
                if self.__dict__[target]:
                    if not self._rawdata[row][col]:
                        self.warning("Empty %s", meta[0], row=row, col=col)
                    if self.__dict__[target] != self._rawdata[row][col]:
                        self.error(
                            "Inkonsistent %s: '%s', found '%s' before",
                            meta[0], self._rawdata[row][col],
                            self.__dict__[target], row=row, col=col)
                elif self._rawdata[row][col]:
                    self.__dict__[target] = self._rawdata[row][col]
                # optional unit for funnel diameter:
                if meta[0] == 'Funnel diameter' and len(pos) == 3:
                    row, col = from_address(pos[2])
                    if self._rawdata[row][col].strip() != '[mm]':
                        self.error(
                            "expected '[mm]', found '%s'",
                            self._rawdata[row][col], row=row, col=col)
            if self.__dict__[target]:
                self.__dict__[target] = self.__dict__[target].strip()
        if self.funnel_diameter:
            try:
                self.funnel_diameter = int(self.funnel_diameter)
            except ValueError:
                self.error("funnel diameter '%s' is not numeric")
        if self.errors:
            raise  EanetError("Exiting because of previous errors")

    def _check_form_headers(self):
        """
        Check the forms layout
        """
        for formname, formdef in self.__class__.LAYOUT.items():
            row, col = from_address(formdef['header'])
            if self._rawdata[row][col] != formname:
                self.error(
                    "Expected '%s' but found '%s'",
                    formname, self._rawdata[row][col], row=row, col=col)
        if self.errors:
            raise EanetError("Exiting because of previous errors")

    def _read_form_sample(self):
        """
        Read sample numbers and sample times from all forms.
        """
        self._merge_samples = []
        for _, formdef in self.__class__.LAYOUT.items():
            row, col = from_address(formdef['start'])
            if formdef['sample_number']:
                sample_numbers = []
                if self._rawdata[row][col] != formdef['sample_number']:
                    self.error(
                        "Expected '%s' but found '%s'",
                        repr(formdef['sample_number']),
                        repr(self._rawdata[row][col]), row=row, col=col)
                else:
                    for i in range(row+3, len(self._rawdata)):
                        try:
                            sample_numbers.append(int(self._rawdata[i][col]))
                        except ValueError:
                            self.error(
                                "Non-integer sample number '%s'",
                                self._rawdata[i][col], row=i, col=col)
                if not self.sample_numbers:
                    self.sample_numbers = sample_numbers
                elif self.sample_numbers != sample_numbers:
                    self.error(
                        "Sample numbers sequence inconsistent (was different "
                        "before)", row=row, col=col)
                col += 1
            if formdef['sample_times']:
                sample_times = []
                check = (
                    ('Sampling period', 0, 0),
                    ('Start', 1, 0),
                    ('End', 1, 2),
                    ('Date', 2, 0),
                    ('Time', 2, 1),
                    ('Date', 2, 2),
                    ('Time', 2, 3))
                for chk in check:
                    if self._rawdata[row+chk[1]][col+chk[2]] != chk[0]:
                        self.error(
                            "Expected '%s', found '%s'", chk[0],
                            self._rawdata[row+chk[1]][col+chk[2]],
                            row=row+chk[1], col=col+chk[2])
                for i in range(row+3, len(self._rawdata)):
                    start = self._parse_datetime(i, col)
                    end = self._parse_datetime(i, col+2)
                    if start and end:
                        try:
                            intv = DatetimeInterval(start, end)
                        except (TypeError, ValueError) as excpt:
                            self.error(str(excpt), row=i, col=col)
                            sample_times.append(None)
                        else:
                            if sample_times and sample_times[-1] == intv:
                                # we assume this is an overflow sample
                                # take the sum of precipitation and the weighed
                                # arithmetic mean for concentrations and
                                # make one sample.
                                if i-row-3 not in self._merge_samples:
                                    # only write warning with first
                                    self.warning(
                                        'Duplicate sample times. '
                                        'Assuming overflow sample, will be '
                                        'merged to one sample.',
                                        row=i, col=col)
                                    self._merge_samples.append(i-row-3)
                                continue
                            sample_times.append(DatetimeInterval(start, end))
                            # check overlaps
                            if len(sample_times) > 1:
                                # look for last valid sample:
                                for samp in reversed(sample_times[:-1]):
                                    if samp:
                                        if samp[1] > sample_times[-1][0]:
                                            self.error(
                                                "Sample time overlap with "
                                                "previous valid sample: %s %s",
                                                samp, sample_times[-1],
                                                row=i, col=col)
                                        break
                    else:
                        sample_times.append(None)
                if not self.sample_times:
                    self.sample_times = sample_times
                elif self.sample_times != sample_times:
                    self.error(
                        "Sample times sequence inconsistent (was different "
                        "before)", row=row, col=col)
                col += 4
        if self.errors:
            raise EanetError("Exiting because of previous errors")

    def _read_form_data(self):
        """
        Read the data for all forms
        """

        def _cvt_flt(str_val, row, col):
            """
            Convert value to float or None.
            Parameters:
                str_val  string value
            Returns:
                float, None for missing
            Raises:
                ValueError in case of syntax errors
            """
            if str_val == '':
                return None
            try:
                return float(str_val)
            except ValueError as excpt:
                self.error(
                    "syntax error in value '{}': {}".format(
                        str_val, str(excpt)), row=row, col=col)

        def _cvt_int(str_val, row, col):
            """
            Convert value to int or None.
            Parameters:
                str_val  string value
            Returns:
                float, None for missing
            Raises:
                ValueError in case of syntax errors
            """
            if not str_val.strip():
                return None
            try:
                return int(str_val)
            except ValueError as excpt:
                self.error(
                    "syntax error in value '{}': {}".format(
                        str_val, str(excpt)), row=row, col=col)

        self.forms = []
        amount = None
        for formname, formdef in self.__class__.LAYOUT.items():
            form = EanetPrecipForm(self, len(self.forms), formname, formdef)
            self.forms.append(form)
            row, col = from_address(formdef['start'])
            if formdef['sample_number']:
                col += 1
            if formdef['sample_times']:
                col += 4
            for varname, vardef in formdef['vars'].items():
                if self._rawdata[row][col] == varname or \
                        (self._rawdata[row][col] == '' and \
                         varname.startswith('<EMPTY ')):
                    if vardef['flags']:
                        flags = [[_cvt_int(self._rawdata[i][j], i, j)
                                  for j in range(col+1, col+1+vardef['flags'])
                                  if self._rawdata[i][j].strip()]
                                 for i in range(row+3, len(self._rawdata))]
                    else:
                        flags = None
                    if varname.startswith("Date") or \
                            varname.startswith("Note"):
                        # use str without conversion
                        values = [self._rawdata[i][col]
                                  for i in range(row+3, len(self._rawdata))]
                    else:
                        values = [_cvt_flt(self._rawdata[i][col], i, col)
                                  for i in range(row+3, len(self._rawdata))]
                    form.variables.append(
                        EanetPrecipVariable(
                            varname, self._rawdata[row+2][col], values, flags))
                    if 'is_amount' in vardef and vardef['is_amount']:
                        # save the amount data, for later merging of samples
                        amount = list(values)
                else:
                    self.error(
                        "Expected variable name '%s', found '%s'",
                        '' if varname.startswith('<EMPTY ') else varname,
                        self._rawdata[row][col], row=row, col=col)
                col += 1 + vardef['flags']
        if self._merge_samples:
            # second loop to merge overflow samples
            for i in reversed(sorted(self._merge_samples)):
                for form in self.forms:
                    formdef = form.layout
                    for varname, vardef in formdef['vars'].items():
                        # seconf iteration: merge overflow samples if needed
                        var = form.var_by_name(varname)
                        if vardef['merge'] == 'mean':
                            if var.samples[i-1] is not None and \
                                    amount[i-1] and \
                                    var.samples[i] is not None and \
                                    amount[i]:
                                # get the rounding for all values:
                                mindig = digits_stat(var.samples)[2]
                                rnd = 0 if mindig is None \
                                    else -mindig if mindig < 0 \
                                    else -(mindig-1) if mindig > 0 \
                                    else 0
                                # calculate weighted mean and round
                                var.samples[i-1] = round(
                                    (var.samples[i] * amount[i] + \
                                     var.samples[i-1] * amount[i-1]) / \
                                     (amount[i] + amount[i-1]), rnd)
                                if var.flags:
                                    var.flags[i-1] += var.flags[i]
                            elif var.samples[i] is not None and \
                                    amount[i]:
                                var.samples[i-1] = var.samples[i]
                                if var.flags:
                                    var.flags[i-1] = var.flags[i]
                            # else, leave samples[i-1]
                        elif vardef['merge'] == 'sum':
                            var.samples[i-1] += var.samples[i]
                            if var.flags:
                                var.flags[i-1] += var.flags[i]
                        elif vardef['merge'] == 'concat':
                            var.samples[i-1] += ',' + var.samples[i]
                            if var.flags:
                                var.flags[i-1] += var.flags[i]
                        elif vardef['merge'] == 'first':
                            pass
                        else:
                            raise RuntimeError('unknown merge option {}'.format(
                                vardef['merge']))
                        del var.samples[i]
                        if var.flags:
                            del var.flags[i]
                amount[i-1] += amount[i]
        if self.errors:
            raise EanetError("Exiting because of previous errors")


