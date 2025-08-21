"""
ebas/nasa_ames/read/parse.py
$Id: parse.py 2585 2020-12-09 21:25:41Z pe $

parser for file input functionality for EBAS NASA Ames module
parses NasaAmes1001 object and builds NasaAems

History:
V.1.0.0  2013-06-22  pe  initial version

"""

import re
import datetime
from nilutility.ndecimal import Decimal
from nilutility.datatypes import DataObject
from nilutility.datetime_helper import datetime_round, DatetimeInterval
from nilutility.string_helper import list_splitter, ListSplitterNewlineError, \
        ListSplitterNullbyteError
from ebas.domain.masterdata.dl import EbasMasterDL
from ebas.domain.masterdata.pr import EbasMasterPR
from ..base import EbasNasaAmesReadError
from ...base import EBAS_IOFORMAT_NASA_AMES
from ...basefile.base import  EbasMetadataInvalid
from .parse_variables import NasaAmesPartialReadParserVariables
from .parse_ebasmetadata import NasaAmesPartialReadParserEbasMetadata
from ....ebasmetadata import EbasMetadata, EbasMetadataError

class NasaAmesPartialReadParser(# pylint: disable=R0901, W0223
        NasaAmesPartialReadParserVariables,
        NasaAmesPartialReadParserEbasMetadata):
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Parser for Nasa Ames I/O object.
    This is a base class for NasaAmesPartialRead
    """

    def parse_nasa_ames_1001(self, skip_variables=None, ignore_parameter=False):
        """
        Converts the NasaAmes1001 object into an EBAS NasaAmes Object.
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
        Raises:
            EbasNasaAmesReadError
        """
        # read ahead through the NCOM line in order to get the Data definition
        self._get_file_format(
            self.nasa1001.data.NCOML,
            13 + self.nasa1001.data.NV+ 1 + len(self.nasa1001.data.SCOML))
        self.metadata.originator = self._parse_persons(self.nasa1001.data.ONAME,
                                                       2)
        self.logger.debug(u'originator={}'.format(self.metadata.originator))
        self._parse_org(self.nasa1001.data.ORG)
        self.metadata.submitter = self._parse_persons(self.nasa1001.data.SNAME,
                                                      4)
        self.logger.debug(u'submitter={}'.format(self.metadata.submitter))
        self._parse_projects()
        if self.nasa1001.data.IVOL != 1:
            self.error('IVOL must be 1', lnum=6)
        if self.nasa1001.data.NVOL != 1:
            self.error('NVOL must be 1', lnum=6)
        self.metadata.reference_date = self.nasa1001.data.DATE
        self.metadata.revdate = self.nasa1001.data.RDATE
        self._parse_xname(self.nasa1001.data.XNAME)
        if self.nasa1001.data.NV < 3:
            # end_time, value, numflag is minimum!
            self.error('NV can not be less than 3', lnum=10)
        for vnum in [k for k in range(len(self.nasa1001.data.VSCAL))
                     if self.nasa1001.data.VSCAL[k] != 1.0]:
            self.error('VSCAL[{}]: only 1 is allowed'.format(vnum), lnum=11)
        # parse ncoml before variables: that way FT_TYPE and CO_COMP_NAME is
        # known (needed for characteristics check)
        self._parse_ncoml(
            self.nasa1001.data.NCOML,
            13 + self.nasa1001.data.NV + 1 + len(self.nasa1001.data.SCOML))
        self._parse_variables(skip_variables=skip_variables,
                              ignore_parameter=ignore_parameter)
        # _parse_title depends on varioables!
        self._parse_title(
            self.nasa1001.data.NCOML[-1],
            13 + self.nasa1001.data.NV + 1 + len(self.nasa1001.data.SCOML) +
            len(self.nasa1001.data.NCOML))
        self._parse_scoml(self.nasa1001.data.SCOML, 13 + self.nasa1001.data.NV)
        # set method_analytical MUST happen before check_mandatory!
        self._set_method_analytical()
        # check mandatory must happen here, sets read_tmp.hea_error if critical
        # metadata are missing, so that data cannot be read
        self.check_mandatory_metadata()
        if self.internal.read_tmp.hea_error:
            self.logger.info("Skip reading data because of severe errors in "
                             "header")
            raise EbasNasaAmesReadError(
                "{} Errors, {} Warnings".format(self.errors,
                                                self.warnings))
        self._parse_data(
            self.nasa1001.data.DATA,
            13 + self.nasa1001.data.NV + 1 + len(self.nasa1001.data.SCOML) + 1 +
            len(self.nasa1001.data.NCOML))
        self.check_timespec_metadata()

    def check_mandatory_metadata(self):
        """
        Check mandatory metadata according to metadata definition.
        Parameters:
            None
        Returns:
            None
        """
        for elem in self.internal.ebasmetadata.metadata:
            if (elem['main'] & 4 or elem['main'] & 8) and \
               (elem['key'] not in self.metadata or \
               self.metadata[elem['key']] is None):
                self.error("mandatory metadata attribute '{}' missing"
                           .format(elem['tag']))
                if elem['main'] & 8:
                    self.internal.read_tmp.hea_error = True
            if elem['vname'] & 4 or elem['vname'] & 8:
                # check mandatory per variable (if elem[vname] is mandatory)
                for i in range(len(self.variables)):
                    file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
                    if not self.get_meta_for_var(i, elem['key']):
                        errstr = ('variable[{}]: mandatory metadata attribute '
                                  "'{}' missing".format(file_vnum, elem['tag']))
                        self.error(errstr, lnum=file_metalnum)
                        if elem['vname'] & 8:
                            self.internal.read_tmp.hea_error = True

    def check_timespec_metadata(self):
        """
        Checks existing timesecific metadata and log errors if needed.
        Parameters:
            None
        Returns:
            None
        Checks:
            type TU/TI (will be corrected in some cases)

        INFO: check startdate/first sample start is done in _check_startdate()
        during parsing of the first data line.
        
        Set type code is not necessarily the same as Nasa Ames DX: Nasa Ames
        x values are float. If the (non 0) DX applies to all x-diffs (last digit
        may be +- 1 due to rounding), the DX is valid. However, in the EBAS
        domain starttimes are datetime (rounded to 0.1s). Here we can have a TI
        series, even if DX in the file is 0.
        Example: 0.000000, 0.041667, 0.083334 0.125000
                 0.083334 is an erroneous reporting
                 (=> 02:00:00.0576 rounded to 02:00:00.1 in the ebas domain)
                 Thus, the series will be TI
                 In Nasa Ames (float) it's just one digit difference in the last
                 digit, which is acceppted to allow for rounding.
        """
        diff = self.uniform_time()
        if diff == datetime.timedelta(0):
            if self.metadata.type != "TI":
                self.warning(
                    'Set type code {} is not consistent with timeseries data, '
                    'setting TI'.format(self.metadata.type))
                self.metadata.type = "TI"
        elif isinstance(diff, datetime.timedelta):
            if self.metadata.type != "TU":
                self.warning(
                    'Set type code {} is not consistent with timeseries data, '
                    'setting TU'.format(self.metadata.type))
                self.metadata.type = "TI"
        # Else (diff is None): Less than 2 samples, type is undefined.
        # We accept whatever value is given.
        # On file read, we don't want to generate error messages for this
        # (e.g. NRT timeseries are definitely TU, but there is always just
        # one sample in the file).

    def _get_file_format(self, ncoml, lnum):
        """
        Read through NasaAmes1001 NCOM block to find the essential metadata
        for classifying the file
            Data definition   mandatory, error when not set
            Data level        optional
        Parameters:
            ncoml    NCOM block as read by Nasa1001 (list of str)
            lnum     line number of NNCOML line (for error reporting)
        Return:
            None
        """
        for i, line in enumerate(ncoml):
            try:
                (tag, value) = self._list_splitter(line, lnum+i+1,
                                                   delimiter=":")
            except ValueError:
                pass
            else:
                if tag == 'Data definition':
                    if value == 'EBAS_1':
                        self.warning('Legacy data definition EBAS_1',
                                     lnum=lnum+i+1)
                    elif value != 'EBAS_1.1':
                        self.error('illegal data definition ' + value,
                                   lnum=lnum+i+1)
                        raise EbasNasaAmesReadError(
                            "{} Errors, {} Warnings".format(self.errors,
                                                            self.warnings))
                    self.metadata.datadef = value
                if tag == 'Data level':
                    conv_dl = {
                        '': None,
                        '2b': '1.5'
                    }
                    if value in conv_dl.keys():
                        self.warning(
                            "converting data level '{}' to '{}'".format(
                                value, conv_dl[value]))
                        value = conv_dl[value]
                    if value is not None:
                        master = EbasMasterDL()
                        try:
                            _ = master[value]
                        except KeyError:
                            self.error(
                                "illegal Data level {} (only {} allowed)"
                                .format(value,
                                        ', '.join([elem['DL_DATA_LEVEL']
                                                   for elem in master])))
                            self.metadata.datalevel = EbasMetadataInvalid(value)
                        else:
                            self.metadata.datalevel = value
        if not self.metadata.datadef:
            self.error('No Data definition specified', lnum=lnum+1)
            raise EbasNasaAmesReadError("{} Errors, {} Warnings".format(
                self.errors, self.warnings))
        # instantiate the ebas metadata object to be used for this fileformat:
        self.internal.ebasmetadata = EbasMetadata(
            self.metadata.datadef, data_format=EBAS_IOFORMAT_NASA_AMES,
            data_level=self.metadata.datalevel)

    def _parse_persons(self, name, lnum):
        """
        Parse person names (generic method for ONAME or SNAME).
        Syntax: "Last Name(s), First Name(s)" or
                "Last Name(s), First Name(s);Last Name(s), First Name(s);..."
        Parameters:
            name   oname/sname line read from file
            lnum   line number (for error reporting)
        Returns:
            List of PS data elements
        """
        labels = ('PS_LAST_NAME', 'PS_FIRST_NAME', 'PS_EMAIL', 'PS_ORG_NAME',
                  'PS_ORG_ACR', 'PS_ORG_UNIT', 'PS_ADDR_LINE1', 'PS_ADDR_LINE2',
                  'PS_ADDR_ZIP', 'PS_ADDR_CITY', 'PS_ADDR_COUNTRY', 'PS_ORCID')
        ret = []
        if name == 'MISSING INFORMATION':
            self.warning('MISSING INFORMATION in person metadata', lnum=lnum)
            return ret
        if self.metadata.datadef == 'EBAS_1':
            for name in self._list_splitter(name, lnum, delimiter=','):
                reg = re.match('^([^ ]+) (.*)$', name.strip())
                if reg:
                    last = reg.group(1).strip()
                    first = reg.group(2).strip()
                    if last == '' and first == '':
                        self.warning("Ignoring empty Person name ('{}')".
                                     format(name), lnum=lnum)
                    else:
                        ret.append(DataObject(
                            dict(zip(labels,
                                     [last if last != u'' else None,
                                      first if first != u'' else None] +
                                     [None] * (len(labels)-2)))))
                else:
                    self.error('Person name syntax error', lnum=lnum)
        else: # default (EBAS_1.1)
            for name in self._list_splitter(name, lnum, delimiter=';'):
                try:
                    (last, first) = self._list_splitter(name.strip(), lnum,
                                                        delimiter=',')
                except ValueError:
                    self.error('Person name syntax error', lnum=lnum)
                else:
                    last = last.strip()
                    first = first.strip()
                    if last == '' and first == '':
                        self.warning("Ignoring empty Person name ('{}')".
                                     format(name), lnum=lnum)
                    else:
                        ret.append(DataObject(
                            dict(zip(labels,
                                     [last if last != u'' else None,
                                      first if first != u'' else None] +
                                     [None] * (len(labels)-2)))))
        if not ret:
            self.error('At least one person must be specified', lnum=lnum)
        return ret

    def _parse_org(self, org): # pylint: disable-msg=R0914
        # R0914 Too many local variables
        """
        Parse ORG line (Organization).
        Syntax:
            "code, name, acronym, unit, addr1, addr2, zip, city, country"
        Example:
            "NO01L, Norwegian Institute for Air Research, NILU,," +\
            "Instituttveien 18,, N-2027, Kjeller, Norway"
        Parameters:
            org   org line read from file (str)
        Returns:
            None
        """
        if self.metadata.datadef == 'EBAS_1':
            reg = re.match('^ *([^ ,]*), (.*)$', org)
            if not reg:
                self.error('Organization syntax error, should be: code, name, '
                           '...', lnum=3)
                return  # stop parsing this line
            (code, name) = reg.groups()
            (acron, unit, addr1, addr2, zip_, city, country) = (None, ) * 7
        else:  # default (EBAS_1.1)
            vals = [elem.strip() if elem.strip() != u'' else None
                    for elem in self._list_splitter(org, 3, delimiter=',')]
            try:
                (code, name, acron, unit, addr1, addr2, zip_, city, country) = \
                    vals
            except ValueError:
                self.error(
                    'Organization syntax error, should be: code, name, '
                    'acronym, unit, addr1, addr2, zip, city, country', lnum=3)
                return  # stop parsing this line
        # check OR_CODE syntax
        try:
            self.internal.ebasmetadata.parse_org_code(code)
        except EbasMetadataError as excpt:
            self.error("Organization code: " + str(excpt), lnum=3)
            return  # stop parsing this line

        reg = re.match(r"^([A-Z][A-Z])(\d\d)([LO])$", code)
        number = int(reg.group(2))
        type_ = reg.group(3)
        self.metadata.org = DataObject(
            OR_CODE=code, OR_TYPE=type_,
            OR_NUMBER=number, OR_NAME=name, OR_ACRONYM=acron, OR_UNIT=unit,
            OR_ADDR_LINE1=addr1, OR_ADDR_LINE2=addr2, OR_ADDR_ZIP=zip_,
            OR_ADDR_CITY=city, OR_ADDR_COUNTRY=country)
        self.logger.debug(u'org={}'.format(self.metadata.org))

    def _parse_projects(self):
        """
        Parse MNAME line and setup project list.
        """
        projstr = self.nasa1001.data.MNAME
        if self.metadata.datadef == 'EBAS_1':
            projstr = re.sub(r'\(insert\)', '', projstr)
        elif re.search(r'\(insert\)', projstr):
            self.warning(
                "Use of '(insert)' for projects is deprecated in EBAS_1.1, "
                "will be ignored", lnum=5)
            projstr = re.sub(r'\(insert\)', '', projstr)
        self.metadata.projects = self._list_splitter(projstr, 5)
        if len(self.metadata.projects) < 1:
            self.error('At least one project must be specified', lnum=5)
        master = EbasMasterPR()
        for proj in self.metadata.projects:
            try:
                master[proj]
            except KeyError:
                self.error("invalid framework acronym '{}'".format(proj),
                           lnum=5)
        self.logger.debug(u'projects={}'.format(self.metadata.projects))

    def _parse_xname(self, xname):
        """
        Parse XNAME line.
        Syntax:
            "days from file reference point" or
            "Days from the file reference point (start_time)"
        Parameters:
            xname   xname line read from file (str)
        Returns:
            None
        """
        if not re.match(\
           r'^(d|D)ays from (the )?file reference point( \(start_time\))?$', \
           xname):
            self.error("XNAME is not supported: '{}'".format(xname), lnum=9)
        self.logger.debug('xname: days from file reference point')

    def _parse_scoml(self, scoml, lnum):
        """
        Parse the complete SCOML block.
        SCOML is completely ignored and skipped currently.
        Parameters:
            scoml   scoml lines read from file (list of str)
            lnum          line number (NSCOML) (for error reporting)
        Returns:
            None
        """
        if len(scoml) > 0:
            self.warning('{} SCOML lines ignored'.format(len(scoml)),
                         lnum=lnum)

    def _parse_ncoml(self, ncoml, lnum):
        """
        Parse the complete NCOML block.
        Parameters:
            ncoml   ncoml lines read from file (list of str)
            lnum          line number (NNCOML) (for error reporting)
        Returns:
            None
        """
        # Component name and Instrument type needs to be pre parsed (needed for
        # any characteristics in NCOM!
        if len(ncoml) == 0:
            self.error('NNCOML: 0 not allowed, NCOM block is mandatory',
                       lnum=lnum)

        pre_read = ('Component', 'Instrument type')
        for i in range(len(ncoml)-1):
            # Last NCOM line should be EBAS TITLE line
            lst = self._list_splitter(ncoml[i], lnum+i+1, delimiter=":")
            if len(lst) == 2:
                # ignore lines which do not have tag: value syntax (error in
                # second loop)
                (tag, value) = self._list_splitter(ncoml[i], lnum+i+1,
                                                   delimiter=":")
                if tag in pre_read:
                    self._parse_ebasmetadata(tag, value, lnum + i + 1)

        for i in range(len(ncoml)):
            # loop through all but last line
            # Last NCOM line should be EBAS TITLE line
            # can only pe parsed after variables have been read
            # see _parse_title_()
            if i == len(ncoml) - 1 and ':' not in ncoml[i]:
                # if last line does not contain a colon: break and parse title
                # this is the normal case for the last nncom line
                break
            # if last line contains a colon: parse metadata first and
            # finally parse for title (raising an error that last line should
            # be title line)
            lst = self._list_splitter(ncoml[i], lnum+i+1, delimiter=":")
            if len(lst) <= 1:
                self.error(
                    'NCOM[{}]: syntax error: not "Tag: value" syntax (no colon '
                    'found which separates the metadata tag from the value)'
                    .format(i+1), lnum=lnum+i+1)
            elif len(lst) > 2:
                self.error(
                    'NCOM[{}]: syntax error: not "Tag: value" syntax (more '
                    'then one colon found which separates the metadata tag '
                    'from the value). Colons in metadata values need to be '
                    'escaped (quote the value with double quotes, e.g. '
                    'Comment: "text with :")'.format(i+1) , lnum=lnum+i+1)
            else:
                (tag, value) = self._list_splitter(ncoml[i], lnum+i+1,
                                                   delimiter=":")
                if tag in ('Data definition', 'Data level') or tag in pre_read:
                    # skip, this has been parsed in _get_file_format
                    # or in the previous loop
                    continue
                self._parse_ebasmetadata(tag, value, lnum + i + 1)

    def _parse_title(self, title, lnum):
        """
        Parse the title line (last NCOML line).
        Parameters:
            title   title line read from file (str)
            lnum    line number (NNCOML) (for error reporting)
        Returns:
            None
        """
        if not re.match(' *start((time)|(_time)|(_DOY)) ', title):
            self.warning(
                u"NCOM: last NCOM line should be title line: '{}'. Title line "
                u"needs to start with 'starttime ', 'start_time ' or "
                u"'start_DOY'".format(title), lnum=lnum)
            return   # stop parsing this line
        titles = self._list_splitter(title, lnum)

        if len(titles) != self.nasa1001.data.NV + 1:
            self.warning(
                u"NCOM: last NCOM line: Number of title elements must be equal "
                u"NV+1 (number of dependent variables specified in line 10) -- "
                u"ignoring titles. Info: NV={}, Number of title elememts={}, "
                u"Titles='{}'".format(self.nasa1001.data.NV, len(titles),
                                      title),
                lnum=lnum)
            return   # stop parsing this line

        if self.internal.read_tmp.hea_error:
            return
            # something critical was wrong with the variable metadata
        for i in range(len(self.variables)):
            self.variables[i].metadata.title = \
                                    titles[self.internal.read_tmp.var_num[i]+1]

    def _parse_data(self, data, lnum):
        """
        Converts the NasaAmes1001 data to EBAS NasaAmes:
        Sets objects's sample_times and variables.
        Parameters:
            data    NasaAmes1001 data array (list of lists, 1 for each variable)
            lnum    line number (of first data line) (for error reporting)
        """
        if not self.msg_condenser.is_reset():
            raise RuntimeError('Uninitialized MessageCondenser')
        self._parse_data_sample_times(data, lnum)
        flag = False
        vnum = 0
        for i in range(1, len(data)-1):
            if i in self.internal.read_tmp.var_skipped:
                # nothing needs to be done with flag. Value and flag variables
                # always need to be skipped at the same time.
                continue
            if flag:
                # data[i+1]: +1 because data includes independent var at [0]
                flags = list(data[i+1])  # make a copy
                dt_decimal = all([True if isinstance(x, Decimal) else False
                                  for x in flags if x is not None])
                if None in flags:
                    errstr = "variable[{}]: ".format(i+1) +\
                             "Missing value for flag column is not allowed."
                    for ln_ in [n for n, x in enumerate(flags)
                                if x is None]:
                        self.msg_condenser.add(
                            self.error, self.msg_condenser.MSG_ID_FLAG_MISSING,
                            i+1, errstr, lnum+ln_)
                    # ignore missing flag and set to 0 for further checks
                    subst = Decimal("0.0") if dt_decimal else 0.0
                    flags = [subst if x is None else x for x in flags]
                # check if value is 0.... and not negative or >= 1.0
                errstr = "variable[{}]: flag value must start with '0.'".format(
                    i+1)
                for ln_ in [n for n, x in enumerate(flags)
                            if x < 0.0 or x >= 1.0]:
                    self.msg_condenser.add(
                        self.error, self.msg_condenser.MSG_ID_FLAG_ZERODOT,
                        i+1, errstr, lnum+ln_)
                # flag conversion:
                #  1) convert all flag variables to Decimal
                #  2) '{:f}'.format() with a decimal prints always all digits
                #     (float does not! - only 6 digits after comma)
                if not dt_decimal:
                    flags = [Decimal(repr(f)) for f in flags]
                self.variables[vnum].flags = \
                    [[int((flagstr[k:k+3]+'00')[:3])
                      for k in range(0, len(flagstr), 3)
                      if int(flagstr[k:k+3]) != 0]
                     # special case: if flag in Nasa was Decimal and the flag
                     # string was '0' or '0.', the Decimal will be Decimal('0')
                     # which crashes ...split('.')[1]
                     for flagstr in ['{:f}'.format(numflag).split('.')[1]
                                     if repr(numflag) != "Decimal('0')"
                                     else "000"
                                     for numflag in flags]]
                # set all previous variables' flags if needed
                for j in reversed(range(vnum)):
                    if self.variables[j].flagcol:
                        break
                    # make a full copy of the flag list (flag correction in
                    # checks might change flags for a single variable):
                    self.variables[j].flags = \
                        [list(x) for x in self.variables[vnum].flags]
                vnum += 1
                flag = False
                # the next column is no flag column, because this was one
            else:
                # data[i+1]: +1 because data includes independent var at [0]
                self.variables[vnum].values_ = data[i+1]
                if self.variables[vnum].flagcol:
                    flag = True
                    # the next column will be a flag column
                else:
                    vnum += 1
        # write all condensed messages and reset condenser object:
        self.msg_condenser.deliver()

    def _parse_data_sample_times(self, data, lnum):
        """
        Sets objects's sample_times from the NasaAmes1001 data.
        Convert columns 0 and 1 to start and endtime, apply starttime and
        timeref, check for time interval overlaps.
        Parameters:
            data    NasaAmes1001 data array (list of lists, 1 for each variable)
            lnum    line number (of first data line) (for error reporting)
        """
        for i in range(len(data[0])):
            # start time is a float (checked already in NasaAmes1001)
            start = self.metadata.reference_date +\
                    self.internal.timeoffset +\
                    datetime.timedelta(days=float(data[0][i]))
            start = datetime_round(start, 1) # round to 1/10 second
            # make sure end time is not missing (this is valid in the
            # NasaAmes1001 file object, but not here in ebas)
            if  data[1][i] is None:
                self.msg_condenser.add(
                    self.error, self.msg_condenser.MSG_ID_TIME_MISSING,
                    None, "Missing value for end time is not allowed.",
                    lnum+i)
                self.internal.read_tmp.hea_error = True
                # strictly, this is not a header error, but needs to be
                # handled the same way (further parsing/checking of the
                # object needs to be skipped)
                end = None
            else:
                end = self.metadata.reference_date +\
                      self.internal.timeoffset +\
                      datetime.timedelta(days=float(data[1][i]))
                end = datetime_round(end, 1) # round to 1/10 second
            try:
                self.sample_times.append(DatetimeInterval(start, end))
            except ValueError:
                self.msg_condenser.add(
                    self.error, self.msg_condenser.MSG_ID_TIME_INVERT,
                    None, "starttime is not < endtime", lnum+i) 

    def _list_splitter(self, string, lnum, **kwargs):
        """
        Splits a string. Double quoted parts are untouched.
        Wrapper for nilutility.string_helper (add error reporting for
        parsing errors).
        Parameters:
            string        string to be splitted
            lnum          line number (for error reporting)
        Returns:
            [part,...] splitted parts as list
        """
        try:
            return list_splitter(string, **kwargs)
        except ListSplitterNewlineError:
            # seems to be an old issue: "newline inside string" seems to be
            # not thrown anymore in revcent versions of the csv module.
            # however on ratatoskr this is currently a problem
            # (status 2016-12-06, ubuntu 12.04, python 2.7.3)
            # this is an issue, we catch the _csv.Error exception in nilutility,
            # throw a ListSplitterNewlineError which is cought here.
            # TODO: may be deleted in th future
            # e.g. ubuntu 16.04, python 2.7.11, this is not an issue
            #      MacOS, python.org 2.7.10 also no issue
            self.error(
                'syntax error: newline inside quoted string constant is not '
                'allowed', lnum=lnum)
            return [string]
        except ListSplitterNullbyteError:
            self.error(
                'syntax error: NULL byte is not allowed', lnum=lnum)
            return [string]

