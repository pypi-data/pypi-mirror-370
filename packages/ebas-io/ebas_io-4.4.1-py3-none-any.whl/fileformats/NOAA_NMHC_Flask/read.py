"""
NOAA NMHC Flask data file format
   partial class for reading

$Id: read.py 2706 2021-09-14 08:57:09Z pe $
"""

from .base import NOAA_NMHC_Flask_Base, NOAA_NMHC_Flask_Rawdata_Base, \
    NOAA_NMHC_Flask_Header_Base, NOAA_NMHC_Flask_Data_Base, \
    NOAA_NMHC_Flask_HeaderContact_Base, NOAA_NMHC_Flask_HeaderDescription_Base,\
    NOAA_NMHC_Flask_Error
from six import string_types
import re
import datetime
from nilutility.datetime_helper import datetime_parse_iso8601

class NOAA_NMHC_Flask_ReadError(NOAA_NMHC_Flask_Error):
    """
    Exception class for read errors.
    """
    pass


class NOAA_NMHC_Flask_Rawdata_Read(NOAA_NMHC_Flask_Rawdata_Base):
    """
    Partial class for reading raw data from the file.
    """
    def parse(self, raw_data):
        """
        Parses the raw data (parse number of header lines, split into header
        and data.
        """
        self.raw_data = raw_data
        reg = re.match(r'^# number_of_header_lines: *(\d*)$', raw_data[0])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError("not a NOAA_NMHC_Flask file")
        self.num_hea_lines = int(reg.group(1))
        if self.num_hea_lines > len(self.raw_data):
            raise NOAA_NMHC_Flask_ReadError(
                "less lines in file then specified number_of_header_lines in "
                "first line")
        self.header = self.raw_data[0:self.num_hea_lines]
        self.data = self.raw_data[self.num_hea_lines:]

class NOAA_NMHC_Flask_HeaderContact_Read(NOAA_NMHC_Flask_HeaderContact_Base):
    """
    Partial class for parsing the contact information from the file header.
    """
    def parse(self, index, rawhea):
        """
        Parses a contact information block from the file header.
        Parameters:
            index      start index of the contact block
            rawhea     raw header lines (header attribute from
                       NOAA_NMHC_Flask_Rawdata object)
        Returns:
            index of the line following the block
        Syntax of a contact block:
            # contact_parameter: IC4H10 ARL (Individual Flasks)\n
            # contact_name: Detlev Helmig\n
            # contact_telephone: (303) 492-2509\n
            # contact_email: Detlev.Helmig@colorado.edu\n
        """
        reg = re.match(r'^# contact_parameter: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# contact_parameter'".format(index + 1))
        self.parameter = reg.group(1)
        index += 1

        reg = re.match(r'^# contact_name: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# contact_name'".format(index + 1))
        self.name = reg.group(1)
        index += 1

        reg = re.match(r'^# contact_telephone: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# contact_telephone'".format(index + 1))
        self.telephone = reg.group(1)
        index += 1

        reg = re.match(r'^# contact_email: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# contact_email'".format(index + 1))
        self.email = reg.group(1)
        index += 1

        return index


class NOAA_NMHC_Flask_HeaderDescription_Read(
        NOAA_NMHC_Flask_HeaderDescription_Base):
    """
    Partial class for parsing the description information from the file header.
    """
    def parse(self, index, rawhea):
        """
        Parses a description information block from the file header.
        Parameters:
            index      start index of the contact block
            rawhea     raw header lines (header attribute from
                       NOAA_NMHC_Flask_Rawdata object)
        Returns:
            index of the line following the block
        Syntax of a description block:
            # description_site-code: zep\n
            # description_project-abbr: ccg_surface\n
            # description_strategy-abbr: flask\n
            # description_sample-constraints: date:1900-01-01,2016-12-31\n
            # description_creation-time: 2017-02-01 16:54:49\n
        """
        reg = re.match(r'^# description_site-code: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# description_site-code'".format(index + 1))
        self.site_code = reg.group(1)
        if not re.match(r'^[a-z]{3}$', self.site_code):
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: site_code must be 3 characters, lower case'".format(
                    index + 1))
        index += 1

        reg = re.match(r'^# description_project-abbr: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# description_project-abbr'".format(
                    index + 1))
        self.project_abbr = reg.group(1)
        index += 1

        reg = re.match(r'^# description_strategy-abbr: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# description_strategy-abbr'".format(
                    index + 1))
        self.strategy_abbr = reg.group(1)
        if (self.strategy_abbr != 'flask'):
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: only flask is supported for strategy_abbr".format(
                    index + 1))
            # other file content might need changes in the implementation?
        index += 1

        reg = re.match(r'^# description_sample-constraints: *(.*)$',
                       rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# description_sample-constraints'".format(
                    index + 1))
        self.sample_constraints = reg.group(1)
        index += 1

        reg = re.match(r'^# description_creation-time: *(.*)$', rawhea[index])
        if not reg:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: expected '# description_creation-time'".format(
                    index + 1))
        try:
            self.creation_time = datetime_parse_iso8601(
                reg.group(1).replace(" ","T"))
        except ValueError:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: illegal time string {}'".format(
                    index + 1, reg.group(1)))
        index += 1

        return index


