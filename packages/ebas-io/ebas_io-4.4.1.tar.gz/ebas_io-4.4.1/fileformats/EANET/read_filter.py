"""
EANET filter file read
"""

import os
import re
import datetime
from collections import defaultdict
from fileformats.CsvUnicode import CsvUnicodeReader
from nilutility.datetime_helper import DatetimeInterval
from .base import EanetError
from .base import EanetFilterBase, EanetFilterVariable


class EanetFilterRead(EanetFilterBase):
    """
    Class for reading EANET filter files
    """

    def __init__(self):
        """
        Initialize class.
        """
        EanetFilterBase.__init__(self)
        self._rawdata = None
        self._sample_time_flags = []

    def read(self, filename):
        """
        Read from file.
        Parameters:
            filename    path and file name
        Returns:
            None
        Raises:
            IOError     in case of I/O issues
            EanetError  other unrecoverable raeding errors
        """
        self.logger.info('reading file %s', filename)
        self.file_name = filename
        self.parse_filename()
        self._read_file()
        if self.errors:
            raise EanetError("Exiting because of previous errors")

    def parse_filename(self):
        """
        Parses site code from filename, warnings if filename is not standard.
        Parameters:
            None
        Returns:
            None
        """
        basename = os.path.basename(self.file_name)
        reg = re.match(
            '([A-Z]{3}[0-9]{3})_([0-9]{4})_(dry_deposition_filter_pack).(csv)',
            basename)
        if not reg:
            self.logger.warning("Unconventional file name '%s'.", basename)
            reg = re.match('([A-Z]{3}[0-9]{3})_', basename)
            if not reg:
                self.logger.warning(
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
        Raises: EanetError in case of unrecoverable errors
        """
        with open(self.file_name, 'rb') as fil:
            rdr = CsvUnicodeReader(fil)
            self._rawdata = [x for x in rdr]
        self._check_headerline()
        self._check_units()
        self._check_column_numbers()
        self._read_country()
        self._read_site_name()
        self._read_sample_times()
        self._read_variables()
        self.notes = [None if x[-1] == '' else x[-1] for x in self._rawdata[2:]]

    def _check_headerline(self):
        """
        Check the header line (line2).
        """
        if self._rawdata[1][:6] != ['Country', 'Site', 'Date', 'Time', 'Date',
                                    'Time']:
            self.error(
                'Format error: The first 6 elements in the second line must be '
                "'Country', 'Site', 'Date', 'Time', 'Date', 'Time'",
                row=1, col=0)
        if self._rawdata[1][-1] == 'Note':
            # Notes in the last column, read last column as notes, not as var
            self._hasnotes = True
            self._lastcol = len(self._rawdata[1]) - 1
        else:
            # No Notes in last column, read all columns as data
            self._hasnotes = False
            self._lastcol = len(self._rawdata[1])
        for i, varname in enumerate(self._rawdata[1][6:self._lastcol]):
            if varname.strip() == '':
                self.error("No variable name", row=1, col=i)
                # in order to be able to recover from this error:
                self._rawdata[1][i] = 'NoName{}'.format(i-5)

    def _check_units(self):
        """
        Checks line 1 of the file: Units
        """
        if any([self._rawdata[0][i] != '' for i in range(5)]):
            self.error(
                'Format error: The first 5 elements in the first line must be '
                'empty.', row=0, col=0)
        if self._rawdata[0][5] != u'Unit':
            self.error(
                "Format error: The 6. element in the first line must be 'Unit'",
                row=0, col=5)
        if self._hasnotes and self._rawdata[0][-1] != '':
            self.error(
                "Format error: The last element in the first line "
                "(unit for 'Note') must be empty",
                row=0, col=len(self._rawdata[0]-1))
        for i, unit in enumerate(self._rawdata[0][6:self._lastcol]):
            if unit.strip() == '':
                self.error("No unit", row=0, col=i)

    def _check_column_numbers(self):
        """
        Check the number of columns in all lines is equal.
        Parameters:
            None
        Returns:
            None
        Raises: EanetError in case of unrecoverable errors
        """
        occ = defaultdict(list)  # occurrences of different column counts
        for i, row in enumerate(self._rawdata):
            occ[len(row)].append(str(i+1))
        if len(occ) > 1:
            self.error("Different column numbers in file: " + \
                       self._occ_to_str(occ, add_spec='columns'))
            # unrecoverable error
            raise EanetError("Exiting because of previous errors")

    def _read_country(self):
        """
        Read the country column.
        """
        occ = defaultdict(list)  # occurrences of different countries
        for i, row in enumerate(self._rawdata[2:]):
            occ[row[0]].append(str(i+3))
        if len(occ) > 1:
            self.error("Different country names in file (column 1): " +\
                       self._occ_to_str(occ))
        self.country_name = self._rawdata[2][0]

    def _read_site_name(self):
        """
        Read the site name column.
        """
        occ = defaultdict(list)  # occurrences of different sites
        for i, row in enumerate(self._rawdata[2:]):
            occ[row[1]].append(str(i+3))
        if len(occ) > 1:
            self.error("Different site names in file (column 2): " +\
                       self._occ_to_str(occ))
        self.site_name = self._rawdata[2][1]

    def _read_sample_times(self):
        """
        Read the sample times from the file's rawdata array.
        Parameters:
            None
        Returns:
            None
        """
        self.sample_times = []
        self._sample_time_flags = []
        for i, row in enumerate(self._rawdata[2:]):
            flags = []
            start = self._parse_datetime(i+2, 2)
            end = self._parse_datetime(i+2, 4)
            try:
                sample = DatetimeInterval(start, end)
                # DatetimeInterval checks for start < end
            except (TypeError, ValueError) as excpt:
                self.error(
                    "Start/end date/time: %s", str(excpt),
                    row=i+2, col=2)
                sample = DatetimeInterval(None, None)
            if i and self.sample_times[i-1][1] and \
                    sample[0] and self.sample_times[i-1][1] > sample[0]:
                # overlap!
                if sample[0].second == 0 and sample[0].minute == 0 and \
                        sample[0].hour == 0:
                    self.warning(
                        "sample time overlap %s %s. Changing start time to %s "
                        "and flagging with flag 249.",
                        self.sample_times[i-1], sample,
                        self.sample_times[i-1][1],
                        row=i+2, col=2)
                    sample[0] = self.sample_times[i-1][1]
                    flags.append(249)
                else:
                    self.warning(
                        "sample time overlap %s %s. Changing end time to %s and "
                        "flagging with flag 249.",
                        self.sample_times[i-1], sample, sample[0],
                        row=i+1, col=4)
                    self.sample_times[i-1][1] = sample[0]
                    self._sample_time_flags[-1].append(249) 
            self.sample_times.append(sample)
            self._sample_time_flags.append([])

    def _read_variables(self):
        """
        Read all data from the file's rawdata array.
        Parameters:
            None
        Returns:
            None
        """
        for i in range(6, self._lastcol):
            values, flags = self._get_values(i)
            self.variables.append(EanetFilterVariable(
                self._rawdata[1][i].strip(), self._rawdata[0][i].strip(),
                values, flags))

    def _get_values(self, i):
        """
        Get the values for one variable.
        Parameters:
            i      column index
        Returns:
            list of values (float, None for missing)
        """
        def _cvt(str_val, var_name, i, j):
            """
            Convert value to float or None.
            Parameters:
                str_val  string value
            Returns:
                float, None for missing
            """
            if str_val == '':
                return None, [999]
            flags = []
            if str_val[0] == '<':
                str_val = str_val[1:].strip()
                flags = [781]
            try:
                return float(str_val), flags
            except ValueError as excpt:
                self.error(
                    "Syntax error in value for variable %s: %s",
                    var_name, str(excpt),
                    row=j, col=i)
                return None, [999]

        values = []
        flags = []
        for j, val in enumerate(self._rawdata[2:], 2):
            value, flag = _cvt(val[i], self._rawdata[1][i], i, j)
            flag += self._sample_time_flags[j-2]
            values.append(value)
            flags.append(flag)
        return values, flags

    @staticmethod
    def _occ_to_str(occ, add_spec=''):
        """
        Generates string for error messages in case of different occurences.
        Parameters:
            occ        occurence dictionary (occurences: list(line numbers))
            add_spec   additional specifier (optional)
        Returns:
            str summarising the different occurrences (used for error messages)
        """
        if add_spec:
            add_spec = ' ' + add_spec
        return ", ".join(
            ["{} {} containing {}{} ({})".format(
                len(x[1]), 'rows' if len(x[1]) > 1 else 'row',
                x[0],
                add_spec,
                ('lines ' if len(x[1]) > 1 else 'line ') +
                ', '.join(
                    (x[1][:3] + ['...']) if len(x[1]) > 3 else x[1]))
             for x in sorted(
                 occ.iteritems(),
                 key=lambda k, v: len(v),
                 reverse=True)])
