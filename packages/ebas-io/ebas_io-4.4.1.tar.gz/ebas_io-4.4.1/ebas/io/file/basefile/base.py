"""
ebas/io/base.py
$Id: base.py 2774 2022-01-10 19:03:29Z pe $

Base classes for (file) I/O.

"""

import datetime
import logging
import os.path
from six import PY3
from copy import deepcopy
from ebas.domain.basic_domain_logic.dataset_types import \
    is_precip_concentration, is_precip_amount, is_auxiliary
from ebas.domain.basic_domain_logic.flags import get_flag_summary
from ebas.io.ebasmetadata import DatasetCharacteristicList
from ebas.domain.basic_domain_logic.unit_convert import UnitConvert, \
    NoConversion
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
    estimate_resolution_code
from ebas.domain.basic_domain_logic.parameters import title
from nilutility.datatypes import DataObject
from nilutility.datetime_helper import DatetimeInterval
from nilutility.msg_condenser import MessageRecord, MessageCondenser
from ...ebasmetadata import EbasMetadata
from ebas.io.templates import get_template, NoTemplate

if PY3:
    unicode = str


class EbasMetadataInvalid(unicode):
    """
    Modified unicode class for EBAS metadata. The class is able to contain an
    unicode value in addition to the fact that the value is invalid (by class).
    A metadata parser or check function can keep the original value but set it
    to type EbasMetadataInvalid, thus downstream code will know the value is
    invalid.
    """
    pass

def isempty(var):
    """
    Check if the metadata element is empty in any way.
    Possible types of "empty":
        None    The metadata are not specified in the file or are reported
                as empty string in the file.
        EbasMetadataEmpty
                Is set when the metadata where originally set in the file, but
                the parser experienced an error. This special value is set to
                avoid false errors about mandatory metadata missing.
    """
    if var is None or isinstance(var, EbasMetadataInvalid):
        return True
    return False

def isvalid(var):
    """
    Check if the metadata element contains a valid value.
    Opposite of isempty.
    """
    return not isempty(var)

class EbasIOFileMessageRecord(MessageRecord):
    """
    Derived MessageRecord class for EbasIO:
    Adds column number to keys and line number to data.
    """
    KEYS = ['msgfunc', 'msg_id', 'vnum']
    DATA = ['message', 'line']


class EbasIOFileMessageCondenser(MessageCondenser):
    """
    Message condenser for NasaAmes logging
    """

    MSG_ID_FLAG_MISSING = 1
    MSG_ID_FLAG_ZERODOT = 2
    MSG_ID_TIME_OVERLAP = 3
    MSG_ID_TIME_MISSING = 4
    MSG_ID_TIME_INVERT = 5

    def deliver_msg(self, record, condensed):
        """
        Deliver a single message.
        Parameters:
            record     the message record
            condensed  bool, condensed message
        Returns:
            None
        """
        record.msgfunc(record.message, lnum=record.line)
        if condensed:
            lst = self.dict[record.key]
            record.msgfunc(
                "The previous message repeats {} times{}. First occurrences "
                "in lines: {}, ..."
                .format(len(lst)-1,
                        " for variable {}".format(record.vnum) \
                            if record.vnum is not None else "",
                        ", ".join(
                            [str(x.line) for x in lst[0:self.threshold]])),
                lnum=record.line, counter_increase=len(lst)-1)
            # use same lnum as above message, otherwise the lines get parted
            # in submit-tool