class NOAA_NMHC_Flask_Header_Read(NOAA_NMHC_Flask_Header_Base):
    """
    Partial class for parsing the header part of the file.
    """
    def parse(self, rawhea):
        """
        Parses the header information from the raw data object
        (NOAA_NMHC_Flask_Rawdata).
        Parameters:
            rawhea     raw header lines (header attribute from
                       NOAA_NMHC_Flask_Rawdata object)
        Returns:
            None
        """
        from .__init__ import NOAA_NMHC_Flask_HeaderContact, \
            NOAA_NMHC_Flask_HeaderDescription, NOAA_NMHC_Flask_Data

        i = 1  # skip first line (number_of_header_lines)
        while  i < len(rawhea):
            if rawhea[i].startswith('# comment:'):
                start = i
                i += 1
                while i < len(rawhea):
                    if not rawhea[i].startswith('# comment:'):
                        break
                    i += 1
                block = rawhea[start:i]
                self.comments.append(block)
            elif rawhea[i].startswith('# contact_parameter: '):
                contact = NOAA_NMHC_Flask_HeaderContact()
                i = contact.parse(i, rawhea)
                self.contact.append(contact)
            elif rawhea[i].startswith('# collaborator_name: '):
                reg = re.match(r'^# collaborator_name: *(.*)$', rawhea[i])
                if not reg:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: collaborator_name could not be parsed".format(
                            i+1))
                self.collaborator_name.append(reg.group(1))
                i += 1
            elif rawhea[i].startswith('# collaborator_comment: '):
                reg = re.match(r'^# collaborator_comment: *(.*)$', rawhea[i])
                if not reg:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: collaborator_comment could not be parsed"\
                            .format(i+1))
                self.collaborator_comment.append(reg.group(1))
                i += 1
            elif rawhea[i].startswith('# collaborator_url: '):
                reg = re.match(r'^# collaborator_url: *(.*)$', rawhea[i])
                if not reg:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: collaborator_url could not be parsed".format(
                            i+1))
                self.collaborator_url.append(reg.group(1))
                i += 1
            elif rawhea[i].startswith('# collaborator_comment: '):
                reg = re.match(r'^# collaborator_comment: *(.*)$', rawhea[i])
                if not reg:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: collaborator_comment could not be parsed".format(
                            i+1))
                self.collaborator_comment.append(reg.group(1))
                i += 1
            elif rawhea[i].startswith('# description_site-code: '):
                if self.description:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: only one description block allowed".format(
                            i+1))
                description = NOAA_NMHC_Flask_HeaderDescription()
                i = description.parse(i, rawhea)
                self.description = description
            elif rawhea[i].startswith('# data_fields: '):
                if self.data_fields:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: only one line with data_fields allowed".
                        format(i+1))
                reg = re.match(r'^# data_fields: *(.*)$', rawhea[i])
                if not reg:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: error parsing data_fields".format(i+1))
                self.data_fields = reg.group(1).split()
                expected_data_fields = NOAA_NMHC_Flask_Data.DATA_FIELDS
                if self.data_fields != expected_data_fields:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}: expected data_fields {}, read {}".format(
                            i + 1, ', '.join(expected_data_fields),
                            ', '.join(self.data_fields)))
                i += 1
            else:
                self._logger.error(
                    "cannot parse header line '{}'".format(rawhea[i]))
                i += 1


