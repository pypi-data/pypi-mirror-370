"""
ebas/io/base.py
$Id: check_metadata.py 2503 2020-10-14 16:59:06Z pe $

Base classes for (file) I/O.

TODO: fuctionality which should be implemented in check_metadata is mixed into
ebasmetadata (parsing/checking is _not_ separated). This means that those checks
are only performed for files read, but not for file objects constructed for
writiting.
"""

from .base import EbasFileBase, EbasMetadataInvalid, isvalid
import datetime
from nilutility.list_helper import all_none, all_equal
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
    estimate_resolution_code, estimate_sample_duration_code, \
    period_code_seconds
from ebas.domain.masterdata.am import EbasMasterAM
from ebas.domain.masterdata.ax import EbasMasterAX
from ebas.domain.masterdata.ca import EbasMasterCA
from ebas.domain.masterdata.co import EbasMasterCO
from ebas.domain.masterdata.fm import EbasMasterFM
from ebas.domain.masterdata.pm import EbasMasterPM
from ebas.domain.masterdata.qm_qv import EbasMasterQM, EbasMasterQV
from ebas.domain.masterdata.ip import EbasMasterIP
from ebas.domain.masterdata.se import EbasMasterSE
from ebas.domain.masterdata.sm import EbasMasterSM
from ebas.domain.masterdata.pr import EbasMasterPR


