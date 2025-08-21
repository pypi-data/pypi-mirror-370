"""
ebas/io/base.py
$Id: check_data.py 2773 2022-01-08 02:29:35Z pe $

Base classes for (file) I/O.

"""

import datetime
from nilutility.datetime_helper import datetime_round
from nilutility.list_helper import all_none, all_equal
from ebas.domain.masterdata.bc import EbasMasterBC, \
    EbasMasterBCNoProj, EbasMasterBCDuplicateErrorList
from ebas.domain.basic_domain_logic.flags import check_value_flag_consistency, \
    ISSUE_SEVERITY_ERROR
from ebas.domain.basic_domain_logic.value_check import check_values
from ebas.domain.basic_domain_logic.datalevel import base_datalevel
from ebas.domain.masterdata.pg_pl import EbasMasterPL
from .base import EbasFileBase, isvalid


class EbasFileCheckData(EbasFileBase):  # pylint: disable=W0223
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Partial class for EbasFile (Base class for file objects).
    This part handles checking of the data part.
    """

    def check_data(
        self, ignore_identicalvalues=False,
        ignore_flagconsistency=False, fix_flagconsistency=False,
        ignore_nodata=False, ignore_valuecheck=False,
        fix_overlap_set_start=False, fix_bc211=False):
        """
        Check data consistency and any cause for suspicion in the data.
        Parameter:
            ignore_identicalvalues
                    ignore errors related to all values of one
                    variable being equal (e.g. all data missing for
                    one variable, all values 0.0 or all values any
                    other constant value).
            ignore_flagconsistency
                    ignore errors regarding flag consistency and flag/value
                    consitency
            ignore_nodata
                    the object is expected to not contain any data (ie.g. read
                    with skip_data)
            ignore_valuecheck ignore value checks (boundaries and spikes)
            fix_overlap_set_start
                    instead of raising an error oin case of overlapping samples,
                    the starttime i set to the previous end time
            fix_bc211
                    flag boundary check violations with flag 211
        """
        self._check_sample_times(ignore_nodata, fix_overlap_set_start)
        self._check_value_flag_consistency(
            ignore_flagconsistency, fix_flagconsistency)
        # boundaries and spikes:
        self._check_values(ignore_valuecheck, fix_bc211=fix_bc211)
        self._check_identical_values(ignore_identicalvalues)

    def _check_sample_times(self, ignore_nodata, fix_overlap_set_start):
        """
        Parameters:
            ignore_nodata
                    the object is expected to not contain any data (ie.g. read
                    with skip_data)
            fix_overlap_set_start
                    instead of raising an error oin case of overlapping samples,
                    the starttime i set to the previous end time
        """
        _unused, file_lnum, _ = self.msgref_vnum_lnum(0)
        if not self.msg_condenser.is_reset():
            raise RuntimeError('Uninitialized MessageCondenser')
        for i in range(len(self.sample_times)):
            if i > 0 and (self.sample_times[i-1][1] - \
                          self.sample_times[i][0]).total_seconds() > 0.0:
                if fix_overlap_set_start:
                    self.msg_condenser.add(
                        self.warning, self.msg_condenser.MSG_ID_TIME_OVERLAP,
                        None,
                        "start time {} is not >= previous end time {}, fixing "
                        "start time".format(
                            self.sample_times[i][0], self.sample_times[i-1][1]),
                        file_lnum+i)
                    self.sample_times[i][0] = self.sample_times[i-1][1]
                    for var in self.variables:
                        if 247 not in var.flags[i]:
                            # flag 247: Overlapping sample interval was
                            # corrected by the database co-ordinator. Possible
                            # wrong sample time (used for historic data only)
                            var.flags[i].append(247)
                else:
                    self.msg_condenser.add(
                        self.error, self.msg_condenser.MSG_ID_TIME_OVERLAP,
                        None,
                        "start time {} is not >= previous end time {}".format(
                            self.sample_times[i][0], self.sample_times[i-1][1]),
                        file_lnum+i)
            if not self.sample_times[i][0] < self.sample_times[i][1]:
                self.msg_condenser.add(
                    self.error, self.msg_condenser.MSG_ID_TIME_INVERT,
                    None, "starttime is not < endtime", file_lnum+i)
        # write all condensed messages and reset condenser object:
        self.msg_condenser.deliver()

        # check first starttime is equal metadata elemen Startdate
        self._check_startdate(ignore_nodata, file_lnum)

        # check last endtime is not in the future.
        # This is only true for observed data (not for model data).
        # Needs reconsideration when we accept regimes other than IMG
        now = datetime.datetime.utcnow()
        if self.sample_times and \
           self.sample_times[-1][1] is not None and \
           self.sample_times[-1][1] >= now:
            self.error(
                "No future data allowed. Last sample endtime is '{}'.".\
                format(self.sample_times[-1][1].strftime("%Y%m%d%H%M%S")))

        if not self.sample_times and not ignore_nodata:
            # reason to report an error when a file contains no (valid) data:
            # revdate and period code can not be checked, which means the header
            # cannot be validated without data, thus a file without data cannot
            # be valid
            self.error('File contains no data')

    def _check_startdate(self, ignore_nodata, lnum):
        """
        Check the metadata elemet startdate against first sample start.
        Parameters:
            firststart   starttime of first sample
            lnum         line number (of first data line) (for error reporting)
        Returns:
            None
        """
        if not self.metadata.startdate:
            self.error("No start date set in metadata")
        if not ignore_nodata and (\
                not self.sample_times or not self.sample_times[0] or \
                not self.sample_times[0][0]):
            # report error only if not ignore_nodata
            self.error(
                "No samples in file, cannot check metadata start date",
                lnum=lnum)

        if not self.metadata.startdate or not  self.sample_times or \
                not self.sample_times[0] or not self.sample_times[0][0]:
            return

        firststart = self.sample_times[0][0]
        if self.metadata.datadef == 'EBAS_1' and \
           self.metadata.startdate.time() == datetime.time(0, 0):
            # EBAS_1 and startdate is only specified with date precision, only
            # check for same day.
            if self.metadata.startdate.date() != firststart.date():
                self.error(
                    "start day of first sample ({}) is not equal to "
                    "'Startdate' specified in metadata ({})".format(
                        firststart.strftime('%Y-%m-%d'),
                        self.metadata.startdate.strftime('%Y-%m-%d')),
                    lnum=lnum)

        elif abs((firststart-self.metadata.startdate).total_seconds()) >= 1800:
            # difference >= 30 minutes
            self.error(
                "start time of first sample ({}) is not equal to 'Startdate' "
                "specified in metadata ({})".format(
                    datetime_round(firststart, 0).strftime('%Y-%m-%dT%H:%M:%S'),
                    self.metadata.startdate.strftime('%Y-%m-%dT%H:%M:%S')),
                lnum=lnum)
        elif abs((firststart-self.metadata.startdate).total_seconds()) >= 0.5:
            # difference >= 0.5 sec
            self.warning(
                "start time of first sample ({}) is not equal to 'Startdate' "
                "specified in metadata ({})".format(
                    datetime_round(firststart, 0).strftime('%Y-%m-%dT%H:%M:%S'),
                    self.metadata.startdate.strftime('%Y-%m-%dT%H:%M:%S')),
                lnum=lnum)

    def _check_value_flag_consistency(self, ignore_flagconsistency,
                                      fix_flagconsistency):
        """
        Check valididy of flags, consistency of flags and flag/value
        combinations.
        Parameters:
            ignore_flagconsistency
                    ignore errors regarding flag consistency and flag/value
                    consitency
        Returns:
            None
        """
        if not self.msg_condenser.is_reset():
            raise RuntimeError('Uninitialized MessageCondenser')
        for vnum in range(len(self.variables)):  # pylint: disable=C0200
            # C0200: Consider using enumerate instead of iterating with
            # range/len
            # --> only using index
            file_vnum, file_lnum, _ = self.msgref_vnum_lnum(vnum)

            # Make sure the message condenser is fresh
            if not self.msg_condenser.is_reset():
                raise RuntimeError('Uninitialized MessageCondenser')

            # check all flags/values consistency
            special = 0
            if self.is_precip_amount(vnum):
                special = 1
            if self.is_auxiliary(vnum):
                special = 2
            for issue in check_value_flag_consistency(
                    self.variables[vnum].values_,
                    self.variables[vnum].flags,
                    special, ignore_flagconsistency, fix_flagconsistency):
                self.msg_condenser.add(
                    self.error if issue['severity'] == ISSUE_SEVERITY_ERROR
                    else self.warning,
                    issue['msg_id'], file_vnum,
                    "variable[{}]: ".format(file_vnum) + issue['message'],
                    file_lnum + issue['row'])
            # write all condensed messages and reset condenser object:
            self.msg_condenser.deliver()

    def _check_identical_values(self, ignore_identicalvalues):
        """
        Check for all identical values (including all zero and all None).
        Parameter:
            ignore_identicalvalues
                    ignore errors related to all values of one
                    variable being equal (e.g. all data missing for
                    one variable, all values 0.0 or all values any
                    other constant value).
        """
        if len(self.sample_times) > 10:
            # Do not check if it's too little values.
            # There are also some exceptions in _identical_values_exception_mask
            # depending on number of samples or sample period.
            for vnum in range(len(self.variables)):
                exceptions = self._identical_values_exception_mask(vnum)
                file_vnum, _, _ = self.msgref_vnum_lnum(vnum)

                # some sanity checks:
                messagefunc = \
                    self.warning if ignore_identicalvalues else self.error
                if all_none(self.variables[vnum].values_):
                    if not exceptions & \
                            self.__class__.CHECK_EXCEPTION_ALLNONE_SILENT:
                        # only raise any message if not _SILENT, else skip
                        # message alltogether
                        if exceptions & self.__class__.CHECK_EXCEPTION_ALLNONE:
                            messagefunc = self.warning
                        messagefunc(
                            "variable[{}]: All values are MISSING. Check data "
                            "sanity.".format(file_vnum))
                elif all_equal(self.variables[vnum].values_, ignore_none=True):
                    # get first none None value:
                    value = next((x for x in self.variables[vnum].values_
                                  if x is not None))
                    message = ("variable[{}]: All valid values are {}. Check "
                               "data sanity.").format(file_vnum, value)
                    dl_ = self.get_meta_for_var(vnum, "detection_limit")
                    if value == 0.0:
                        if not exceptions & \
                                self.__class__.CHECK_EXCEPTION_ALLZERO_SILENT:
                            # only raise any message if not _SILENT, else skip
                            # message alltogether
                            if exceptions & \
                                    self.__class__.CHECK_EXCEPTION_ALLZERO:
                                messagefunc = self.warning
                            messagefunc(message)
                    else:
                        if not exceptions & \
                                self.__class__.CHECK_EXCEPTION_ALLEQUAL_SILENT:
                            # only raise any message if not _SILENT, else skip
                            # message alltogether
                            if exceptions & \
                                    self.__class__.CHECK_EXCEPTION_ALLEQUAL:
                                messagefunc = self.warning
                            # exception for BDL values: if only BDL values and
                            # all are set to BDL, this error needs to be
                            # downgraded to a warning:
                            if all([781 in self.variables[vnum].flags[i]
                                    for i in range( \
                                        len(self.variables[vnum].values_))
                                    if self.variables[vnum].values_[i] \
                                        is not None]):
                                message = (
                                    "variable[{}]: All valid values are {} (below "
                                    "detection limit, flagged 781)").format(
                                        file_vnum, value)
                                messagefunc = self.warning
                            messagefunc(message)

    CHECK_EXCEPTION_ALLEQUAL = 1  # allow equal, but not zero or None
    CHECK_EXCEPTION_ALLEQUAL_SILENT = 2  # addtn'lly, be silent in this case
    CHECK_EXCEPTION_ALLZERO = 4  # special case of identilcalvalues, needed
    CHECK_EXCEPTION_ALLZERO_SILENT = 8  # # addtn'lly, be silent in this case
    CHECK_EXCEPTION_ALLNONE = 16
    CHECK_EXCEPTION_ALLNONE_SILENT = 32 # addtn'lly, be silent in this case
    # often used sums:
    CHECK_EXCEPTION_ALLIDENTICAL = CHECK_EXCEPTION_ALLEQUAL | \
        CHECK_EXCEPTION_ALLZERO | CHECK_EXCEPTION_ALLNONE
        # allow equal, zero or None
    CHECK_EXCEPTION_ALLIDENTICAL_SILENT =  CHECK_EXCEPTION_ALLEQUAL_SILENT | \
        CHECK_EXCEPTION_ALLZERO_SILENT | CHECK_EXCEPTION_ALLNONE_SILENT
        # addtn'lly, be silent in this case

    def _identical_values_exception_mask(self, vnum):
        """
        Get possible exceptions for checking the variable.
        Parameters:
            vnum              variable index
            exception_mask    bitmask of exceptions to be checked
        """
        exceptions = 0
        instr_type = self.get_meta_for_var(vnum, "instr_type")
        regime = self.get_meta_for_var(vnum, "regime")
        matrix = self.get_meta_for_var(vnum, "matrix")
        comp_name = self.get_meta_for_var(vnum, "comp_name")
        data_level = base_datalevel(self.get_meta_for_var(vnum, 'datalevel'))
        charact = self.get_characteristics_for_var(vnum)
        statistics = self.get_meta_for_var(vnum, "statistics")

        # General exceptions
        if comp_name == 'status':
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
        if 'Actual/target' in charact and charact['Actual/target'] == 'target':
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
        if ('Nominal/measured' in charact and
            charact['Nominal/measured'] in ('nominal',
                                            'Calibration gas concentration')):
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLEQUAL_SILENT
        if 'Assumption' in charact and charact['Assumption']:
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
        if 'Actual/target' in charact and charact['Actual/target'] == 'target':
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL

        if comp_name == 'particle_number_size_distribution':
            # ops, size > 400 nm: ignore 0 values (the bigger sizes the more
            # oftern there are in fact no particles detected for a whole year.
            # depends on the station setting (Troll 400 nm, Greece 16000)
            # aps depends on station (e.g. KR0100R 19000 nm)
            # We make an exception for the upper 30% of sizes
            all_sizes = set()
            for i, var in enumerate(self.variables):
                if (var.metadata.comp_name ==
                    'particle_number_size_distribution'):
                    charact1 = self.get_characteristics_for_var(i)
                    if 'D' in charact1:
                        all_sizes.add(charact1['D'])
            if len(all_sizes) > 2:
                threshold = sorted(all_sizes)[int(2*len(all_sizes)/3)]
                if 'D' in charact and charact['D'] >= threshold:
                    exceptions |= self.__class__.CHECK_EXCEPTION_ALLZERO
            # MPSS, smallest size bin, lower percentile, allow all 0
            if (statistics == 'percentile:15.87' and
                'D' in charact and charact['D'] == sorted(all_sizes)[0]):
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLZERO
        if instr_type == 'TEOM' and \
           comp_name == 'temperature':
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
        if data_level == '0' and  instr_type in ('dmps', 'smps'):
            if comp_name in ('status', 'temperature', 'flow_rate',
                             'particle_diameter'):
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
            if comp_name == 'particle_number_concentration' and \
               'Size bin' in charact and charact['Size bin'] > 25:
                # ther might be no "big" particles all year...
                # however we define big here in level 0 (let's say 25th bin)
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLZERO
        if instr_type == 'aerosol_mass_spectrometer':
            if (data_level == '0' and
                comp_name in ('pressure', 'temperature', 'relative_humidity',
                              'flow_rate','status',
                              'frequency', 'electric_power',
                              'electric_tension', 'electric_current',
                              'airbeam_signal', 
                              'nitrogen_ion_flow_signal',
                              'ionization_efficiency',
                              'relative_ionization_efficiency',
                              'collection_efficiency')):
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
            if comp_name == 'ammonium':
                # 2023-11-16: There is an issue with ammonium for ToF ACSM
                # baseline below 0, so data submitters flag out all ammonium
                # in lev0, which means all missing in lev2.
                # We accept this, or we would not get any data...
                # TODO: this is only temporary, as long as the underlying
                # problem is not fixed
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLNONE
        if instr_type == 'filter_absorption_photometer' and \
           comp_name in ('flow_rate', 'bypass_fraction'):
            # the bypass fraction is usually set and left constant for all
            # measurements (it's instrument configuration, really)
            # Therefore, silence this issue completely (not even a warning)
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL_SILENT
        if instr_type == 'filter_absorption_photometer' and \
           data_level == '0':
            if comp_name in ('status', 'temperature', 'pressure'):
                # AE33 temp and pressure is a reference value (for volume
                # standard) and NOT measured, thus it can be constant.
                # TODO: change AE33 template, use Assumption=reference pressure
                # Some of the status variables may be constant over a year...
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
            if comp_name == 'filter_loading_compensation_parameter' and \
                    (self.sample_times[-1][1]-self.sample_times[0][0]).\
                    total_seconds() <= 3600*24*10:
                # AE33 filter_loading_compensation_parameter may be constant
                # over some time time?
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
            if comp_name == 'filter_number' and \
                    (self.sample_times[-1][1]-self.sample_times[0][0]).\
                    total_seconds() <= 3600*24*30*3:
                # AE33 filter_number may be constant over 3 month
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLIDENTICAL
        if instr_type == 'filter_absorption_photometer' and \
           data_level == '0' and  \
           comp_name in ('relative_humidity', ):
            # AE42 no temp, pressure and humidity, but using template for AE31
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLNONE

        if [1 for x in EbasMasterPL().list_groups(regime, matrix, comp_name)
                if x.startswith("VOC-") or x.startswith("voc_")]:
            # VOCs: precision and expanded uncertainty 2 sigma may turn out
            # constant if all measurements very low and around DL
            if statistics in ('precision', 'expanded uncertainty 2sigma'):
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLEQUAL

        if [1 for x in EbasMasterPL().list_groups(regime, matrix, comp_name)
                if x == 'pollen']:
            # Pollen data: certain species can be 0 for long periods, maybe
            # always. This can be valueable information.
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLZERO

        if instr_type == 'online_gc' and data_level == '0':
            # all components may be missing (not measured)
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLNONE_SILENT
            if comp_name.endswith('_retention_time'):
                exceptions |= self.__class__.CHECK_EXCEPTION_ALLEQUAL
        if instr_type == 'online_gc' and data_level == '1':
            # all components may be missing (not measured)
            exceptions |= self.__class__.CHECK_EXCEPTION_ALLNONE_SILENT
        return exceptions

    def _check_values(self, ignore_valuecheck, fix_bc211=False):
        """
        Checks boundaries and spikes in the data of an EBAS NasaAmes Object.
        Parameters:
            ignore_valuecheck ignore value checks (boundaries and spikes)
            fix_bc211         flag boundary check violations with flag 211
        Returns:
            None
        """
        ebc = EbasMasterBC()
        trans_meta = [
            ('regime', 'RE_REGIME_CODE', 'Regime code'),
            ('matrix', 'MA_MATRIX_NAME', 'Matrix name'),
            ('comp_name', 'CO_COMP_NAME', 'Component name'),
            ('projects', 'PR_ACRONYM', 'Frameworks'),
            ('station_code', 'ST_STATION_CODE', 'Station code'),
            ('instr_type', 'FT_TYPE', 'Intrument type'),
            # ('datalevel', 'DL_DATA_LEVEL', 'Data level'),
            # Datalevel is not mandatory, we don't want to raise an error
            # if it is missing in the file!
            # Datalevel is handled separately below
            ('statistics', 'SC_STATISTIC_CODE', 'Statistics')]
        for vnum in range(len(self.variables)):  # pylint: disable=C0200
            # C0200: Consider using enumerate instead of iterating with
            # range/len
            # --> only using index
            undef = []
            search = {}
            file_vnum, file_lnum, _ = self.msgref_vnum_lnum(vnum)

            # translate metadata
            for elem in trans_meta:
                val = self.get_meta_for_var(vnum, elem[0])
                if not isvalid(val):
                    undef.append(elem[2])
                else:
                    search[elem[1]] = val

            # special case for datalevel: no error message when not set
            val = self.get_meta_for_var(vnum, 'datalevel')
            if isvalid(val):
                search['DL_DATA_LEVEL'] = val
            else:
                search['DL_DATA_LEVEL'] = None

            # special case for fi_ref:
            lab_code = self.get_meta_for_var(vnum, 'lab_code')
            instr_name = self.get_meta_for_var(vnum, 'instr_name')
            if not isvalid(lab_code):
                undef.append('Laboratory code')
            if not isvalid(instr_name):
                undef.append('Instrument name')
            if isvalid(lab_code) and isvalid(instr_name):
                search['FI_REF'] = lab_code + '_' + instr_name

            # any undefied metadata?
            if undef:
                self.error(
                    "variable[{}]: No applicable boundary check found because "
                    "some metadata are not specified correctly ({})".format(
                        file_vnum, ', '.join(undef)),
                    None)
                continue

            # characteristics:
            search['characteristics'] = self.get_characteristics_for_var(vnum)

            try:
                bc_list = ebc.select(search)
            except EbasMasterBCNoProj as excpt:
                self.error(
                    "variable[{}]: {}; boundary and spike checks skipped"
                    .format(file_vnum, excpt), None)
                bc_list = []
            except EbasMasterBCDuplicateErrorList as excpt:
                for err in excpt.errlist:
                    self.error(
                        "variable[{}]: {}; some boundary and spike checks "
                        "skipped".format(file_vnum, err), None)
                bc_list = excpt.retlist
            if not bc_list:
                self.warning(
                    "variable[{}]: No applicable boundary check found".format(
                        file_vnum), None)
            else:
                # check all rules:
                for rule in bc_list:
                    # Make sure the message condenser is fresh
                    if not self.msg_condenser.is_reset():
                        raise RuntimeError('Uninitialized MessageCondenser')
                    # check all values for variable vnum, filter by flags!
                    issues = check_values(
                        rule.PR_ACRONYM,
                        self.variables[vnum].values_,
                        self.variables[vnum].flags,
                        rule.BC_MINVAL, rule.BC_MAXVAL,
                        rule.BC_SPIKE_RADIUS,
                        rule.BC_SPIKE_MINOFFSET, rule.BC_SPIKE_MAXOFFSET,
                        rule.BC_SPIKE_MINSTDDEVFACT,
                        rule.BC_SPIKE_MAXSTDDEVFACT,
                        fix_bc211=fix_bc211)
                    for issue in issues:
                        self.msg_condenser.add(
                            self.error if not ignore_valuecheck and \
                                issue['severity'] == ISSUE_SEVERITY_ERROR \
                                else self.warning,
                            issue['msg_id'], file_vnum,
                            "variable[{}]: {}".format(file_vnum,
                                                      issue['message']),
                            file_lnum + issue['row'])
                    # write all condensed messages and reset condenser object:
                    self.msg_condenser.deliver()