class EbasFileBase(object): # pylint: disable-msg=R0902
    # R0902: Too many instance attributes
    """
    Base class for all EBAS I/O objects.
    """

    IOFORMAT = None  # Must be set by derived classes

    def __init__(self, indexdb=None, condense_messages=0):
        """
        Constructor for class IOBase.
        Parameters:
            indexdb           index db object (if indexdb should be written)
            condense_messages threshold for condensing repeating messages.
                              0 turns off condensation.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # strict global metadata: this is considered part of the file format
        # specification and must be set in the __init__ of all derived classes.
        # (only metadata which apply to ALL variables are considered global)
        self.strict_global = None

        self.indexdb = indexdb
        self.msg_condenser = EbasIOFileMessageCondenser(
            threshold=condense_messages, record_cls=EbasIOFileMessageRecord)
        # TODO: most of the internal attributes are only used by one of the
        # derived classes (NasaAmes parser, fromdomain, todomain etc)
        self.from_domain = False
        self.internal = \
            DataObject(
                # metadata.timeref as timedelta object
                timeoffset=datetime.timedelta(seconds=0),
                # temporary attributes used during reading in different
                #implementations:
                read_tmp=None,
                # temporary attributes used in from_domain:
                fromdomain_tmp=None,
                # used internaly for I/O of ebas specific metadata,
                # will be initialized to an EbasMetadata object on read/write
                ebasmetadata=None,
                )
        self.metadata = \
            DataObject(setkey=None,    # dataset id (needed for xml export)
                       datadef=None,   # specification of file format
                       license=None,   # license URI
                       citation=None,  # citation string
                       filename=None,  # generated filename
                       doi=None,       # doi URI and optional part number
                       # [doi, part]
                       # (part number of the doi) if DOI is exported to multiple
                       # files
                       doi_list=None,  # list of DOIs (series state) the file
                       # contains data from []
                       creation_time=None, # file creation date (datetime)
                       export_state=None,  # export state for DB extracts
                       export_filter=None,  # export filter (f900, invalid)
                       startdate=None, # first start time (datetime)
                       timezone=None,  # timezone, currently only UTC
                       org=None,       # ORG code (string)
                       originator=[],  # list of EbasDB PS dict.
                       submitter=[],   # list of EbasDB PS dict.
                       projects=[],    # list of PR_ACRONYMS (strings)
                       # list of project names, descriptions, contact names and
                       # contact emails: only for output and for non-NasaAmes:
                       project_names = [],
                       project_descs = [],
                       project_cotact_names = [],
                       project_contact_emails = [],
                       type=None,      # 'TU' / 'TI' (string)
                       revision=None,  # revision number (string)
                       revdate=None,   # latest update data or meta (datetime)
                       revdesc=None,   # revision desc (string)
                       input_dataset=None, # list of strings
                       software=None,  # software (string)
                       acknowledgements=None, # (string)
                       reference_date=None, # zero point of time axes (datetime)
                       timeref=None,   # timeref HH_MM (string)
                       period=None,
                       resolution=None,
                       rescode_sample=None,
                       duration=None,
                       datalevel=None,
                       regime=None,
                       matrix=None,
                       comp_name=None, # component name
                       unit=None,
                       statistics=None,# statistics code
                       characteristics=None, # ds characteristics (dict)
                       title=None,     # title name (comp.caption or comp.name)
                       station_code=None,
                       platform_code=None, # (7 chars including 6 char st.code)
                       station_name=None,
                       station_wdca_id=None,
                       station_gaw_name=None,
                       station_gaw_id=None,
                       station_airs_id=None,
                       station_other_ids=None,
                       station_state_code=None,
                       station_landuse=None,
                       station_setting=None,
                       station_gaw_type=None,
                       station_wmo_region=None,
                       station_latitude=None,
                       station_longitude=None,
                       station_altitude=None,
                       mea_latitude=None,
                       mea_longitude=None,
                       mea_altitude=None,
                       mea_height=None,
                       instr_type=None,
                       lab_code=None,
                       instr_name=None,
                       instr_manufacturer=None,
                       instr_model=None,
                       instr_serialno=None,
                       sensor_type=None,
                       ana_technique=None,
                       ana_lab_code=None,
                       ana_instr_name=None,
                       ana_instr_manufacturer=None,
                       ana_instr_model=None,
                       ana_instr_serialno=None,
                       cal_scale=None,
                       cal_std_id=None,
                       sec_std_id=None,
                       inlet_type=None,
                       inlet_desc=None,
                       inlet_tube_material=None,  # string, restricted
                       inlet_tube_outerD=None,    # float, unit=mm
                       inlet_tube_innerD=None,    # float, unit=mm
                       inlet_tube_length=None,    # float, unit=m
                       maintenance_desc=None,     # string, freetext
                       hum_temp_ctrl=None,
                       hum_temp_ctrl_desc=None,
                       vol_std_temp=None,
                       vol_std_pressure=None,
                       detection_limit=None,  # (value, unit)
                       detection_limit_desc=None,
                       upper_range_limit=None,  # (value, unit)
                       uncertainty=None,  # (value, unit)
                       uncertainty_desc=None,
                       zero_negative=None,
                       zero_negative_desc=None,
                       ext_lab=None,
                       method=None,
                       std_method=None,
                       medium=None,
                       flow_rate=None,
                       filter_face_velocity=None,
                       filter_area=None,
                       filter_descr=None,
                       filter_prefiring=None,
                       filter_conditioning=None,
                       coating_solution=None,
                       sample_prep=None,
                       blank_corr=None,
                       artifact_corr=None,
                       artifact_corr_desc=None,
                       charring_corr=None,
                       ozone_corr=None,
                       watervapor_corr=None,
                       zero_span_type=None,       # string: automatic/manual
                       zero_span_interval=None,   # period code, e.g 1d
                       abs_cross_section=None,    # float (unit=cm2)
                       qa=None,                   # dictionary, many QA blocks
                       # example:
                       # [
                       #   DataObject({
                       #    'qa_number': 1,
                       #    'qm_id': '...',
                       #    'qa_date': datetime.datetime(...),
                       #    ...}),
                       #   DataObject(...)
                       #   ...
                       # ]
                       comment=None,

                       # elements only supporded in lev 0 (implemented in
                       # ebasmetadata with condition data_level == 0
                       # those elements are NOT implemented in ebas.domain!
                       time_inlet_to_converter=None,
                       time_converter_or_bypass_line=None,
                       time_stay_converter= None,
                       converter_temp= None,
                       filter_type=None,
                       multi_scattering_corr_fact=None,
                       max_attenuation=None,
                       leakage_factor_zeta=None,
                       comp_thresh_atten1=None,
                       comp_thresh_atten2=None,
                       comp_param_kmin=None,
                       comp_param_kmax=None,
                       mass_abs_cross_section=None,
                       coincidence_corr = None,
                       charge_type = None,
                       inlet_diffusion_loss_data = None,
                       cpc_default_pulse_width = None,
                       normalized_ion_mobility = None,
                       number_density_of_air = None,
                       normalized_pressure = None,
                       normalized_count_rate = None,
                       drift_tube_length = None,
                      )

        self.sample_times = []
        # self.sample times: list of tupels (start, end)
        # (subsetted to correct time interval)

        self.variables = []
        # self.variables: list of DataObject:
        #  {
        #    is_hex:    True for hexint variables (e.g. instrument status)
        #    values_:   measurement values (list)
        #               (subsetted to correct time interval)
        #    flags:     flags for measurments (list of tuples)
        #               (subsetted to correct time interval)
        #    flagcol:   Bool, whether this variable needs a flag column
        #    flagtitle: Text, used as title for flag column
        #               (analog to metadata.title for the variable itself)
        #    metadata   variable specific metadata
        #               (potentially the same keys as self.metadata, but only if
        #                it differs from self.metadata)
        #
        #    internal metadata (only used on demand):
        #
        #  }

        # attributes needed for error handling
        self.errors = 0
        self.warnings = 0

    def from_ebasfile(self, ebasfile):
        """
        Clone object from another ebas file objects.
        """
        self.metadata = deepcopy(ebasfile.metadata)
        self.sample_times = deepcopy(ebasfile.sample_times)
        self.variables = deepcopy(ebasfile.variables)

    def setup_non_domain(self):
        """
        """
        self.internal.nondomain_tmp = DataObject(id_set=set())

    def merge_var_non_domain(self, id, metadata, sample_times, values, flags,
            convert, is_hex=False):
        """
        For data source other than ebas domain
        Add variable to file if it fits (metadata and the timesseries must be
        matching).
        Parameters:
            metadata        metadata dict (DataObject)
            sample_times    sample times list
            values          values list
            flags           flags list
            convert         unit conversion: 0 none, 1 convert,
                                             2 add additional converted variable
            is_hex          should be represented in hex
        Returns:
            (state, remaining)
            state: True (could be added), False (could not be added)
            remaining:
                None in case of state==Flase
                else: list of remaining intervals, each tuple
                      (saple_times, values, flags)
        """
        if len(sample_times) != len(values) or len(sample_times) != len(flags):
            raise RuntimeError("different sample times and values/flags")
        if not sample_times and self.sample_times or \
                sample_times and not self.sample_times:
            # samples do not overlap
            return False, None
        if sample_times and \
                (sample_times[0][0] > self.sample_times[0][0] or \
                 sample_times[-1][1] < self.sample_times[-1][1]):
            return False, None
        start = 0
        for i in range(len(sample_times)):
            if sample_times[i] == self.sample_times[0]:
                start = i
                break
        else:
            return False, None
        if self.sample_times != \
                sample_times[start:len(self.sample_times)+start]:
            return False, None

        # fix metadata defaults:
        if 'org' not in metadata:
            metadata.org = None
        if 'station_code' not in metadata:
            metadata.station_code = None
        if 'lab_code' not in metadata:
            metadata.lab_code = None
        if 'instr_name' not in metadata:
            metadata.instr_name = None
        if 'matrix' not in metadata:
            metadata.matrix = None
        if 'comp_name' not in metadata:
            metadata.comp_name = None
        if 'originator' not in metadata:
            metadata.originator = []
        if 'projects' not in metadata:
            metadata.projects = []

        # metadata that may NOT differ in one file:
        # organisation, station, originators, submitters, projects,\
        if self.get_meta_for_var(0, 'org') != metadata.org or \
            self.get_meta_for_var(0, 'station_code') != metadata.station_code:
            return False, None
        # generally avoid different instruments. but allow for:
        #  - precip amount
        #  - matrix position
        if self.get_meta_for_var(0, 'lab_code') != metadata.lab_code or \
            self.get_meta_for_var(0, 'instr_name' != metadata.instr_name):
            # this would be a new instrument for this file
            if metadata.matrix != 'position' and \
               not any([self.get_meta_for_var(i, 'matrix') == 'position'
                        for i in range(len(self.variables))]):
                if (not is_precip_amount(metadata.matrix, metadata.comp_name) and \
                    not is_precip_concentration(metadata.matrix, metadata.comp_name)) or \
                   (is_precip_amount(metadata.matrix, metadata.comp_name) and not \
                    any([self.is_precip_concentration(i) for i in range(len(self.variables))])) or \
                   (is_precip_concentration(metadata.matrix, metadata.comp_name) and not \
                    any([self.is_precip_amount(i) for i in range(len(self.variables))])):
                    return False, None

        if set(tuple([tuple(sorted(x.items()))
                      for x in self.get_meta_for_var(0, 'originator')])) != \
           set(tuple([tuple(sorted(x.items()))
                      for x in metadata.originator])):
            return False, None
        # submission metadata can go to the same nasa_ames file
        # Set of projects must be checked in any cas. Can be changed afterwards,
        # thus the same submission is _not_ sufficient.
        if set(self.get_meta_for_var(0, 'projects')) != set(metadata.projects):
            return False, None

        # if this variable is not already in the file, add the variable:
        if id not in self.internal.nondomain_tmp.id_set:
            self._add_variable_nondomain(
                id,
                metadata, 
                values[start:start+len(self.sample_times)],
                flags[start:start+len(self.sample_times)],
                convert,
                is_hex=is_hex)
        # calculate remaining interval(s):
        remain = []
        if  start > 0:
            remain.append((sample_times[0:start], values[0:start],
                flags[0:start]))
        if len(sample_times) > start + len(self.sample_times):
            rest = start + len(self.sample_times)
            remain.append((sample_times[rest:], values[rest:], flags[rest:]))
        return True, remain

    def _add_variable_nondomain(self, id, metadata, values, flags, convert,
        is_hex=False):
        """
        Add variable to file (other sources than ebas domain).
        Parameters:
            metadata        metadata dict (DataObject)
            values          values list
            flags           flags list
            convert         unit conversion: 0 none, 1 convert,
                                             2 add additional converted variable
            is_hex          should be represented in hex
        Returns:
            None
        """
        self.internal.nondomain_tmp.id_set.add(id)
        self.variables.append(
            DataObject(
                values_=values, flags=flags, flagcol=True,
                metadata=DataObject(metadata), is_hex=is_hex))
        if convert == 1:
            # convert variable if needed:
            self._convert_variable_output_new()
        if convert == 2:
            try:
                vol_std_temp = float(metadata.vol_std_temp)
            except (ValueError, TypeError, AttributeError):
                # ValueError if string, eg instrument internal
                # TypeError if None
                # AttributeError if not in metadsta
                vol_std_temp = None
            try:
                vol_std_pressure = float(metadata.vol_std_pressure)
            except (ValueError, TypeError, AttributeError):
                # ValueError if string, eg instrument internal
                # TypeError if None
                # AttributeError if not in metadsta
                vol_std_pressure = None
            regime = metadata.regime if 'regime' in metadata else None
            matrix = metadata.matrix if 'matrix' in metadata else None
            comp_name = metadata.comp_name if 'comp_name' in metadata else None
            unit = metadata.unit if 'unit' in metadata else None
            try:
                unit_convert = UnitConvert()
                unit_convert.export_conv_params(
                    regime, matrix, comp_name, unit,
                    vol_std_pressure, vol_std_temp)
                # We do not care about the result here. We just know there is a
                # possible conversion if there is no NoConversion exception.
            except NoConversion as expt:
                for msg in expt.msgs:
                    self.logger.warning(
                        "variable {}: {}".format(
                            len(self.variables) + 1, msg))
            else:
                # add converted variable if needed and conversion is possible
                # make copies of value and flag lists, otherwise the values
                # of the original variable gets converted as well
                self._add_variable_nondomain(
                    id, metadata, list(values), [[x for x in f] for f in flags],
                    1, is_hex=is_hex)

    def _convert_variable_output_new(self):
        """
        Adds one variable to file if conversion is needed.
        This is a new experimental implementation for files without ebas domain.
        This can in principle also be used for domain export.
        TODO: retire the old _convert_variable_output method
        Parameters:
            None
        Returns:
            None
        """
        regime = self.get_meta_for_var(-1, 'regime')
        matrix = self.get_meta_for_var(-1, 'matrix')
        comp_name = self.get_meta_for_var(-1, 'comp_name')
        unit = self.get_meta_for_var(-1, 'unit')
        try:
            vol_std_temp = float(self.get_meta_for_var(-1, 'vol_std_temp'))
        except (ValueError, TypeError):
            vol_std_temp = None
        try:
            vol_std_pressure = float(
                self.get_meta_for_var(-1, 'vol_std_pressure'))
        except (ValueError, TypeError):
            vol_std_pressure = None
        try:
            unit_convert = UnitConvert()
            (conv_obj, reset_stdcond) = unit_convert.export_conv_params(
                regime, matrix, comp_name, unit, vol_std_pressure, vol_std_temp)
        except NoConversion as expt:
            for msg in expt.msgs:
                self.logger.warning(
                    "variable {}: {}".format(
                        len(self.variables) + 1, msg))
            return
        if self.__class__.LAZY_READ:
            # fake the conversion (it should be delayed in the lazy read object)
            # TODO: we use hardcoded 4 decimals for now, are there better ways?
            conv_obj.convert_data([1.0001, 1.0002])
            self.variables[-1].values_.conversion_functions.append(
                conv_obj.convert_data)
        else:
            # convert the values right away:
            conv_obj.convert_data(self.variables[-1].values_)
        cnvstr = conv_obj.conversion_string()
        self.logger.info(
            "variable {}: Componment '{}', converting unit {}.".format(
                len(self.variables) + 1, comp_name, cnvstr))
        conv_remark = "Data converted on export from EBAS {}.".format(
            cnvstr)

        # correct uncertainty:
        uncert = self.get_meta_for_var(-1, 'uncertainty')
        if uncert and uncert[1] == unit:
            origval = uncert[0]
            if conv_obj.rounding is None:
                # rounding needs to be reset after conversion
                reset = True
            else:
                reset = False
            value_list = [origval]
            conv_obj.convert_data(value_list)
            newval = value_list[0]
            self.variables[-1].metadata.uncertainty = (newval, conv_obj.to_unit)
            cnvstr = conv_obj.conversion_string(from_val=origval,
                                                to_val=newval)
            self.logger.info(
                "variable {}: converting 'Measurement uncertainty' for "
                "component {} {}.".format(len(self.variables) + 1,
                                          comp_name, cnvstr))
            conv_remark += " Measurement uncertainty converted {}.".format(
                cnvstr)
            if reset:
                conv_obj.rounding = None  # reset the rounding

        # correct detection limit:
        detect = self.get_meta_for_var(-1, 'detection_limit')
        if detect and detect[1] == unit:
            origval = detect[0]
            if conv_obj.rounding is None:
                # rounding needs to be reset after conversion
                reset = True
            else:
                reset = False
            value_list = [origval]
            conv_obj.convert_data(value_list)
            newval = value_list[0]
            self.variables[-1].metadata.detection_limit = (newval,
                                                           conv_obj.to_unit)
            cnvstr = conv_obj.conversion_string(from_val=origval, to_val=newval)
            self.logger.info(
                "variable {}: converting 'Detection limit' for component {} {}."
                .format(len(self.variables) + 1, comp_name,
                        cnvstr))
            conv_remark += " Detection limit converted {}.".format(cnvstr)
            if reset:
                conv_obj.rounding = None  # reset the rounding

        # correct upper range limit:
        upper = self.get_meta_for_var(-1, 'upper_range_limit')
        if upper and upper[1] == unit:
            origval = upper[0]
            if conv_obj.rounding is None:
                # rounding needs to be reset after conversion
                reset = True
            else:
                reset = False
            value_list = [origval]
            conv_obj.convert_data(value_list)
            newval = value_list[0]
            self.variables[-1].metadata.upper_range_limit = (newval,
                                                             conv_obj.to_unit)
            cnvstr = conv_obj.conversion_string(from_val=origval, to_val=newval)
            self.logger.info(
                "variable {}: converting 'Upper range limit' for component "
                "{} {}." .format(len(self.variables) + 1,
                                 comp_name, cnvstr))
            conv_remark += " Upper range limit {}.".format(cnvstr)
            if reset:
                conv_obj.rounding = None  # reset the rounding

        # correct QA bias and variability:
        for qanum in self.get_qa_numbers():
            qa_ = self.get_qa_by_number(qanum, -1)
            if 'qa_bias' in qa_ and qa_.qa_bias and qa_.qa_bias[1] == unit:
                if conv_obj.rounding is None:
                    # rounding needs to be reset after conversion
                    reset = True
                else:
                    reset = False
                origval = qa_.qa_bias[0]
                value_list = [origval]
                conv_obj.convert_data(value_list)
                newval = value_list[0]
                qa_.qa_bias = (newval, conv_obj.to_unit)
                cnvstr = conv_obj.conversion_string(from_val=origval,
                                                    to_val=newval)
                self.logger.info(
                    "variable {}: converting 'QA{} bias' for component "
                    "{} {}." .format(
                        len(self.variables) + 1,
                        str(qanum) if qanum == -1 else '',
                        comp_name, cnvstr))
                conv_remark += " QA{} bias {}.".format(
                    str(qanum) if qanum == -1 else '', cnvstr)
                if reset:
                    conv_obj.rounding = None  # reset the rounding
            if 'qa_variability' in qa_ and qa_.qa_variability and \
                    qa_.qa_variability[1] == unit:
                if conv_obj.rounding is None:
                    # rounding needs to be reset after conversion
                    reset = True
                else:
                    reset = False
                origval = qa_.qa_variability[0]
                value_list = [origval]
                conv_obj.convert_data(value_list)
                newval = value_list[0]
                qa_.qa_variability = (newval, conv_obj.to_unit)
                cnvstr = conv_obj.conversion_string(from_val=origval,
                                                    to_val=newval)
                self.logger.info(
                    "variable {}: converting 'QA{} variability' for component "
                    "{} {}." .format(
                        len(self.variables) + 1,
                        str(qanum) if qanum == -1 else '',
                        comp_name, cnvstr))
                conv_remark += " QA{} variability {}.".format(
                    str(qanum) if qanum == -1 else '', cnvstr)
                if reset:
                    conv_obj.rounding = None  # reset the rounding

        # correct metadata:
        self.variables[-1].metadata.unit = conv_obj.to_unit
        if reset_stdcond:
            self.variables[-1].metadata.vol_std_pressure = reset_stdcond[0]
            self.variables[-1].metadata.vol_std_temp = reset_stdcond[1]
        oldcomment = self.get_meta_for_var(-1, 'comment')
        if oldcomment:
            conv_remark = oldcomment + " -- " + conv_remark
        self.variables[-1].metadata.comment = conv_remark

    def error(self, msg, lnum=None, counter_increase=1, prefix=''):
        """
        Error handling: Error will be logged, counter incremented.
        Parameters:
            msg        error message
            lnum       line number, optional (only if file is related to a
                       physical file (read))
            counter_incrrease
                       increase the file objects error counter by n
                       (default 1, other values used by message condenser)
            prefix     prefix message, comes before line number
        Returns:
            None
        """
        self.errors += counter_increase
        if lnum is not None:
            msg = u"line {}: {}".format(lnum, msg)
        self.logger.error(prefix + msg)

    def warning(self, msg, lnum=None, counter_increase=1, prefix=''):
        """
        Warning will be logged, counter incremented.
        Parameters:
            msg         warning message
            lnum        line number, optional (only if file is related to a
                        physical file (read))
            counter_incrrease
                       increase the file objects error counter by n
                       (default 1, other values used by message condenser)
            prefix     prefix message, comes before line number
        Returns:
            None
        """
        self.warnings += counter_increase
        if lnum is not None:
            msg = u"{}line {}: {}".format(prefix, lnum, msg)
        self.logger.warning(prefix + msg)

    def gen_filename(self, createfiles=False, destdir=None, extension=""):
        """
        Generates a file name according to NILU file name convention.
        The file name is created according to objects metadata, and the
        resulting filename is also set as metadata attribute.

        If parameter createfiles is set to True, the filename is also tested for
        uniqueness. If needed, _dupN is added (where N is an ascending integer)

        Parameter:
            createfiles   write to physical file?
            destdir       destination directory path for files
            extension     file name extension
        Return:
            None
        """
        def _add(elem):
            if isvalid(elem):
                return elem
            return ''

        if isvalid(self.metadata.doi) and self.metadata.doi[1]:
                # DOI part number is set
                # use doi + part number, fall back to dup if exists
                from ebas.domain.entities.do import DOI_PREFIX
                # import here, to make ebas-io independent of domain
                fname = '{}_part{:02.0f}'.format(
                    self.metadata.doi[0].replace(DOI_PREFIX, ''),
                    self.metadata.doi[1])
        elif isvalid(self.metadata.doi) and self.metadata.doi[0]:
                # use the doi as file name, fallback to _dup if it exists
                from ebas.domain.entities.do import DOI_PREFIX
                # import here, to make ebas-io independent of domain
                fname = self.metadata.doi[0].replace(DOI_PREFIX, '')
        else:
            fi_ref = ''
            lev = ''
            startdate = ''
            revdate = ''
            if isvalid(self.metadata.lab_code) and \
               isvalid(self.metadata.instr_name):
                fi_ref = self.metadata.lab_code + '_' + self.metadata.instr_name
                # TODO: temporary fix, to avoid '/' in filenames.
                # Needs final fix: - change existing FI_REF with /
                #                  - change DB constraint
                #                  - change input checks
                fi_ref = fi_ref.replace('/', '-')
            if isvalid(self.metadata.datalevel):
                lev = 'lev' + self.metadata.datalevel
            if isvalid(self.metadata.startdate):
                startdate = self.metadata.startdate.strftime("%Y%m%d%H%M%S")
            if isvalid(self.metadata.revdate):
                revdate = self.metadata.revdate.strftime("%Y%m%d%H%M%S")
    
            fname = _add(self.metadata.station_code) + '.' +\
                startdate + '.' +\
                revdate + '.' +\
                _add(self.metadata.instr_type) + '.' +\
                _add(self.metadata.comp_name) + '.' +\
                _add(self.metadata.matrix) + '.' +\
                _add(self.metadata.period) + '.' + \
                _add(self.metadata.resolution) + '.' + \
                fi_ref + '.' +\
                _add(self.metadata.method) + '.' +\
                lev
        testname = fname + extension
        if createfiles:
            if destdir is None:
                destdir = '.'
            i = 1
            while os.path.exists(os.path.join(destdir, testname)):
                testname = fname + '_dup{0}'.format(i) + extension
                i += 1
        self.metadata.filename = testname

    def setup_ebasmetadata(self, datadef, metadata_options):
        """
        Set up the ebasmetadata structure depending on format, datadef, and
        metadata options.
        Parameters:
            datadef    data definition (EBAS_1 or EBAS_1.1)
            metadata_options
                       options for output (bitfield):
                       EBAS_IOMETADATA_OPTION_SETKEY
        Returns
            None
        """
        # must be implemented here, because ebasmetadata can't be imported in
        # ..base
        self.metadata.datadef = datadef
        self.internal.ebasmetadata = EbasMetadata(
            self.metadata.datadef, self.__class__.IOFORMAT,
            data_level=self.metadata.datalevel,
            metadata_options=metadata_options)

    def set_default_metadata(self):
        """
        Sets some default metadata (non mandatory metadata elements which have
        a defined default.
        Is used both, for import and export.
        Parameters:
            None
        Returns:
            None
        """
        # some metadata must be set strictly for the whole file
        # make sure those are not set in any variable:
        reset_meta = ['timezone', 'creation_time']
        for var in self.variables:
            for meta in reset_meta:
                if meta in var.metadata:
                    del var.metadata[meta]

        if not self.metadata.timezone:
            self.metadata.timezone = 'UTC'
        if not self.metadata.regime:
            self.metadata.regime = 'IMG'
        now = datetime.datetime.utcnow()
        if not self.metadata.creation_time:
            self.metadata.creation_time = now
        if not self.metadata.revdate:
            self.metadata.revdate = now
        if not self.metadata.platform_code and self.metadata.station_code:
            self.metadata.platform_code = self.metadata.station_code[0:6] + 'S'
        if self.metadata.statistics is None:
            self.metadata.statistics = 'arithmetic mean'

    def get_meta_for_var(self, vnum, elem):
        """
        Get the applicable metadata element for a specific variable.
        (First lookup file metadata, then override with var metadata)
        Parameters:
            vnum   variable index
            elem   metadata element needed
        Returns:
            metadata elemnt value
        """
        res = None
        if elem in self.metadata:
            res = self.metadata[elem]
        if elem in self.variables[vnum].metadata:
            res = self.variables[vnum].metadata[elem]
        return res

    def get_characteristics_for_var(self, vnum):
        """
        Get all characteristics for a specific variable.
        (First lookup file metadata, then override with var metadata)
        Parameters:
            vnum   variable index
            elem   metadata element needed
        Returns:
            metadata elemnt value
        """
        ret = {}
        if self.metadata.characteristics:
            for cha in self.metadata.characteristics:
                if cha.CT_DATATYPE == 'CHR':
                    ret[cha.CT_TYPE] = cha.DC_VAL_CHR
                elif cha.CT_DATATYPE == 'DBL':
                    ret[cha.CT_TYPE] = cha.DC_VAL_DBL
                else:
                    ret[cha.CT_TYPE] = cha.DC_VAL_INT
        if 'characteristics' in self.variables[vnum].metadata and \
           self.variables[vnum].metadata.characteristics:
            for cha in self.variables[vnum].metadata.characteristics:
                if cha.CT_DATATYPE == 'CHR':
                    ret[cha.CT_TYPE] = cha.DC_VAL_CHR
                elif cha.CT_DATATYPE == 'DBL':
                    ret[cha.CT_TYPE] = cha.DC_VAL_DBL
                else:
                    ret[cha.CT_TYPE] = cha.DC_VAL_INT
        return ret

    def add_var_characteristics(self, vnum, ct_type, value):
        """
        Add a characteristic for a variable.
        Parameters:
            vnum      variable index
            ct_type   characteristics type (tag)
            value     value for the characteristic
        """
        if 'characteristics' not in self.variables[vnum].metadata:
            self.variables[vnum].metadata.characteristics = \
                DatasetCharacteristicList()
        ft_type = self.get_meta_for_var(vnum, 'instr_type')
        co_comp_name = self.get_meta_for_var(vnum, 'comp_name')
        data_level = self.get_meta_for_var(vnum, 'datalevel')
        self.variables[vnum].metadata.characteristics.add(
            ct_type, value, ft_type, co_comp_name, data_level=data_level)

    def get_metadata_list_per_var(self, element, string=False):
        """
        Generates a list for one metadata element (one list element per variable
        in file).
        Use variable metadata if possible, else global metadata.
        
        !!! EbasJoinedFile: (hidden catch)
        This method works only for metadata elements that are duplicated to the
        joined file (i.e. elements that are considered to be common) in the join
        method
         
        Parameter:
            element     metadata element (string)
        Returns:
            lst (one element per variable in file, None for empty)
        """
        lst = []
        for vnum in range(len(self.variables)):
            if element in self.variables[vnum].metadata:
                litem = self.variables[vnum].metadata[element]
            else:
                litem = self.metadata[element]
            if string:
                litem = str(litem)
            lst.append(litem)
        return lst

    def get_metadata_set(self, element, string=False, exclude_aux=False):
        """
        Generates a set of different values for one metadata element (of each
        variable).
        This method is meant to give "all different" values for a metadata
        element, this behavior is also overridden in the EbasJoinedFile object.
        Parameter:
            element     metadata element (string)
            string      whether the elements should be reresented as str
            exclude_aux
                        do not report metadata for auxiliary variables
        Returns:
            list (list with unique elements, i.e. set)
        """
        # Because metadata values can be unhashable objects (dict, DataObject),
        # this method must be implemented as a list, not as a set.
        set_ = []
        _str = lambda x: str(x) if string else x

        def _add(x):
            if x is not None and _str(x) not in set_: set_.append(_str(x))

        for vnum in range(len(self.variables)):
            if exclude_aux and self.is_auxiliary(vnum):
                continue
            if isinstance(element, tuple):
                # element is an iterator -- list combinations
                res = []
                for atom in element:
                    res.append(self.get_meta_for_var(vnum, atom))
                _add(res)
            else:
                # else, element is a single metadata key
                res = self.get_meta_for_var(vnum, element)
                if res is not None:
                    _add(res)
        return set_

    def is_precip_concentration(self, vnum):
        """
        Check if the dataset is a precipitation concentration component (one
        that needs precipitation amount)
        Parameters:
            vnum    variable number
        Returns:
            True/False
        """
        return is_precip_concentration(self.get_meta_for_var(vnum, 'matrix'),
                                       self.get_meta_for_var(vnum, 'comp_name'))

    def is_precip_amount(self, vnum):
        """
        Check if the dataset is a precipitation amount component
        Parameters:
            vnum    variable number
        Returns:
            True/False
        """
        return is_precip_amount(self.get_meta_for_var(vnum, 'matrix'),
                                self.get_meta_for_var(vnum, 'comp_name'))

    def is_auxiliary(self, vnum):
        """
        Check if the dataset is to be considered "auxiliary data".
        Parameters:
            vnum    variable number
        Returns:
            True/False
        """
        return is_auxiliary(self.get_meta_for_var(vnum, 'matrix'),
                            self.get_meta_for_var(vnum, 'comp_name'))

    def get_submitter_emails(self):
        """
        Get the email addresses of all data submitters.
        Parameters:
            None
        Returns:
            list of email addresses
        """
        ret = set()
        for ps_ in self.metadata.submitter:
            if 'PS_EMAIL' in ps_ and ps_['PS_EMAIL']:
                ret.add(ps_['PS_EMAIL'])
        return list(ret)


    def get_qa_numbers(self):
        """
        Get a all used QA numbers in the file.
        Sorted by order in main metadata, then by order in each variable as
        they appear in the file.
        Parameters:
            None
        Returns:
            List of integers
        """
        ret_list = []
        if 'qa' in self.metadata and self.metadata.qa is not None:
            for qa_ in self.metadata.qa:
                if qa_['qa_number'] not in ret_list:
                    ret_list.append(qa_['qa_number'])
        for var in self.variables:
            if 'qa' in var.metadata and var.metadata.qa is not None:
                for qa_ in var.metadata.qa:
                    if qa_['qa_number'] not in ret_list:
                        ret_list.append(qa_['qa_number'])
        return ret_list

    def get_qa_by_number(self, qa_number, var_index):
        """
        Get the index for the qa element with a specific qa_number.
        Parameters:
            qa number     number of QA block
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            qa element with the matching qa_number
            self._empty_qa() if not present and var_indes is None
            empty DataObject if not present and var_index is not None
        Raises:
            RuntimeError if more then one list element matches the qa_number
        """
        if var_index is None:
            metadata = self.metadata
        else:
            metadata = self.variables[var_index].metadata
        if 'qa' not in metadata or metadata.qa is None:
            return self._empty_qa() if var_index is None else DataObject()
        qa_list = [qa for qa in metadata.qa if qa['qa_number'] == qa_number]
        if len(qa_list) > 1:
            # this should never happen
            raise RuntimeError('QA metadata qa_number/index error')
        if len(qa_list) == 0:
            return self._empty_qa() if var_index is None else DataObject()
        return qa_list[0]
    
    def get_qa_for_var(self, vnum):
        """
        Returns a list with all integrated qa metadata foe one variable.
        (Fileglogal / per varaible settings are merged)
        Parameters:
            vnum    variable number
        Returns:
            generator of the merged qa dictionaries.
            ! Empty qa dictionaries are skipped !
        """
        for qanum in self.get_qa_numbers():
            qa_ = self.get_qa_by_number(qanum, None)
            if qa_:
                qa_ = qa_.copy()  # need to copy because of update below!
            else:
                qa_ = {}
            var_qa = self.get_qa_by_number(qanum, vnum)
            if var_qa:
                qa_.update(var_qa)
            if not self._is_empty_qa(qa_):
                yield qa_

    def _empty_qa(self):
        """
        Generate an empty qa dictionary for global masterdata (all keys, but all
        values are None).
        """
        return DataObject({x["key"]: None
                           for x in self.internal.ebasmetadata.metadata
                           if "QA_block" in x and x["QA_block"]})

    def _is_empty_qa(self, qa_):
        """
        Check if qa dictionary is empty.
        Returns:
           True if empty, else Flase
        """
        return not any([True for key in qa_.keys()
                        if key != 'qa_number' and qa_[key] is not None])

    def set_qa(self, key, value, qa_number, var_index):
        """
        Set a metadata value for a QA metadata element.
        Check if element has been set before (log error if set already)
        Parameters:
            key           metadata key
            value         value to be set
            qa number     number of QA block
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            None
        """
        if var_index is None:
            metadata = self.metadata
        else:
            metadata = self.variables[var_index].metadata
        qa_ = self.get_qa_by_number(qa_number, var_index)
        # set:
        if 'qa' not in metadata or metadata.qa is None:
            metadata.qa = []
        if qa_ not in metadata.qa:
            # qa_ is a new element, set values and append
            # add the current qQA nuber and the current key/value pair:
            qa_.qa_number = qa_number
            qa_[key] = value
            # add the new QA element to the list
            metadata.qa.append(qa_)
        else:
            qa_[key] = value

    def unset_qa(self, key, qa_number, var_index):
        """
        Removes a metadata value for a QA metadata element.
        Unset in case of a variable is different from setting to None!
        Parameters:
            key           metadata key
            qa number     number of QA block
            var_index     >0 if variable specific (= from VNAME),
                          None if global (from NCOM block)
        Returns:
            None
        """
        if var_index is None:
            metadata = self.metadata
        else:
            metadata = self.variables[var_index].metadata
        qa_ = self.get_qa_by_number(qa_number, var_index)
        # unset:
        if 'qa' in metadata or metadata.qa is not None and key in metadata.qa:
            del qa_[key]

    def values_without_flags(self, vnum):
        """
        Modifies the values of a timeseries in case it should be used
        without flag information.
        Parameters:
            vnum   variable index
        Modifications:
            values with invalid flag -> MISSING
            values with flag 781 -> value/2.0
        This will maybe hgave to be generalized (moved out of the nasa_ames
        module when other output formats are implemented.
        """
        ret = []
        values = self.variables[vnum].values_
        flags = self.variables[vnum].flags
        for i in range(len(values)):
            (_, invalid, missing, _) = get_flag_summary(flags[i])
            if invalid or missing:
                ret.append(None)
            elif 781 in flags[i] and values[i]:
                ret.append(values[i]/2.0)
            else:
                ret.append(values[i])
        return ret

    def find_variables(self, meta):
        """
        Finds variables in the file which match certain metadata criteria.
        Parameters:
            meta      metadata elements for lookup (dict)
        Returns:
            generator (variable numbers that match)
        """
        for i in range(len(self.variables)):
            if meta:
                for elem in meta.keys():
                    skip = False
                    if elem == 'characteristics':
                        # special case, characteristics is a dict
                        char = self.get_characteristics_for_var(i)
                        for k in meta[elem].keys():
                            # If False in criteria, then the characteristic
                            # may not exist
                            # If True in criteria, then the characteristic must
                            # exist.
                            # Else, the characterisic must be equal the set
                            # value.
                            if ((meta[elem][k] is False and  k in char) or
                                (meta[elem][k] is True and  k not in char) or
                                ((meta[elem][k] is not False and
                                  meta[elem][k] is not True and
                                  (k not in char or meta[elem][k] != char[k])))):
                                skip = True
                                break
                        if skip:
                            break
                    else:
                        if meta[elem] != self.get_meta_for_var(i, elem):
                            skip = True
                            break
                if not skip:
                    yield i

    def find_variable(self, meta):
        """
        Finds exactly one specific variable in the file which matches certain
        metadata criteria.
        Parameters:
            meta      metadata elements for lookup (dict)
        Returns:
            variable number
        Raises:
            ValueError if no variable or more than one found
        """
        itr = self.find_variables(meta)
        try:
            ret = next(itr)
        except StopIteration:
            raise ValueError("no Variable matches criteria")
        try:
            next(itr)
        except StopIteration:
            return ret
        raise ValueError("more than one Variable match criteria")

    def match_variable(self, vnum, meta):
        """
        Check if variable vnum matches criteria meta.
        Parameters:
            vnum     variable number in file
            meta     metadata elements for lookup (dict)
        Returns:
            bool
        """
        if vnum in self.find_variables(meta):
            return True
        return False

    def find_sample_time_index(self, time):
        """
        Finds indexes in sample times that cover a given time or interval.
        Parameters:
            time    datetime.datetime - finding coverage for a point in time
                       or
                    (min, max) - finding coverage for an interval
        Returns:
            (min_index, max_index) or None
        """
        if isinstance(time, datetime.datetime):
            time = DatetimeInterval(time,
                                    time+datetime.timedelta(microseconds=1))
        elif not isinstance(time, DatetimeInterval):
            time = DatetimeInterval(*time)
        time_index = [i for i in range(len(self.sample_times))
                      if time.overlap(self.sample_times[i])]
        if time_index:
            return (time_index[0], time_index[-1])
        return None

    def msgref_vnum_lnum(self, vnum):  # pylint: disable=R0201
        # R0201: Method could be a function
        # --> will be overridden as an instance method.
        """
        Get info on variable number and line number for error messages.
        Default implementation, MUST be overridden by concrete file read
        classes.
        Default returns vnum as variable number an 1 as offset line number.
        Parameters:
            vnum    variable index in the file object
        Returns:
            (file_vnum, file_num) where:
                file_vnum: the real variable number in the physical file
                           (if there was a physical file read)
                           Variable 1 is the first variable after end_time
                file_lnum: the line number offset for the first data line in
                           the physical file (if there was a physical file read)
                file_metalnum: the line number reference that should be used for
                               metadata related messages. Default is None.
        """
        return (vnum+1, 1, None)

    def write_indexdb(self):
        """
        Writes indexdb entries for the io object.
        """
        if self.indexdb:
            self.indexdb.insert_file_obj(self)

    def uniform_time(self):
        """
        Checks if the timeseries is uniform.
        TU (uniform) if the same time difference between the start times.
        (Non necessarily the same as DX. DX is Nasa Ames (i.e. rounded float)
        DX can be != 0 if all differences (rounded to ndigits) are equal DX +-
        1 in the last digit (allow for rounding) 
        Parameters:
            None
        Returns:
            datetime.timedelta object if uniform
            timedelta(0) if not uniform
            None if less than 2 samples.
        """
        totaldiff = None
        for (time1, time2) in zip([time[0] for time in self.sample_times],
                                  [time[0] for time in self.sample_times][1:]):
            diff = time2 - time1
            if totaldiff and diff != totaldiff:
                return datetime.timedelta(0)
            elif not totaldiff:
                totaldiff = diff
        return totaldiff

    def title(self):
        """
        Get a human readable title for the file (depending on parameters and
        station.
        Parameters:
            None
        Returns:
            Title string
        """
        return title(
            [(self.get_meta_for_var(i, 'regime'), self.get_meta_for_var(i, 'matrix'), self.get_meta_for_var(i, 'comp_name'))
             for i in range(len(self.variables))],
            [self.metadata.station_name])

    def set_citation(self, metadata_options):
        """
        Calculate and set the citation metadata from other metadata.
        Parameters:
            metadata_options
                       options for output (bitfield):
        Returns:
            None
        Sets:
            citation
        """
        if not self.from_domain:
            # This file is not generated from the ebas domain.
            # Do not generate a citation string (e.g. submitted files to ebas)
            return
        # make sure citation is not set in any variable:
        for var in self.variables:
            if 'citation' in var.metadata:
                del var.metadata['citation']
        # Authors: join all data originators
        self.metadata.citation = ', '.join(
            ['{}{}'.format(
                ps.PS_LAST_NAME,
                (', ' + ps.PS_FIRST_NAME[0] + '.') if ps.PS_FIRST_NAME else '')
             for ps in self.metadata.originator])
        # Authors: join all project acronyms
        if self.metadata.projects:
            prj = ', '.join(self.metadata.projects)
        else:
            # This means, either different variable have different project lists
            # (can only happen when manually creating the file in ebas-io)
            # or, we are are a joined file, and the project list varies between
            # different metadata_intervals.
            # Both cases are handlesd well by union_projects.
            prj = ', '.join(self.union_projects())
        if self.metadata.citation and prj:
            self.metadata.citation += ', '
        self.metadata.citation += prj
        # Year of publication: from revision date
        if isvalid(self.metadata.revdate):
            self.metadata.citation += ', {}'.format(self.metadata.revdate.year)
        self.metadata.citation += ', ' + self.title()
        self.metadata.citation += ', data hosted by EBAS at NILU'
        if self.metadata.doi:
            self.metadata.citation += ', DOI: {}'.format(
                self.metadata.doi[0])
        elif self.metadata.doi_list:
            self.metadata.citation += ', Part of DOI: {}'.format(
                ', '.join([x for x in self.metadata.doi_list]))

    def union_projects(self):
        """
        Get a union of all projects in the file.
        (Overridden in EbasJoinedFile for adequate handling of joined files)
        Parameters:
            None
        Returns:
            list of project acronyms
        """
        return sorted(
            {prj
             for vnum in range(len(self.variables))
             for prj in self.get_meta_for_var(vnum, 'projects')})

    def set_timespec_metadata(self):
        """
        Calculate and set all time specific metadata from sample times.
        Returns:
            None
        Sets:
            type TU/TI
            timeref, timeoffset
            startdate
        """
        # make sure none of the metadata set here is set in any variable:
        reset_meta = ['period', 'type', 'timeref', 'startdate']
        for var in self.variables:
            for meta in reset_meta:
                if meta in var.metadata:
                    del var.metadata[meta]

        res = estimate_resolution_code(self.sample_times)
        if res or not self.metadata.resolution:
            # set resolution code only if it can be calculated, else keep
            # manual setting if there is one
            self.metadata.resolution = res
        # set period code
        self.metadata.period = estimate_period_code(self.sample_times[0][0],
                                                    self.sample_times[-1][1])
        # set type (TU/TI)
        diff = self.uniform_time()
        if diff is None:
            # Less than 2 samples, type is undefined.
            # If types was set already, leave it (user might want this)
            # If nothing is set, set TI
            if self.metadata.type not in ("TU", "TI"):
                self.metadata.type = "TI"
        elif diff == datetime.timedelta(0):
            self.metadata.type = "TI"
        else:
            self.metadata.type = "TU"

        # do not use timeref on export anymore!
        self.metadata.timeref = None
        self.internal.timeoffset = datetime.timedelta(seconds=0)

        self.metadata.startdate = self.sample_times[0][0]

    def join(self, other):  # @UnusedVariable  pylint: disable=W0613, R0201
        # UnusedVariable: only in default implementation
        # W0613: Unused argument 'other': only in default implementation
        # R0201: Method could be a  function: only in default implementation
        """
        Join self with other if possible.
        Default implementation: do not join
        Parameters:
            other    other EbasIO object
        Returns
            New, joined EbasIO object
            None (no join possible)
        """
        return None

    def check(  # pylint: disable=R0913
            # R0913  Too many arguments
            self, ignore_rescode=False, ignore_revdate=False,
            ignore_parameter=False, ignore_sampleduration=False,
            ignore_identicalvalues=False,
            ignore_flagconsistency=False, fix_flagconsistency=False,
            ignore_nodata=False,
            ignore_valuecheck=False, ignore_templatecheck=False,
            fix_overlap_set_start=False,
            fix_bc211=False):
        """
        Performs a full check of the IO object.
        Parameter:
            ignore_rescode    ignore rescde errors (downgraded to warning)
            ignore revdate    ignore revdate errors (downgrade to warning)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
            ignore_identicalvalues
                              ignore errors related to all values of one
                              variable being equal (e.g. all data missing for
                              one variable, all values 0.0 or all values any
                              other constant value).
            ignore_flagconsistency
                              ignore errors regarding flag consistency and
                              flag/value consitency
            fix_flagconsistency
                              ignore errors regarding flag consistency and
                              flag/value consitency; additionally fix problems
                              if possible
            ignore_nodata     the object is expected to not contain any data
                              (ie.g. read with skip_data)
            ignore_valuecheck ignore value checks (boundaries and spikes)
            ignore_templatecheck ignore template checks
            fix_overlap_set_start
                              instead of raising an error in case of overlaps,
                              set the previous endtime to start time
            fix_bc211         flag boundary check violations with flag 211
        """
        self.check_metadata(
            ignore_rescode=ignore_rescode, ignore_revdate=ignore_revdate,
            ignore_parameter=ignore_parameter,
            ignore_sampleduration=ignore_sampleduration)
        self.check_data(ignore_identicalvalues=ignore_identicalvalues,
                        ignore_nodata=ignore_nodata,
                        ignore_flagconsistency=ignore_flagconsistency,
                        fix_flagconsistency=fix_flagconsistency,
                        ignore_valuecheck=ignore_valuecheck,
                        fix_overlap_set_start=fix_overlap_set_start,
                        fix_bc211=fix_bc211)
        try:
            template = get_template(
                self, ignore_templatecheck=ignore_templatecheck)
        except NoTemplate:
            self.warning('No applicable template found')
        else:
            self.logger.info("found template {}".format(template.TEMPLATE_NAME))
            template.checkfile()

    def check_metadata(
            self, ignore_rescode=False, ignore_revdate=False,
            ignore_parameter=False):
        """
        Abstract in the base class, implemented in EbasFileCheckMetadata.
        Performs a check of the metadata of the object.
        Parameter:
            ignore_rescode    ignore rescde errors (downgraded to warning)
            ignore revdate    ignore revdate errors (downgrade to warning)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
        """
        raise NotImplementedError

    def check_data(self, ignore_identicalvalues=False,
                   ignore_flagconsistency=False, fix_flagconsistency=False,
                   ignore_nodata=False,
                   ignore_valuecheck=False, fix_overlap_set_start=False,
                   fix_bc211=False):
        """
        Abstract in the base class, implemented in EbasFileCheckData.
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
                    instead of raising an error in case of overlaps,
            fix_bc211         flag boundary check violations with flag 211
        """
        raise NotImplementedError

    def update_metadata(self, meta, vnum=None):
        """
        Merges the fileglobal or variable specific metadata with a dictionary.
        !!! This merges metadata key wise, e.g. no special trearment for "qa".
        !!! --> "qa" is taken as a whole.
        Parameters:
            vnum    variable number (if variable specific metadata)
            meta    dictionary with metadata to be updated
        Returns:
            None
        """
        if vnum is None:
            mymeta = self.metadata
        else:
            mymeta = self.variables[vnum].metadata
        for key in meta.keys():
            if key not in mymeta or mymeta[key] != meta[key]:
                # updat needed
                if isinstance(meta[key], dict):
                    # Make DataDict from all dict like objects
                    mymeta[key] = DataObject(meta[key])
                elif isinstance(meta[key], list):
                    # Make list of Datadict from all list of dict like objects
                    mymeta[key] = list()
                    for elem in meta[key]:
                        if isinstance(elem, dict):
                            mymeta[key].append(DataObject(elem))
                        else:
                            mymeta[key].append(elem)
                else:
                    mymeta[key] = meta[key]

    def get_all_meta_for_var(self, vnum):
        """
        Get all metadtaa for one variable (merge global and variable specific).
        """
        res = DataObject()
        for key in set(self.metadata.keys() + \
                       self.variables[vnum].metadata.keys()):
            if key == 'qa':
                res[key] = [x for x in self.get_qa_for_var(vnum)]
            else:
                res[key] = self.get_meta_for_var(vnum, key)
        return res
        
        