class NOAA_NMHC_Flask_Data_Read(NOAA_NMHC_Flask_Data_Base):
    """
    Partial class for reading the data part of the file.
    """

    def parse(self, raw):
        """
        Parses the data section of the file.
        Parameters:
            raw    NOAA_NMHC_Flask_Rawdata object  
        Returns:
            None
        """
        for i in range(len(raw.data)):
            self._parse_data_line(len(raw.header)+i+1, raw.data[i])

    def _parse_data_line(self, lnum, data_line):
        """
        Parses one line of data and adds the data to the object.
        Parameters:
            lnum         line number (in file, 1 based, used for messages)
            data_line    raw string with one line of data
        Returns:
            None
        Raises:
            raise NOAA_NMHC_Flask_ReadError("not a NOAA_NMHC_Flask file")xx
        """
        data_list = data_line.split()
        if len(data_list) != 27:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: data line contains {} elements (27 expected)".format(
                    lnum, len(data_list)))
        for (i, elem) in enumerate(self.__class__.DATA_FIELDS):
            # do some type converstion:

            if elem in ('sample_year', 'sample_month', 'sample_day',
                        'sample_hour', 'sample_minute', 'sample_seconds',
                        'analysis_year', 'analysis_month', 'analysis_day',
                        'analysis_hour', 'analysis_minute', 'analysis_seconds'):
                # convert to integer
                try:
                    data_list[i] = int(data_list[i])
                except ValueError:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}, col {} ({}): expected integer value, "
                        "found '{}'".format(lnum, i, elem, data_list[i]))
            if elem in ('analysis_value', 'analysis_uncertainty',
                        'sample_latitude', 'sample_longitude',
                        'sample_altitude', 'sample_elevation',
                        'sample_intake_height'):
                # convert to float
                try:
                    data_list[i] = float(data_list[i])
                except ValueError:
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}, col {} ({}): expected float value, "
                        "found '{}'".format(lnum, i, elem, data_list[i]))
            # apply some additional actions or checks for some elements:
            if elem in ('analysis_value', 'analysis_uncertainty'):
                # set to None if missing -999.990 or -999.999
                if data_list[i] in (-999.990, -999.999):
                    data_list[i] = None
                elif data_list[i] < -5:
                    # Sanity checks: do not accept low negative values
                    # Maybe this limit needs to be adjusted
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}, col {} ({}): very low negative value "
                        "found '{}'".format(lnum, i, elem, data_list[i]))
                elif data_list[i] in (999.990, 999.999):
                    raise NOAA_NMHC_Flask_ReadError(
                        "line {}, col {} ({}): suspicious (missing?) value "
                        "found '{}'".format(lnum, i, elem, data_list[i]))
            # append to data attributes:
            self.__dict__[elem].append(data_list[i])

        # check elevation + intake_height == altitude:
        if abs(self.sample_altitude[-1] - self.sample_elevation[-1] - \
               self.sample_intake_height[-1]) > 0.01:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}: sample_elevation + sample_intake_height is not equal"
                "sample_altitude ({}+{}!={})".format(
                    lnum, self.sample_elevation[-1],
                    self.sample_intake_height[-1], self.sample_altitude[-1]))
        # set sample_time
        try:
            self.sample_time.append(datetime.datetime(
                self.sample_year[-1], self.sample_month[-1],
                self.sample_day[-1],
                self.sample_hour[-1], self.sample_minute[-1],
                self.sample_seconds[-1]))
        except ValueError as expt:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}, col 2-7 (sample time): {}".format(
                    lnum, expt.message))
        # set analysis_time
        try:
            self.analysis_time.append(datetime.datetime(
                self.analysis_year[-1], self.analysis_month[-1],
                self.analysis_day[-1],
                self.analysis_hour[-1], self.analysis_minute[-1],
                self.analysis_seconds[-1]))
        except ValueError as expt:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}, col 16-21 (analysis time): {}".format(
                    lnum, expt.message))

        # sample_time < analysis_time
        # 2021-05: initially, there were errors in many files.
        #          INSTAAR/NOAA investigated, conclusion was that analysis date
        #          is wrong, sample date OK. Changed to sample date in those
        #          cases.
        # --> accept analysis time == sample time for this reason
        if self.analysis_time[-1] < self.sample_time[-1]:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}, col 2-7, 16-21 (sample time and analysis time): "
                "sample time must be before analysis time".format(
                    lnum))

        if len(self.sample_time) > 1 and \
           self.sample_time[-2] > self.sample_time[-1]:
            raise NOAA_NMHC_Flask_ReadError(
                "line {}, col 2-7 (sample time): sample time must be "
                "monotonically increasing".format(lnum))


class NOAA_NMHC_Flask_Read(NOAA_NMHC_Flask_Base):
    """
    Partial class for reading a file.
    """

    def read(self, filespec):
        """
        Reads the file into the object.
        Parameters:
            filespec    file name (incl. path) or file like object (stream)
        Returns:
            None
        Raises:
            IOError                 file open error
            NOAA_NMHC_Flask_Error (or any derived class hereof)
                on any unrecoverable read error
        """
        if isinstance(filespec, string_types):
            self.filename = filespec
            with open(self.filename, "Ur") as self.file:
                self._logger.info("reading file " + self.filename)
                self._read()
        else:
            self.filename = None
            self._logger.info("reading from stream")
            self.file = filespec
            self._read()

    def _read(self):
        """
        Reads the file from opened file handle.
        This method is only needed to extract the reading functionality in order
        to wrap the 'with open(filename)' around it in the read() method.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Error (or any derived class hereof)
                on any unrecoverable read error
        """
        from .__init__ import NOAA_NMHC_Flask_Rawdata, NOAA_NMHC_Flask_Header, \
            NOAA_NMHC_Flask_Data
        self.raw = NOAA_NMHC_Flask_Rawdata()
        self.raw.parse(self.file.readlines())
        self.header = NOAA_NMHC_Flask_Header()
        self.header.parse(self.raw.header)
        self.data = NOAA_NMHC_Flask_Data(self.raw.num_hea_lines+1)
        self.data.parse(self.raw)
        self.check()
        #self.data.parse()