class EbasFileCheckMetadata(EbasFileBase):  # pylint: disable=W0223
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Partial class for EbasFile (Base class for file objects).
    This part handles checking of the metadata.
    """

    def check_metadata(self, ignore_rescode=False, ignore_revdate=False,
                       ignore_parameter=False, ignore_sampleduration=False):
        """
        Performs a check of the metadata of the object.
        Parameter:
            ignore_rescode    ignore rescde errors (downgraded to warning)
            ignore revdate    ignore revdate errors (downgrade to warning)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
        TODO: currently, most of the metadata syntax check is done during
        parsing, this checks are not available here. This should be fixed...
        """
        self.harmonize_persons()
        self.check_interdependent_metadata(
            ignore_rescode=ignore_rescode, ignore_revdate=ignore_revdate,
            ignore_parameter=ignore_parameter,
            ignore_sampleduration=ignore_sampleduration)

    def harmonize_persons(self):
        """
        Harmonize additional metadata in Originator and Submitter if both are
        the same persons.
        Ref: http://jira.nilu.no/browse/EWB-432

        Parmaters:
            None
        Returns:
            None
        """
        passes = (('originator', 'submitter'), ('submitter', 'originator'))
        for cur in passes:
            for pers in self.metadata[cur[0]]:
                if set([key for key in pers.keys()
                        if pers[key] is not None]) == \
                   set(['PS_LAST_NAME', 'PS_FIRST_NAME']):
                    # person has honly first and last name, look for same person
                    # in the other category:
                    res = [x for x in self.metadata[cur[1]]
                           if x.PS_LAST_NAME == pers.PS_LAST_NAME and
                           x.PS_FIRST_NAME == pers.PS_FIRST_NAME]
                    if res and \
                       set([key for key in res[0].keys()
                            if res[0][key] is not None]) != \
                       set(['PS_LAST_NAME', 'PS_FIRST_NAME']):
                        pers.update(res[0])
                        self.warning(
                            '{} {}, {}: no additional metadata '
                            'specified; using metadata from the {} with the '
                            'same name.'
                            .format(cur[0].capitalize(), pers.PS_LAST_NAME,
                                    pers.PS_FIRST_NAME, cur[1]))

    def check_interdependent_metadata(
            self, ignore_rescode=False, ignore_revdate=False,
            ignore_parameter=False, ignore_sampleduration=False):
        """
        Checks metadata consistency within the file.
        Parameters:
            ignore_rescode    ignore inconsistencies in rescode (downgrade error
                              to warning)
            ignore_revdate    ignore inconsistencies in revdate (downgrade error
                              to warning)
            ignore_paramter   ignore illegal parameters
        Returns:
            None
        """
        self._check_interdep_license()
        self._check_interdep_station()
        self._check_interdep_periodcode()
        self._check_interdep_rescode(ignore_rescode=ignore_rescode)
        self._check_interdep_durationcode(
            ignore_sampleduration=ignore_sampleduration)
        self._check_interdep_revdate(ignore_revdate=ignore_revdate)
        self._check_interdep_qa()
        self._check_interdep_uncertainty()
        self._check_interdep_detectionlimit()
        self._check_interdep_upperrangelimit()
        self._check_interdep_instrument()
        self._check_interdep_inlet()
        self._check_interdep_analytical()
        self._check_interdep_sensortype()
        self._check_interdep_absorption_crosssection()
        self._check_interdep_calibrationscale()
        self._check_interdep_stdmethod()
        self._check_interdep_parameter(ignore_parameter=ignore_parameter)

        orig_filename = self.metadata.filename
        self.gen_filename()
        if self.metadata.filename != orig_filename:
            self.warning("File name: changed from '{}' to '{}'".format(
                orig_filename, self.metadata.filename))

    def _check_interdep_license(self):
        """
        Checks project and license consistency.
        Parameters:
            None
        Returns:
            None
        """
        master = EbasMasterPR()
        if not isvalid(self.metadata.license):
            # no need to check
            return
        if isvalid(self.metadata.projects):
            is_open = False
            check_closed = True
            for proj in self.metadata.projects:
                try:
                    pr_elem = master[proj]
                except KeyError:
                    # error is written alreadt in ansa_ames.parse...
                    # but if we have an illegal project, we will not check on
                    # closed projects...
                    check_closed = False
                if pr_elem['OPEN_ACCESS']:
                    is_open = True
                    break
            if is_open and self.metadata.license != \
                    'https://creativecommons.org/licenses/by/4.0/':
                self.error("Wrong license for open data: '{}'".format(
                    self.metadata.license))
            if not is_open and check_closed:
                self.error("Wrong license for restricted data: '{}'".format(
                    self.metadata.license))

    def _check_interdep_station(self):
        """
        Checks Station and Platform consistency.
        Parameters:
            None
        Returns:
            None
        """
        if isvalid(self.metadata.station_code) and \
           isvalid(self.metadata.platform_code) and \
           not self.metadata.platform_code.startswith(\
               self.metadata.station_code[0:6]):
            self.error('Station Code and Platform code must match in the first '
                       '6 characters')
        # station is (still?) file global, no need to check for each variable

    def _check_interdep_periodcode(self):
        """
        Check consistency of period code.
        Parameters:
            None
        Returns:
            None
        """
        if isvalid(self.metadata.period) and len(self.sample_times) > 0 and \
           self.sample_times[0][0] is not None and self.sample_times[-1][1]:
            # periode code can not be checked, if there are no data
            # (len(sample_times) == 0): make sure files without data report an
            # error anyway (see read())
            period = estimate_period_code(self.sample_times[0][0],
                                          self.sample_times[-1][1])
            if self.metadata.period != period:
                self.warning("Period code '{}' should be '{}' according to "
                             "data".format(self.metadata.period, period))
        # period code is (by definition) file global, no need to check for each
        # variable

    def _check_interdep_rescode(self, ignore_rescode=False):
        """
        Check consistency of resolution code. Check against the median of all
        start time differences in data.
        Parameters:
            ignore_rescode    ignore inconsistencies in rescode (downgrade error
                              to warning)
        Returns:
            None
        """
        if isvalid(self.metadata.resolution) and len(self.sample_times) > 1:
            res_cde = estimate_resolution_code(self.sample_times)
            res_sec = period_code_seconds(res_cde)
            if not ignore_rescode and \
               self.metadata.resolution != res_cde and \
               abs(period_code_seconds(self.metadata.resolution) - \
                   res_sec) > res_sec * 0.25:
                # > 25% off: ERROR
                self.error("Resolution code '{}' should be '{}' according "
                           "to data".format(self.metadata.resolution,
                                            res_cde))
            elif self.metadata.resolution != res_cde and \
               abs(period_code_seconds(self.metadata.resolution) - \
                   res_sec) > res_sec * 0.1:
                # > 10% off: WARNING
                self.warning("Resolution code '{}' should be '{}' "
                             "according to data"\
                             .format(self.metadata.resolution, res_cde))
        # resolution code is (by definition) file global, no need to check for
        # each variable

    def _check_interdep_durationcode(self, ignore_sampleduration=False):
        """
        Check consistency of duration code. Check against the median of all
        sample durations in the data.
        Parameters:
            None
        Returns:
            None
        """
        if isvalid(self.metadata.duration) and len(self.sample_times) > 0:
            # check sample duration against median duration in data
            dur_cde = estimate_sample_duration_code(self.sample_times)
            if dur_cde:
                if self.metadata.duration == dur_cde:
                    return
                dur_sec = period_code_seconds(dur_cde)
                diff = abs(period_code_seconds(self.metadata.duration) -
                           dur_sec)
                if ignore_sampleduration and diff > dur_sec * 0.25:
                    # > 20% off: ERROR
                    self.warning("Sample duration '{}' should be '{}' according "
                               "to data".format(self.metadata.duration,
                                                dur_cde))
                elif diff > dur_sec * 0.25:
                    # > 20% off: ERROR
                    self.error("Sample duration '{}' should be '{}' according "
                               "to data".format(self.metadata.duration,
                                                dur_cde))
                elif diff > dur_sec * 0.1:
                    # > 10% off: WARNING
                    self.warning("Sample duration '{}' should be '{}' "
                                 "according to data"\
                                 .format(self.metadata.duration, dur_cde))
            else:
                self.error(
                    "Sample duration could not be checked because of errors in "
                    "start/end times (see previous error messages)")
        # duration code is (by definition) file global, no need to check for
        # each variable

    def _check_interdep_revdate(self, ignore_revdate=False):
        """
        Check consistency of revision date.
        Parameters:
            ignore_revdate    ignore inconsistencies in revdate (downgrade error
                              to warning)
        Returns:
            None
        """
        if not isvalid(self.metadata.revdate):
            return

        now = datetime.datetime.utcnow()
        # check reported revision date against last sample end time
        if len(self.sample_times) > 0 and \
           self.sample_times[-1][1] is not None and \
           self.metadata.revdate < self.sample_times[-1][1]:
            # revision date can not be checked, if there are no data
            # (len(sample_times) == 0): make sure files without data report an
            # error anyway (see read())

            # check rev date > last sample
            # This is only true for observed data (not for model data).
            # Needs reconsideration when we accept regimes other than IMG
            if ignore_revdate:
                self.warning(
                    'Revision date ({}) should not be earlier than last sample '
                    'endtime ({})'.format(
                        self.metadata['revdate'].strftime("%Y%m%d%H%M%S"),
                        self.sample_times[-1][1].strftime("%Y%m%d%H%M%S")))
            else:
                self.error(
                    'Revision date ({}) must not be earlier than last sample '
                    'endtime ({})'.format(
                        self.metadata['revdate'].strftime("%Y%m%d%H%M%S"),
                        self.sample_times[-1][1].strftime("%Y%m%d%H%M%S")))
        if self.metadata.revdate >= now:
            self.error('Revision date ({}) must not be in the future'.\
                       format(self.metadata.revdate.strftime("%Y%m%d%H%M%S")))

        # check for all variables:
        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            if 'revdate' in self.variables[i].metadata:
                if len(self.sample_times) > 0 and \
                   self.sample_times[-1][1] is not None and \
                   self.variables[i].metadata['revdate'] < \
                   self.sample_times[-1][1]:
                    # revision date can not be checked, if there are no data
                    # (len(sample_times) == 0): make sure files without data
                    # report an error anyway (see read())

                    # check rev date > last sample
                    # This is only true for observed data (not for model data).
                    # Needs reconsideration when we accept regimes other than
                    # IMG
                    self.error(
                        'Variable {}: Revision date ({}) must not be earlier '
                        'than last sample endtime ({})'.\
                        format(
                            file_vnum,
                            self.variables[i].metadata['revdate'].strftime(
                                "%Y%m%d%H%M%S"),
                            self.sample_times[-1][1].strftime("%Y%m%d%H%M%S")),
                        lnum=file_metalnum)
                if self.variables[i].metadata['revdate'] > \
                   self.metadata['revdate']:
                    # check variable specific revdate is not greater than
                    # revdate:
                    self.error(
                        'Variable {}: Revision date specified for variable '
                        '({}) must not be later than globally set Revision '
                        'date ({})'.\
                        format(
                            file_vnum,
                            self.variables[i].metadata['revdate'].strftime(
                                "%Y%m%d%H%M%S"),
                            self.metadata.revdate.strftime("%Y%m%d%H%M%S")),
                        lnum=file_metalnum)
                if self.variables[i].metadata['revdate'] >= now:
                    self.error(
                        'Variable {}: Revision date ({}) must '
                        'not be in the future'.format(
                            file_vnum,
                            self.variables[i].metadata['revdate'].strftime(
                                "%Y%m%d%H%M%S")),
                        lnum=file_metalnum)

    def _check_interdep_qa(self):
        """
        Check consistency of QA metadata
        Parameters:
            None
        Returns:
            None
        """
        qv_ = EbasMasterQV()
        qm_ = EbasMasterQM()
        for qanum in self.get_qa_numbers():
            qanum_txt = qanum if qanum != -1 else ""
            main_qa = self.get_qa_by_number(qanum, None)
            if main_qa is None:
                main_qa = {}
            main_ft_type = self.metadata.instr_type
            # only use main component name if it is a "real" component, and
            # not just an arbitrary name:
            if self._is_real_comp(self.metadata.comp_name):
                main_comp_name = self.metadata.comp_name
            else:
                main_comp_name = None
            # check global metadata:
            if isvalid(main_qa['qm_id']):
                if not qm_.new_reference_calibration(main_qa['qm_id']):
                    # check QV validity:
                    if isvalid(main_ft_type) and \
                       isvalid(main_comp_name):
                        try:
                            # QV masterdata lookup with additional data level:
                            # if QV is not defined in DB masterdata, lookup in
                            # exceptional masterdata (data level dependent,
                            # not meant to be imported)
                            qv_[(main_qa['qm_id'], main_ft_type,
                                 main_comp_name, self.metadata.datalevel)]
                        except KeyError:
                            self.error(
                                "QA{} measure ID/Instrument type/Component "
                                "combination '{}'/'{}'/'{}' is not defined"
                                .format(qanum_txt, main_qa['qm_id'], main_ft_type,
                                        main_comp_name))

                    qm_dict = qm_[main_qa['qm_id']]
                    # check QA date is within QM date start and date end:
                    if (qm_dict.QM_START and isvalid(main_qa['qa_date']) and \
                        main_qa['qa_date'] < qm_dict.QM_START) or \
                       (qm_dict.QM_END and isvalid(main_qa['qa_date']) and \
                        main_qa['qa_date'] > qm_dict.QM_END):
                        if qm_dict.QM_START and qm_dict.QM_END:
                            self.error(
                                "QA{} date must be between {} and {}".format(
                                    qanum_txt, qm_dict.QM_START, qm_dict.QM_END))
                        elif qm_dict.QM_START:
                            self.error(
                                "QA{} date must be at or after {}".format(
                                    qanum_txt, qm_dict.QM_START))
                        else:
                            self.error(
                                "QA{} date must be at or before {}".format(
                                    qanum_txt, qm_dict.QM_END))
                    # check QA document metadata are consistent with QM:
                    if qm_dict.QM_DOCUMENT_TITLE and main_qa['qa_doc_name'] and \
                       qm_dict.QM_DOCUMENT_TITLE != main_qa['qa_doc_name']:
                        self.error(
                            "QA{} document name must be'{}'".format(
                                qanum_txt, qm_dict.QM_DOCUMENT_TITLE))
                    if qm_dict.QM_DOCUMENT_DATE and main_qa['qa_doc_date'] and \
                       qm_dict.QM_DOCUMENT_DATE != main_qa['qa_doc_date']:
                        date_txt = qm_dict.QM_DOCUMENT_DATE.strftime("%Y%m%d") \
                            if qm_dict.QM_DOCUMENT_DATE.time() == \
                                datetime.time(0, 0) \
                            else qm_dict.QM_DOCUMENT_DATE.strftime(
                                "%Y%m%d$H%M%S")
                        self.error(
                            "QA{} document date must be '{}'".format(
                                qanum_txt, date_txt))
                    if qm_dict.QM_DOCUMENT_URL and main_qa['qa_doc_url'] and \
                       qm_dict.QM_DOCUMENT_URL != main_qa['qa_doc_url']:
                        self.error(
                            "QA{} document name must be '{}'".format(
                                qanum_txt, qm_dict.QM_DOCUMENT_URL))
                    # check qa bias unit: must be consistent within NNCOM
                    if isvalid(main_qa['qa_bias']) and \
                       main_qa['qa_bias'][1] != '%' and \
                       self.metadata.unit != main_qa['qa_bias'][1]:
                        self.error("Unit '{}' used for 'QA{} bias' is "
                            "inconsistent with 'Unit' ({})".format(
                                main_qa['qa_bias'][1], qanum_txt,
                                self.metadata.unit))
                    # check qa variability unit: must be consistent within NNCOM
                    if isvalid(main_qa['qa_variability']) and \
                       main_qa['qa_variability'][1] != '%' and \
                       self.metadata.unit != main_qa['qa_variability'][1]:
                        self.error("Unit '{}' used for 'QA{} variability' is "
                            "inconsistent with 'Unit' ({})".format(
                                main_qa['qa_variability'][1], qanum_txt,
                                self.metadata.unit))


            # check varaible specific metadata:
            for vnum in range(len(self.variables)):
                file_vnum, _, file_metalnum = self.msgref_vnum_lnum(vnum)
                qa_ = main_qa.copy()  # need a copy, because of update below
                # update with var metadata:
                var_qa = self.get_qa_by_number(qanum, vnum)
                if var_qa:
                    qa_.update(var_qa)
                if isinstance(qa_['qm_id'], EbasMetadataInvalid):
                    continue
                if self._is_empty_qa(qa_):
                    continue
                if qm_.new_reference_calibration(main_qa['qm_id']):
                    continue
                
                # check mandatory metadata
                mandatory = (
                    ('qm_id', 'QA{} measure ID'.format(qanum_txt)),
                    ('qa_date', 'QA{} date'.format(qanum_txt)))
                    #('qa_outcome', 'QA{} outcome'.format(qanum_txt)))
                for err in [key[1] for key in mandatory
                            if qa_[key[0]] is None]:
                    self.error(
                        "Variable {}: {} is mandatory".format(file_vnum,
                                                              err),
                        lnum=file_metalnum)

                ft_type = self.get_meta_for_var(vnum, "instr_type")
                comp_name = self.get_meta_for_var(vnum, "comp_name")
                # check QV validity:
                if isvalid(ft_type) and isvalid(comp_name) and \
                   (qa_['qm_id'] != main_qa['qm_id'] or \
                    ft_type != main_ft_type or \
                    comp_name != main_comp_name):
                    try:
                        # IP masterdata lookup with additional data level:
                        # if IP is not defined in DB masterdata, lookup in
                        # exceptional masterdata (data level dependent, not
                        # meant to be imported)
                        qv_[(qa_['qm_id'], ft_type, comp_name,
                             self.metadata.datalevel)]
                    except KeyError:
                        self.error(
                            "Variable {}: QA{} measure ID/Instrument type/"
                            "Component combination '{}'/'{}'/'{}' is not "
                            "defined"
                            .format(file_vnum, qanum_txt, qa_['qm_id'],
                                    ft_type, comp_name),
                            lnum=file_metalnum)
                if isvalid(qa_['qm_id']):
                    qm_dict = qm_[qa_['qm_id']]
                    # check QA date is within QM date start and date end:
                    if qa_['qm_id'] != main_qa['qm_id'] or \
                       qa_['qa_date'] != main_qa['qa_date']:
                        if (qm_dict.QM_START and qa_['qa_date'] and \
                            qa_['qa_date'] < qm_dict.QM_START) or \
                           (qm_dict.QM_END and qa_['qa_date'] and \
                            qa_['qa_date'] > qm_dict.QM_END):
                            if qm_dict.QM_START and qm_dict.QM_END:
                                self.error(
                                    "Variable {}: QA{} date must be between {} and "
                                    "{}".format(file_vnum, qanum_txt,
                                                qm_dict.QM_START, qm_dict.QM_END),
                                    lnum=file_metalnum)
                            elif qm_dict.QM_START:
                                self.error(
                                    "Variable {}: QA{} date must be at or after {}"
                                    .format(file_vnum, qanum_txt, qm_dict.QM_START),
                                    lnum=file_metalnum)
                            else:
                                self.error(
                                    "Variable {}: QA{} date must be at or before {}"
                                    .format(file_vnum, qanum_txt, qm_dict.QM_END),
                                    lnum=file_metalnum)
                    # check QA document metadata are consistent with QM:
                    if qa_['qm_id'] != main_qa['qm_id'] or \
                       qa_['qa_doc_name'] != main_qa['qa_doc_name']:
                        if qm_dict.QM_DOCUMENT_TITLE and qa_['qa_doc_name'] and \
                           qm_dict.QM_DOCUMENT_TITLE != qa_['qa_doc_name']:
                            self.error(
                                "Variable {}: QA{} document name must be'{}'"
                                .format(file_vnum, qanum_txt,
                                        qm_dict.QM_DOCUMENT_TITLE),
                                lnum=file_metalnum)
                    if qa_['qm_id'] != main_qa['qm_id'] or \
                       qa_['qa_doc_date'] != main_qa['qa_doc_date']:
                        if qm_dict.QM_DOCUMENT_DATE and qa_['qa_doc_date'] and \
                           qm_dict.QM_DOCUMENT_DATE != qa_['qa_doc_date']:
                            date_txt = qm_dict.QM_DOCUMENT_DATE.strftime("%Y%m%d") \
                                if qm_dict.QM_DOCUMENT_DATE.time() == \
                                    datetime.time(0, 0) \
                                else qm_dict.QM_DOCUMENT_DATE.strftime(
                                    "%Y%m%d$H%M%S")
                            self.error(
                                "Variable {}: QA{} document date must be '{}'"
                                .format(file_vnum, qanum_txt, date_txt),
                                lnum=file_metalnum)
                    if qa_['qm_id'] != main_qa['qm_id'] or \
                       qa_['qa_doc_url'] != main_qa['qa_doc_url']:
                        if qm_dict.QM_DOCUMENT_URL and qa_['qa_doc_url'] and \
                           qm_dict.QM_DOCUMENT_URL != qa_['qa_doc_url']:
                            self.error(
                                "Variable {}: QA{} document name must be '{}'"
                                .format(file_vnum, qanum_txt,
                                        qm_dict.QM_DOCUMENT_URL),
                                lnum=file_metalnum)

                    unit = self.get_meta_for_var(vnum, 'unit')
                    # check qa bias unit: must be consistent for each variable
                    # check always, even if qm_id and qm_variablility is the
                    # same as in NCOM (check unit against var's unit!)
                    if isvalid(qa_['qa_bias']) and \
                        qa_['qa_bias'][1] != '%' and \
                        qa_['qa_bias'][1] != unit:
                        self.error(
                            "Variable {}: Unit '{}' used for 'QA{} bias' "
                            "is inconsistent with variable's unit ('{}')"
                                .format(file_vnum, qa_['qa_bias'][1],
                                        qanum_txt, unit))
                    # check qa variability unit: must be consistent for each
                    # variable
                    # check always, even if qm_id and qm_variablility is the
                    # same as in NCOM (check unit against var's unit!)
                    if isvalid(qa_['qa_variability']) and \
                        qa_['qa_variability'][1] != '%' and \
                        qa_['qa_variability'][1] != unit:
                        self.error(
                            "Variable {}: Unit '{}' used for 'QA{} variability' "
                            "is inconsistent with variable's unit ('{}')"
                                .format(file_vnum, qa_['qa_variability'][1],
                                        qanum_txt, unit))


    def _check_interdep_uncertainty(self):
        """
        Check consistency of uncertainty.
        Parameters:
            None
        Returns:
            None
        """
        # check uncertainty/unit: must be consistent within NNCOM
        if isvalid(self.metadata.uncertainty) and \
           self.metadata.uncertainty[1] != '%' and \
           self.metadata.unit != self.metadata.uncertainty[1]:
            self.error("Unit '{}' ".format(self.metadata.uncertainty[1]) +\
                "used for 'Measurement uncertainty' is inconsistent with " +\
                "'Unit' ({})".format(self.metadata.unit))
        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            unit = self.get_meta_for_var(i, 'unit')

            # special: ignore NNCOM uncertainty for variables where unit does
            # not match (relative uncertainties [%] match ALL variables)
            if 'uncertainty' not in self.variables[i].metadata and \
               isvalid(self.metadata.uncertainty) and \
               self.metadata.uncertainty[1] != '%' and \
               self.metadata.uncertainty[1] != unit:
                self.warning(
                    "Variable {}: unit '{}' used for 'Measurement uncertainty' "
                    "is inconsistent with variable's unit ('{}'); "
                    "uncertainty definition will not be applied".format(
                        file_vnum,
                        self.metadata.uncertainty[1], unit),
                    lnum=file_metalnum)
                self.variables[i].metadata['uncertainty'] = None
                if 'uncertainty_desc' not in self.variables[i].metadata:
                    self.variables[i].metadata['uncertainty_desc'] = None
                    self.warning(
                        "Variable {}: 'Measurement uncertainty expl.' will not "
                        "be applied for the same reason".format(
                            file_vnum),
                        lnum=file_metalnum)

            # check uncertainty/unit: must be consistent for each variable
            uncert = self.get_meta_for_var(i, 'uncertainty')
            if uncert and uncert[1] != '%' and uncert[1] != unit:
                self.error(
                    "Variable {}: unit '{}' used for 'Measurement uncertainty' "
                    "is inconsistent with variable's unit ('{}')".format(
                        file_vnum, uncert[1], unit),
                    lnum=file_metalnum)

    def _check_interdep_detectionlimit(self):
        """
        Check consistency of detection limit.
        Parameters:
            None
        Returns:
            None
        """
        # check detection limit/unit: must be consistent within NNCOM
        if isvalid(self.metadata.detection_limit) and \
           self.metadata.unit != self.metadata.detection_limit[1]:
            self.error("Unit '{}' ".format(self.metadata.detection_limit[1]) +\
                "used for 'Detection limit' is inconsistent with " +\
                "'Unit' ('{}')".format(self.metadata.unit))
        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            unit = self.get_meta_for_var(i, 'unit')

            # special: ignore NNCOM detection limit for variables where unit
            # does not match
            if 'detection_limit' not in self.variables[i].metadata and \
               isvalid(self.metadata.detection_limit) and \
               self.metadata.detection_limit[1] != unit:
                self.warning(
                    "Variable {}: unit '{}' used for 'Detection limit' is "
                    "inconsistent with variable's unit ('{}'); "
                    "detection limit definition will not be applied".format(
                        file_vnum,
                        self.metadata.detection_limit[1], unit),
                    lnum=file_metalnum)
                self.variables[i].metadata['detection_limit'] = None
                if 'detection_limit_desc' not in self.variables[i].metadata:
                    self.variables[i].metadata['detection_limit_desc'] = None
                    self.warning(
                        "Variable {}: 'Detection limit expl.' will not be "
                        "applied for the same reason".format(
                            file_vnum),
                        lnum=file_metalnum)
            # check detection limit/unit: must be consistent for each variable
            detect = self.get_meta_for_var(i, 'detection_limit')
            if isvalid(detect) and detect[1] != unit:
                self.error(
                    "Variable {}: unit '{}' used for 'Detection limit' is "
                    "inconsistent with variable's unit ('{}')".format(
                        file_vnum, detect[1], unit),
                    lnum=file_metalnum)

    def _check_interdep_upperrangelimit(self):
        """
        Check consistency of upper range limit. Additionally check consistency
        of upper range limit and detection limit.
        Parameters:
            None
        Returns:
            None
        """
        # check upper range limit/unit: must be consistent within NNCOM
        if isvalid(self.metadata.upper_range_limit) and \
           self.metadata.unit != self.metadata.upper_range_limit[1]:
            self.error(
                "Unit '{}' ".format(self.metadata.upper_range_limit[1]) +\
                "used for 'Upper range limit' is inconsistent with " +\
                "'Unit' ('{}')".format(self.metadata.unit))
        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            unit = self.get_meta_for_var(i, 'unit')

            # special: ignore NNCOM upper range limit for variables where unit
            # does not match
            if 'upper_range_limit' not in self.variables[i].metadata and \
               isvalid(self.metadata.upper_range_limit) and \
               self.metadata.upper_range_limit[1] != unit:
                self.warning(
                    "Variable {}: unit '{}' used for 'Upper range limit' is "
                    "inconsistent with variable's unit ('{}'); upper range "
                    "limit definition will not be applied".format(
                        file_vnum,
                        self.metadata.upper_range_limit[1], unit),
                    lnum=file_metalnum)
                self.variables[i].metadata['upper_range_limit'] = None

            # check upper range limit/unit: must be consistent for each variable
            upper = self.get_meta_for_var(i, 'upper_range_limit')
            if upper and upper[1] != unit:
                self.error(
                    "Variable {}: unit '{}' used for 'Upper range limit' is "
                    "inconsistent with variable's unit ('{}')".format(
                        file_vnum, upper[1], unit),
                    lnum=file_metalnum)

            # check detection limit lower then upper range limit
            detect = self.get_meta_for_var(i, 'detection_limit')
            upper = self.get_meta_for_var(i, 'upper_range_limit')
            if detect and upper and detect[0] >= upper[0]:
                self.error(
                    "Variable {}: detection limit ({} {}) must be lower then "
                    "upper range limit ({} {})".format(
                        file_vnum,
                        detect[0], detect[1], upper[0], upper[1]),
                    lnum=file_metalnum)

    def _check_interdep_instrument(self):
        """
        Check consistency of instrument metadata.
        Parameters:
            None
        Returns:
            None
        """
        # instrument metadata must be only consistent within NNCOM if all three
        # are set
        allset = False
        if isvalid(self.metadata.instr_type) and \
           isvalid(self.metadata.instr_manufacturer) and \
           isvalid(self.metadata.instr_model):
            # check global metadata consistency only when ALL THREE are set!
            allset = True
            try:
                EbasMasterFM()[
                    (self.metadata.instr_type, self.metadata.instr_manufacturer,
                     self.metadata.instr_model)]
            except KeyError:
                self.error(
                    "Instrument type/manufacturer/model "
                    "combination '{}'/'{}'/'{}' is not defined".format(
                        self.metadata.instr_type,
                        self.metadata.instr_manufacturer,
                        self.metadata.instr_model))

        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            instr_type = self.get_meta_for_var(i, 'instr_type')
            fm_man = self.get_meta_for_var(i, 'instr_manufacturer')
            fm_mod = self.get_meta_for_var(i, 'instr_model')
            if fm_man is not None or fm_mod is not None:
                # model or manufacturer is set for this variable: check
                if allset and \
                   'instr_type' not in self.variables[i].metadata and \
                   'instr_manufacturer' not in self.variables[i].metadata and \
                   'instr_model' not in self.variables[i].metadata:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                # check if any is not set or set with an illegal value:
                dependencies = []
                if not isvalid(instr_type):
                    dependencies.append('instrument type')
                if not isvalid(fm_man):
                    dependencies.append('instrument manufacturer')
                if not isvalid(fm_mod):
                    dependencies.append('instrument model')
                if dependencies:
                    self.error(
                        "Variable {}: Instrument type/manufacturer/model "
                        "combination could not be checked because {} is not "
                        "specified correctly".format(
                            file_vnum, " and ".join(dependencies)),
                        lnum=file_metalnum)
                else:
                    try:
                        EbasMasterFM()[(instr_type, fm_man, fm_mod)]
                    except KeyError:
                        self.error(
                            "Variable {}: Instrument type/manufacturer/model "
                            "combination '{}'/'{}'/'{}' is not defined".format(
                                file_vnum, instr_type, fm_man, fm_mod),
                            lnum=file_metalnum)

    def _check_interdep_inlet(self):
        """
        Check consistency of Inlet tube outer and inner diameter.
        Parameters:
            None
        Returns:
            None
        """
        if isvalid(self.metadata.inlet_tube_outerD) and \
           isvalid(self.metadata.inlet_tube_innerD) and \
            self.metadata.inlet_tube_outerD <= self.metadata.inlet_tube_innerD:
            self.error(
                "Inlet tube outer diameter ({} mm) is not greater than "
                "inlet tube inner diameter ({} mm)".format(
                    self.metadata.inlet_tube_outerD,
                    self.metadata.inlet_tube_innerD))
        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            outer = self.get_meta_for_var(i, 'inlet_tube_outerD')
            inner = self.get_meta_for_var(i, 'inlet_tube_innerD')
            if outer is not None and inner is not None:
                # innerD and outerD is set for this variable: check
                if 'inlet_tube_outerD' not in self.variables[i].metadata and \
                   'inlet_tube_innerD' not in self.variables[i].metadata:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                # check if any is not set or set with an illegal value:
                if outer <= inner:
                    self.error(
                        "Variable {}: Inlet tube outer diameter ({} mm) is not "
                        "greater than inlet tube inner diameter ({} mm)".format(
                            file_vnum, outer, inner), lnum=file_metalnum)

    def _check_interdep_analytical(self):
        """
        Check consistency of analytical metadata.
        Parameters:
            None
        Returns:
            None
        """
        # instrument metadata must be only consistent within NNCOM if all three
        # are set
        allset = False
        if isvalid(self.metadata.ana_technique) and \
           isvalid(self.metadata.ana_instr_manufacturer) and \
           isvalid(self.metadata.ana_instr_model):
            # check global metadata consistency only when ALL THREE are set!
            allset = True
            try:
                EbasMasterAM()[(self.metadata.ana_technique,
                                self.metadata.ana_instr_manufacturer,
                                self.metadata.ana_instr_model)]
            except KeyError:
                self.error(
                    "Analytical instrument technique/manufacturer/model "
                    "combination '{}'/'{}'/'{}' is not defined".format(
                        self.metadata.ana_technique,
                        self.metadata.ana_instr_manufacturer,
                        self.metadata.ana_instr_model))

        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            ana_technique = self.get_meta_for_var(i, 'ana_technique')
            am_man = self.get_meta_for_var(i, 'ana_instr_manufacturer')
            am_mod = self.get_meta_for_var(i, 'ana_instr_model')

            if am_man is not None or am_mod is not None:
                # model or manufacturer is set for this variable: check
                if allset and \
                   'ana_technique' not in self.variables[i].metadata and \
                   'am_man' not in self.variables[i].metadata and \
                   'am_mod' not in self.variables[i].metadata:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                # check if any is not set or set with an illegal value:
                dependencies = []
                if not isvalid(ana_technique):
                    dependencies.append('analytical measurement technique')
                if not isvalid(am_man):
                    dependencies.append('analytical instrument manufacturer')
                if not isvalid(am_mod):
                    dependencies.append('analytical instrument model')
                if dependencies:
                    self.error(
                        "Variable {}: Analytical measurement technique/"
                        "manufacturer/model combination could not be checked "
                        "because {} is not specified correctly".format(
                            file_vnum, " and ".join(dependencies)),
                        lnum=file_metalnum)
                else:
                    try:
                        EbasMasterAM()[(ana_technique, am_man, am_mod)]
                    except KeyError:
                        self.error(
                            "Variable {}: Analytical measurement technique/"
                            "manufacturer/model combination '{}'/'{}'/'{}' is "
                            "not defined".format(
                                file_vnum, ana_technique, am_man, am_mod),
                            lnum=file_metalnum)

    def _check_interdep_sensortype(self):
        """
        Check consistency of sensor type and instrument type / component.
        Parameters:
            None
        Returns:
            None
        """
        # metadata must be only consistent within NNCOM if both are set.
        allset = False
        instr_type = self.metadata.instr_type
        sensor_type = self.metadata.sensor_type
        # only use main component name if it is a "real" component, and
        # not just an arbitrary name:
        if self._is_real_comp(self.metadata.comp_name):
            comp_name = self.metadata.comp_name
        else:
            comp_name = None
        if isvalid(instr_type) and isvalid(comp_name) and isvalid(sensor_type):
            allset = True
            try:
                _ = EbasMasterSE()[(instr_type, comp_name, sensor_type)]
            except KeyError:
                self.error(
                    "Instrument type/Component/Sensor type combination "
                    "'{}'/'{}'/'{}' is not defined").format(
                        instr_type, comp_name, sensor_type)

        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            instr_type = self.get_meta_for_var(i, 'instr_type')
            comp_name = self.get_meta_for_var(i, 'comp_name')
            sensor_type = self.get_meta_for_var(i, 'sensor_type')
            if isvalid(instr_type) and isvalid(comp_name) and \
               isvalid(sensor_type):
                if allset and \
                   'instr_type' not in self.variables[i].metadata and \
                   comp_name == self.get_meta_for_var(i, 'comp_name') and \
                   'sensor_type' not in self.variables[i].metadata:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                try:
                    _ = EbasMasterSE()[(instr_type, comp_name, sensor_type)]
                except KeyError:
                    self.error(
                        "Variable {}: Instrument type/Component/Sensor type "
                        "combination '{}'/'{}'/'{}' is not defined".format(
                            file_vnum, instr_type, comp_name, sensor_type),
                        lnum=file_metalnum)

    def _check_interdep_absorption_crosssection(self):
        """
        Check consistency of absorption cross section and component.
        Parameters:
            None
        Returns:
            None
        """
        # metadata must be only consistent within NNCOM if both are set.
        allset = False
        main_abs_cross_section = self.metadata.abs_cross_section
        # only use main component name if it is a "real" component, and
        # not just an arbitrary name:
        if self._is_real_comp(self.metadata.comp_name):
            main_comp_name = self.metadata.comp_name
        else:
            main_comp_name = None
        if isvalid(main_comp_name) and isvalid(main_abs_cross_section):
            allset = True
            try:
                _ = EbasMasterAX()[(main_comp_name, main_abs_cross_section)]
            except KeyError:
                self.error(
                    "Component/Absorption cross section "
                    "'{}'/'{}' is not defined").format(
                        main_comp_name, main_abs_cross_section)

        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            comp_name = self.get_meta_for_var(i, 'comp_name')
            abs_cross_section = self.get_meta_for_var(i, 'abs_cross_section')
            if isvalid(comp_name) and isvalid(abs_cross_section):
                if allset and \
                   comp_name == main_comp_name and \
                   abs_cross_section == main_abs_cross_section:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                try:
                    _ = EbasMasterAX()[(comp_name, abs_cross_section)]
                except KeyError:
                    self.error(
                        "Variable {}: Component/Absorption cross section "
                        "combination '{}'/'{}' is not defined".format(
                            file_vnum, comp_name, abs_cross_section),
                        lnum=file_metalnum)

    def _check_interdep_calibrationscale(self):
        """
        Check consistency of sensor type and instrument type / component.
        Parameters:
            None
        Returns:
            None
        """
        # metadata must be only consistent within NNCOM if both are set.
        allset = False
        main_cal_scale = self.metadata.cal_scale
        # only use main component name if it is a "real" component, and
        # not just an arbitrary name:
        if self._is_real_comp(self.metadata.comp_name):
            main_comp_name = self.metadata.comp_name
        else:
            main_comp_name = None
        if isvalid(main_comp_name) and isvalid(main_cal_scale):
            allset = True
            try:
                _ = EbasMasterCA()[(main_comp_name, main_cal_scale,
                                    self.metadata.datalevel)]
            except KeyError:
                self.error(
                    "Component/Calibration scale combination '{}'/'{}' is not "
                    "defined".format(main_comp_name, main_cal_scale))

        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            comp_name = self.get_meta_for_var(i, 'comp_name')
            cal_scale = self.get_meta_for_var(i, 'cal_scale')
            if isvalid(comp_name) and isvalid(cal_scale):
                if allset and \
                   comp_name == main_comp_name and \
                   cal_scale == main_cal_scale:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                try:
                    _ = EbasMasterCA()[(comp_name, cal_scale,
                                        self.metadata.datalevel)]
                except KeyError:
                    self.error(
                        "Variable {}: Component/Calibration scale combination "
                        "'{}'/'{}' is not defined".format(
                            file_vnum, comp_name, cal_scale),
                        lnum=file_metalnum)

    def _check_interdep_stdmethod(self):
        """
        Check consistency of standard method and instrument type.
        Parameters:
            None
        Returns:
            None
        """
        # metadata must be only consistent within NNCOM if both are set.
        allset = False
        instr_type = self.metadata.instr_type
        std_method = self.metadata.std_method
        if isvalid(instr_type) and isvalid(std_method):
            allset = True
            try:
                _ = EbasMasterSM()[(instr_type, std_method)]
            except KeyError:
                self.error(
                    "Instrument type/Standard method combination '{}'/'{}' is "
                    "not defined".format(instr_type, std_method))

        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)
            instr_type = self.get_meta_for_var(i, 'instr_type')
            std_method = self.get_meta_for_var(i, 'std_method')
            if isvalid(instr_type) and isvalid(std_method):
                if allset and \
                   'instr_type' not in self.variables[i].metadata and \
                   'std_method' not in self.variables[i].metadata:
                    # all are set in NCOM and none is set per variable:
                    # no need to check
                    continue
                try:
                    _ = EbasMasterSM()[(instr_type, std_method)]
                except KeyError:
                    self.error(
                        "Variable {}: Instrument type/Standard method "
                        "combination '{}'/'{}' is not defined".format(
                            file_vnum, instr_type, std_method),
                        lnum=file_metalnum)

    def _check_interdep_parameter(self, ignore_parameter=False):
        """
        Check consistency of parameter.
           1) validity of triple (regime, matrix, component)
           2) consistency of unit
           3) validity of the parameter for the instrument
        Parameters:
            ignore_parameter  ignore inconsistencies in parameters (downgrade
                              error to warning)
        Returns:
            None
        """
        # parameter metadata must be only consistent within NNCOM if all three
        # are set and component name is equal one of the vaiable's component
        # (this to allow for free component names: like VOC, inorganics, ...

        def check_param_unit(file_lnum, file_vnum, param, unit):
            """
            Helper for checking the unit is correct for parameter.
            """
            if param['PM_UNIT'] != unit:
                vtxt = ''
                if file_vnum:
                    vtxt = "Variable {}: ".format(file_vnum)
                msg = (
                    "{}Regime/Matrix/Component combination '{}'/'{}'/'{}': "
                    "unit '{}' not allowed, should be '{}'".format(
                        vtxt, param['RE_REGIME_CODE'], param['MA_MATRIX_NAME'],
                        param['CO_COMP_NAME'], unit, param['PM_UNIT']))
                if ignore_parameter:
                    self.warning(msg, lnum=file_lnum)
                else:
                    self.error(msg, lnum=file_lnum)

        def check_param_ip(file_lnum, file_vnum, instr_type, regime, matrix,
                           comp_name):
            """
            Helper for checking the intrument-type/parameter validity
            """
            try:
                # IP masterdata lookup with additional data level:
                # if IP is not defined in DB masterdata, lookup in exceptional
                # masterdata (data level dependent, not meant to be imported)
                EbasMasterIP()[
                    (instr_type, regime, matrix, comp_name,
                     self.metadata.datalevel)]
            except KeyError:
                vtxt = ''
                if file_vnum:
                    vtxt = "Variable {}: ".format(file_vnum)
                msg = (
                    "{}Regime/Matrix/Component combination '{}'/'{}'/'{}' "
                    "is not allowed for instrument type {}".format(
                        vtxt, regime, matrix, comp_name,
                        instr_type))
                if ignore_parameter:
                    self.warning(msg, lnum=file_lnum)
                else:
                    self.error(msg, lnum=file_lnum)

        regime = self.metadata.regime
        matrix = self.metadata.matrix
        comp_name = self.metadata.comp_name
        param = None
        instr_type = self.metadata.instr_type
        statistics = self.metadata.statistics
        unit = self.metadata.unit

        if isvalid(regime) and isvalid(matrix) and isvalid(comp_name) and \
           comp_name in [self.get_meta_for_var(i, 'comp_name')
                         for i in range(len(self.variables))]:
            # check global metadata consistency only when ALL THREE are set!
            try:
                # pm masterdata lookup with additional data level:
                # if pm is not defined in DB masterdata, lookup in exceptional
                # masterdata (data level dependent, not meant to be imported)
                param = EbasMasterPM()[(regime, matrix, comp_name, statistics,
                                        self.metadata.datalevel)]
            except KeyError:
                msg = (
                    "Regime/Matrix/Component combination '{}'/'{}'/'{}' is "
                    "not defined").format(regime, matrix, comp_name)
                if ignore_parameter:
                    self.warning(msg)
                else:
                    self.error(msg)
        if param and isvalid(unit):
            # check unit consistency
            check_param_unit(None, None, param, unit)
        if param and isvalid(instr_type):
            check_param_ip(None, None, instr_type, regime, matrix, comp_name)

        # do the checks for all variables:
        for i in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(i)

            # check paramter existence:
            v_regime = self.get_meta_for_var(i, 'regime')
            v_matrix = self.get_meta_for_var(i, 'matrix')
            v_comp_name = self.get_meta_for_var(i, 'comp_name')
            v_param = None
            v_unit = self.get_meta_for_var(i, 'unit')
            v_instr_type = self.get_meta_for_var(i, 'instr_type')
            v_statistics = self.get_meta_for_var(i, 'statistics')

            dependencies = []
            if not isvalid(v_regime):
                dependencies.append('Regime code')
            if not isvalid(v_matrix):
                dependencies.append('Matrix name')
            if not isvalid(v_comp_name):
                dependencies.append('Component name')
            if dependencies:
                msg = (
                    "Variable {}: Regime/Matrix/Component combination could "
                    "not be checked because {} is not specified correctly"
                    .format(file_vnum, " and ".join(dependencies)))
                if ignore_parameter:
                    self.warning(msg, lnum=file_metalnum)
                else:
                    self.error(msg, lnum=file_metalnum)
            else:
                if (v_regime, v_matrix, v_comp_name) == (regime, matrix,
                                                         comp_name):
                    v_param = param
                    if v_param and isvalid(v_unit) and v_unit != unit:
                        # the parameter triple is identical to global
                        # metadata, if the unit is identical as well, skip
                        # this check
                        check_param_unit(file_metalnum, file_vnum, v_param,
                                         v_unit)
                    if v_param and isvalid(v_instr_type) and \
                       v_instr_type != instr_type:
                        # the parameter triple is identical to global
                        # metadata, if the isntr_type is identical as well,
                        # skip this check
                        check_param_ip(file_metalnum, file_vnum, v_instr_type,
                                       v_regime, v_matrix, v_comp_name)
                else:
                    try:
                        # pm masterdata lookup with additional data level:
                        # if pm is not defined in DB masterdata, lookup in exceptional
                        # masterdata (data level dependent, not meant to be imported)
                        v_param = EbasMasterPM()[
                            (v_regime, v_matrix, v_comp_name, v_statistics,
                             self.metadata.datalevel)]
                    except KeyError:
                        msg = (
                            "Variable {}: Regime/Matrix/Component "
                            "combination '{}'/'{}'/'{}' is not defined"
                            .format(file_vnum, v_regime, v_matrix,
                                    v_comp_name))
                        if ignore_parameter:
                            self.warning(msg, lnum=file_metalnum)
                        else:
                            self.error(msg, lnum=file_metalnum)
                    if v_param and isvalid(v_unit):
                        # here, the parameter triple is already different, so
                        # check unit validity for this variable!
                        check_param_unit(file_metalnum, file_vnum, v_param,
                                         v_unit)
                    if v_param and isvalid(v_instr_type):
                        # here, the parameter triple is already different, so
                        # check instr_type validity for this variable!
                        check_param_ip(file_metalnum, file_vnum, v_instr_type,
                                       v_regime, v_matrix, v_comp_name)

    @staticmethod
    def _is_real_comp(co_comp_name):
        """
        Check if the component name is a "real" component name (exists in 
        CO_COMPONENT table). or a fake name (in the main header, like "GHG" etc.
        Parameters:
            co_comp_name    compoent name
        Returns:
            True if real name, False when fake name
        """
        co_ = EbasMasterCO()
        try:
            co_[co_comp_name].CO_COMP_NAME
        except KeyError:
            return False
        return True
