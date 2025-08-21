"""
Base classes for (file) I/O.

$Id: read.py 2747 2021-11-24 13:56:00Z pe $
"""

import re
from collections import defaultdict
from .base import EbasFileBase, isvalid
from nilutility.datatypes import DataObject
from ebas.domain.basic_domain_logic.unit_convert import UnitConvert, \
    NoConversion


class EbasFileRead(EbasFileBase):
    """
    Partial class for EbasFile (Base class for file objects).
    This part handles generic reading.
    """

    READ_EXCEPTION = NotImplementedError  # must be set in the concrete class

    def read(self, filename,
             ignore_rescode=False,
             ignore_revdate=False, ignore_parameter=False,
             ignore_sampleduration = False,
             ignore_identicalvalues=False,
             ignore_flagconsistency=False, fix_flagconsistency=False,
             ignore_valuecheck=False, ignore_templatecheck=False,
             skip_data=False, skip_unitconvert=False, skip_variables=None,
             fix_overlap_set_start=False, fix_bc211=False,
             **kwargs):
        """
        Reads a NASA Ames files to NasaAmes object.
        Parameters:
            filename          path and filename
            ignore_rescode    ignore rescde errors (downgraded to warning)
            ignore revdate    ignore revdate errors (downgrade to warning)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
            ignore_sampleduration
                              ignore errors related to the sample duration
                              metadata not being consistent with the data
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
            ignore_valuecheck ignore value checks (boundaries and spikes)
            ignore_templatecheck ignore template checks
            skip_data         skip reading of data (speedup, if data are not
                              needed at application level). First and last line
                              are read. (Tjis is just passed to NasaAmes1001)
            skip_unitconvert  skips the automatic unit conversion on input
                              this is needed when a file with non standard units
                              should be processed without importing it into the
                              ebas.domain.
            skip_variables    list of variable numbers to be skipped (variabzle
                              numbers start with 1 for the first variable after
                              end_time)
            **kwargs          extra arguments for read_nasa_ames (e.g. encoding,
                              ignore_numformat, ignore_dx0)
            fix_overlap_set_start
                              instead of raising an error in case of overlaps,
                              set the previous end time to start time
            fix_bc211         flag boundary check violations with flag 211
        Returns:
            None
        Raises:
            IOError (from builtin, file open)
            EbasNasaAmesReadError
        """
        # initialize temporary attributes for reading
        self.internal.read_tmp = DataObject(
            var_skipped=[], var_num=[], vmiss=[], hea_error=False,
            revdate_read=False)

        self._read(
            filename, ignore_rescode=ignore_rescode,
            ignore_revdate=ignore_revdate, ignore_parameter=ignore_parameter,
            ignore_sampleduration=ignore_sampleduration,
            skip_data=skip_data,
            skip_variables=skip_variables, **kwargs)

        if len(self.sample_times) > 0:
            self.internal.read_tmp.timebounds = self.sample_times[0] + \
                                                self.sample_times[-1]
        else:
            self.internal.read_tmp.timebounds = None
        # skip data cleanup: now throw away first and last sample
        if skip_data:
            self.sample_times = []
            for var in self.variables:
                var.values_ = []
                var.flags = []

        self.set_default_metadata()  # must be before convert: regime needed!

        if not skip_unitconvert:
            # Unit convert must happen before check.
            # Otherwise parameter check would fail. 
            self.convert_variables_input()

        # check must be done in the end
        # e.g. unit convert on input changes unit, so that parameter/unit is
        # allowed
        self.check(ignore_rescode=ignore_rescode,
                   ignore_revdate=ignore_revdate,
                   ignore_parameter=ignore_parameter,
                   ignore_sampleduration=ignore_sampleduration,
                   ignore_identicalvalues=ignore_identicalvalues,
                   ignore_flagconsistency=ignore_flagconsistency,
                   fix_flagconsistency=fix_flagconsistency,
                   # ignore error about no data, when skipped:
                   ignore_nodata=skip_data,
                   ignore_valuecheck=ignore_valuecheck,
                   ignore_templatecheck=ignore_templatecheck,
                   fix_overlap_set_start=fix_overlap_set_start,
                   fix_bc211=fix_bc211)

        if self.errors > 0:
            self.logger.info("Exiting because of previous errors")
            raise self.__class__.READ_EXCEPTION(
                "{} Errors, {} Warnings".format(self.errors,
                                                self.warnings))

    def _read(self, filename,
              ignore_rescode=False,
              ignore_revdate=False, ignore_parameter=False, skip_data=False,
              skip_unitconvert=False, skip_variables=None, **kwargs):
        """
        Must be implemented in derived classes for the respective data format.
        Parameters:
            The implementation in derived classes can add parameters up to their
            neds. However, thoseparameters MUST be taken:

            filename          path and filename
            ignore_rescode    ignore rescde errors (downgraded to warning)
            ignore revdate    ignore revdate errors (downgrade to warning)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
            skip_data         skip reading of data (speedup, if data are not
                              needed at application level). First and last line
                              are read. (Tjis is just passed to NasaAmes1001)
            skip_unitconvert  skips the automatic unit conversion on input
                              this is needed when a file with non standard units
                              should be processed without importing it into the
                              ebas.domain.
            skip_variables    list of variable numbers to be skipped (variabzle
                              numbers start with 1 for the first variable after
                              end_time)
            **kwargs          extra arguments for read_nasa_ames (e.g. encoding,
                              ignore_numformat, ignore_dx0)
            Returns:
                None
            Raises:
                IOError (from builtin, file open)
                EbasNasaAmesReadError
        """
        raise NotImplementedError

    def convert_variables_input(self):
        """
        Convert variables on import (depending on component name, unit etc.
        E.g.: convert 'nitrogen_dioxide, nmol/mol' to
                      'nitrogen_dioxide, ug N/m3'
        Parameters:
            None
        Returns:
            None
        """
        self.internal.cvt_tmp = DataObject(
            global_dl_cand1=[], global_url_cand1=[], global_unc_cand1=[],
            global_qabias_cand1=defaultdict(list),
            global_qavariab_cand1=defaultdict(list),
            global_dl_cand2=[], global_url_cand2=[], global_unc_cand2=[],
            global_qabias_cand2=defaultdict(list),
            global_qavariab_cand2=defaultdict(list))
        for vnum in range(len(self.variables)):
            file_vnum, _, file_metalnum = self.msgref_vnum_lnum(vnum)
            regime = self.get_meta_for_var(vnum, 'regime')
            matrix = self.get_meta_for_var(vnum, 'matrix')
            comp_name = self.get_meta_for_var(vnum, 'comp_name')
            unit = self.get_meta_for_var(vnum, 'unit')
            std_pres = self.get_meta_for_var(vnum, 'vol_std_pressure')
            if not isinstance(std_pres, float):
                std_pres = None
            std_temp = self.get_meta_for_var(vnum, 'vol_std_temp')
            if not isinstance(std_temp, float):
                std_temp = None
            try:
                unit_convert = UnitConvert()
                (cvt, reset_stdcond) = unit_convert.import_conv_params(
                    regime, matrix, comp_name, unit, std_pres, std_temp)
            except NoConversion as expt:
                for msg in expt.msgs:
                    self.warning("variable {}: {}".format(
                        file_vnum, msg), lnum=file_metalnum)
            else:
                self._convert_variable_input(vnum, cvt)
                if reset_stdcond:
                    self.variables[vnum].metadata.vol_std_pressure = \
                        reset_stdcond[0]
                    self.variables[vnum].metadata.vol_std_temp = \
                        reset_stdcond[1]
        self._convert_global_metadata()

    def _check_convert_global_metadata(self, vnum, conv_obj):
        """
        Check if the global metadata detection limit (DL),
        upper range limit (URL) and uncertainty (UNC) can be unit converted
        with the same conversion as the variable vnum.
        This is the case, if the global parameter metadata are the same as the
        variable's, the global unit is the same as the variable's unit and the
        global DL, URL or UNC unit is also the same.
        In this case, the varaible's conversion object is a candidate for the
        conversion of global metadata DL, URL and UNC. The conversion of the
        global metadata is then performed by _convert_global_metadata().
        
        Parameters:
            vnum         variable number
            conv_obj     converison object
        Returns:
            None
        """
        regime = self.get_meta_for_var(vnum, 'regime')
        comp = self.get_meta_for_var(vnum, 'comp_name')
        matrix = self.get_meta_for_var(vnum, 'matrix')
        if self.metadata.regime == regime and \
           self.metadata.comp_name == comp and \
           self.metadata.matrix == matrix and \
           self.metadata.unit == conv_obj.from_unit:

            self.internal.cvt_tmp.global_unit = conv_obj.to_unit
            
            if 'uncertainty' in self.metadata and \
               isvalid(self.metadata.uncertainty) and \
               self.metadata.uncertainty[1] == conv_obj.from_unit:
                if "uncertainty" not in self.variables[vnum].metadata or \
                    self.metadata.uncertainty == \
                        self.variables[vnum].metadata.uncertainty:
                    # the global uncertainty will be used for this variable,
                    # so this is a first grade candidate (use the same rounding
                    # as for the variable:
                    self.internal.cvt_tmp.global_unc_cand1.append(conv_obj)
                else:
                    # the global uncertaionty is not used for this variable
                    # anyway it is a useable conversion candidate for global
                    # detection limit (with it's own rounding)
                    self.internal.cvt_tmp.global_unc_cand2.append(conv_obj)
            if 'detection_limit' in self.metadata and \
               isvalid(self.metadata.detection_limit) and \
               self.metadata.detection_limit[1] == conv_obj.from_unit:
                if "detection_limit" not in self.variables[vnum].metadata or\
                        self.metadata.detection_limit == \
                            self.variables[vnum].metadata.detection_limit:
                    # the global detection_limit will be used for this variable,
                    # so this is a first grade candidate (use the same rounding
                    # as for the variable:
                    self.internal.cvt_tmp.global_dl_cand1.append(conv_obj)
                else:
                    # the global detection_limit is not used for this variable
                    # anyway it is a useable conversion candidate for global
                    # detection limit (with it's own rounding)
                    self.internal.cvt_tmp.global_dl_cand2.append(conv_obj)
            if 'upper_range_limit' in self.metadata and \
               isvalid(self.metadata.upper_range_limit) and \
               self.metadata.upper_range_limit[1] == conv_obj.from_unit:
                if "upper_range_limit" not in self.variables[vnum].metadata or \
                        self.metadata.upper_range_limit == \
                            self.variables[vnum].metadata.upper_range_limit:
                    # the global UR limit will be used for this variable,
                    # so this is a first grade candidate (use the same rounding
                    # as for the variable:
                    self.internal.cvt_tmp.global_url_cand1.append(conv_obj)
                else:
                    # the global UR limit is not used for this variable
                    # anyway it is a useable conversion candidate for global
                    # detection limit (with it's own rounding)
                    self.internal.cvt_tmp.global_url_cand2.append(conv_obj)
            for qa_ in self.get_qa_for_var(vnum):
                if 'qa_bias' in qa_ and isvalid(qa_.qa_bias) and \
                        qa_.qa_bias[1] == conv_obj.from_unit:
                    varqa = self.get_qa_by_number(qa_.qa_number, vnum)
                    if 'qa_bias' not in varqa or varqa['qa_bias'] is None or \
                       varqa.qa_bias == qa_.qa_bias:
                        # the global qa bias will be used for this variable,
                        # so this is a first grade candidate (use the same
                        # rounding as for the variable:
                        self.internal.cvt_tmp.\
                            global_qabias_cand1[qa_.qa_number].append(conv_obj)
                    else:
                        # the global qa bias is not used for this variable
                        # anyway it is a useable conversion candidate for global
                        # detection limit (with it's own rounding)
                        self.internal.cvt_tmp.\
                            global_qabias_cand2[qa_.qa_number].append(conv_obj)
                if 'qa_variability' in qa_ and isvalid(qa_.qa_variability) and \
                       qa_.qa_variability[1] == conv_obj.from_unit:
                    varqa = self.get_qa_by_number(qa_.qa_number, vnum)
                    if 'qa_variability' not in varqa or \
                            varqa.qa_variability is None or \
                            varqa.qa_variability == qa_.qa_variability:
                        # the global qa variablility will be used for this
                        # variable, so this is a first grade candidate (use the
                        # same rounding as for the variable:
                        self.internal.cvt_tmp.\
                            global_qavariab_cand1[qa_.qa_number].append(
                                conv_obj)
                    else:
                        # the global qa variablility is not used for this
                        # variable anyway it is a useable conversion candidate
                        # for global detection limit (with it's own rounding)
                        self.internal.cvt_tmp.\
                            global_qavariab_cand2[qa_.qa_number].append(
                                conv_obj)

    def _convert_global_metadata(self):
        """
        Converts global metadata unit, uncertainty, detection limit and
        upper range limit.
        This is needed in those special cases:
            If the global metadata parameter and unit is set and the unit is
            converted for all variables, the global metadata remain with an
            invalid parameter/unit combination, which is a problem in
            check_param_unit() or the gloabal metadata.
            E.g. ozone file in nmol/mol, gloabl metadata ozone, nmol/mol, each
                 variable is ozone, nmol/mol.
                 After conversion, all valiables are ozone, ug/m3, but the
                 global parameter/unit check would fail.
            Once the global unit is converted accordingly, the check of global
            detection limit, upper range limit and uncertainty might fail, e.g.:
            ERROR   : Unit 'X' used for 'Detection limit' is inconsistent
                      with 'Unit' ('Y')

        to be documented in the code:
         - only when the global metadata is not needed anymore (i.e.
        all applicable variables have been converted and thus have got their
        own, variable specific metadata element.
        If the global metadata still applies to any variable, the variable has
        obviously not been converted and the global metadata is needed as was.
        This might lead to resulting errors in consistency within the global
        metadata...
        Parameters:
            conv_obj     conversion object
        Returns:
            None
        """
        if 'global_unit' in self.internal.cvt_tmp:
            self.logger.info("file global unit '{}' changed to '{}'".format(
                self.metadata.unit, self.internal.cvt_tmp.global_unit))
            self.metadata.unit = self.internal.cvt_tmp.global_unit

        if self.internal.cvt_tmp.global_unc_cand1 or \
           self.internal.cvt_tmp.global_unc_cand2:
            if isvalid(self.metadata.uncertainty):
                used_var = [vnum + 1
                            for vnum in range(len(self.variables))
                            if 'uncertainty' not in \
                                   self.variables[vnum].metadata and \
                               self.variables[vnum].metadata.unit == \
                                   self.metadata.uncertainty[1]]
                if used_var:
                    self.warning(
                        "File global 'Uncertaionty' cannot be unit converted "
                        "because it is still used in variable{} {}".format(
                            "s" if len(used_var) > 1 else "",
                            ', '.join(used_var)))
                else:
                    reset = False
                    if self.internal.cvt_tmp.global_unc_cand1:
                        if len(set([x.rounding
                                    for x in \
                                    self.internal.cvt_tmp.global_unc_cand1])) \
                            == 1:
                            # all candidates use the same rounding -- use the
                            # same
                            conv_obj = self.internal.cvt_tmp.global_unc_cand1[0]
                        else:
                            # use the first candidate, but reset the rounding
                            conv_obj = self.internal.cvt_tmp.global_unc_cand1[0]
                            reset = conv_obj.rounding
                    else:
                        # use the first candidate from global_unc_cand2 and
                        # reset rounding
                        conv_obj = self.internal.cvt_tmp.global_unc_cand2[0]
                        reset = conv_obj.rounding

                    origval = self.metadata.uncertainty[0]
                    value_list = [origval]
                    conv_obj.convert_data(value_list)
                    newval = value_list[0]
                    self.metadata.uncertainty = (newval, conv_obj.to_unit)
                    cnvstr = conv_obj.conversion_string(from_val=origval,
                                                        to_val=newval)
                    self.warning(
                        "Converting file global 'Measurement uncertainty' for "
                        "component {} {}.".format(self.metadata.comp_name,
                                                  cnvstr))
                    if reset != False:
                        conv_obj.rounding = reset  # reset the rounding

        if self.internal.cvt_tmp.global_dl_cand1 or \
           self.internal.cvt_tmp.global_dl_cand2:
            if isvalid(self.metadata.detection_limit):
                used_var = [vnum + 1
                            for vnum in range(len(self.variables))
                            if 'detection_limit' not in \
                                   self.variables[vnum].metadata and \
                               self.variables[vnum].metadata.unit == \
                                   self.metadata.detection_limit[1]]
                if used_var:
                    self.warning(
                        "File global 'Detection limit' cannot be unit "
                        "converted because it is still used in variable{} {}"
                        .format(
                            "s" if len(used_var) > 1 else "",
                            ', '.join(used_var)))
                else:
                    reset = False
                    if self.internal.cvt_tmp.global_dl_cand1:
                        if len(set([x.rounding
                                    for x in \
                                    self.internal.cvt_tmp.global_dl_cand1])) \
                            == 1:
                            # all candidates use the same rounding -- use the
                            # same
                            conv_obj = self.internal.cvt_tmp.global_dl_cand1[0]
                        else:
                            # use the first candidate, but reset the rounding
                            conv_obj = self.internal.cvt_tmp.global_dl_cand1[0]
                            reset = conv_obj.rounding
                    else:
                        # use the first candidate from global_dl_cand2 and reset
                        # rounding
                        conv_obj = self.internal.cvt_tmp.global_dl_cand2[0]
                        reset = conv_obj.rounding

                    origval = self.metadata.detection_limit[0]
                    value_list = [origval]
                    conv_obj.convert_data(value_list)
                    newval = value_list[0]
                    self.metadata.detection_limit = (newval, conv_obj.to_unit)
                    cnvstr = conv_obj.conversion_string(from_val=origval,
                                                        to_val=newval)
                    self.warning(
                        "Converting file global 'Detection limit' for "
                        "component {} {}.".format(self.metadata.comp_name,
                                                  cnvstr))
                    if reset != False:
                        conv_obj.rounding = reset  # reset the rounding

        if self.internal.cvt_tmp.global_url_cand1 or \
           self.internal.cvt_tmp.global_url_cand2:
            if isvalid(self.metadata.upper_range_limit):
                used_var = [vnum + 1
                            for vnum in range(len(self.variables))
                            if 'upper_range_limit' not in \
                                   self.variables[vnum].metadata and \
                               self.variables[vnum].metadata.unit == \
                                   self.metadata.upper_range_limit[1]]
                if used_var:
                    self.warning(
                        "File global 'Upper range limit' cannot be unit "
                        "converted because it is still used in variable{} {}"
                        .format(
                            "s" if len(used_var) > 1 else "",
                            ', '.join(used_var)))
                else:
                    reset = False
                    if self.internal.cvt_tmp.global_url_cand1:
                        if len(set([x.rounding
                                    for x in \
                                    self.internal.cvt_tmp.global_url_cand1])) \
                            == 1:
                            # all candidates use the same rounding -- use the
                            # same
                            conv_obj = self.internal.cvt_tmp.global_url_cand1[0]
                        else:
                            # use the first candidate, but reset the rounding
                            conv_obj = self.internal.cvt_tmp.global_url_cand1[0]
                            reset = conv_obj.rounding
                    else:
                        # use the first candidate from global_url_cand2 and
                        # reset rounding
                        conv_obj = self.internal.cvt_tmp.global_url_cand2[0]
                        reset = conv_obj.rounding

                    origval = self.metadata.upper_range_limit[0]
                    value_list = [origval]
                    conv_obj.convert_data(value_list)
                    newval = value_list[0]
                    self.metadata.upper_range_limit = (newval, conv_obj.to_unit)
                    cnvstr = conv_obj.conversion_string(from_val=origval,
                                                        to_val=newval)
                    self.warning(
                        "Converting file global 'Upper range limit' for "
                        "component {} {}.".format(self.metadata.comp_name,
                                                  cnvstr))
                    if reset != False:
                        conv_obj.rounding = reset  # reset the rounding

        for qanum in self.get_qa_numbers():
            qa_ = self.get_qa_by_number(qanum, None)

            if self.internal.cvt_tmp.global_qabias_cand1[qanum] or \
               self.internal.cvt_tmp.global_qabias_cand2[qanum]:
                if 'qa_bias' in qa_ and isvalid(qa_.qa_bias):
                    used_var = []
                    for vnum in range(len(self.variables)):
                        varqa = self.get_qa_by_number(qanum, vnum)
                        if ('qa_bias' not in varqa or varqa.qa_bias is None) \
                                and self.variables[vnum].metadata.unit == \
                                    qa_.qa_bias[1]:
                            used_var.append(vnum + 1)
                    if used_var:
                        self.warning(
                            "File global 'QA{} bias' cannot be unit converted "
                            "because it is still used in variable{} {}"
                            .format(
                                str(qanum) if qanum != -1 else '',
                                "s" if len(used_var) > 1 else "",
                                ', '.join(used_var)))
                    else:
                        reset = False
                        if self.internal.cvt_tmp.global_qabias_cand1[qanum]:
                            if len(set(
                                    [x.rounding
                                     for x in \
                                     self.internal.cvt_tmp.\
                                     global_qabias_cand1[qanum]])) == 1:
                                # all candidates use the same rounding -- use
                                # the same
                                conv_obj = self.internal.cvt_tmp.\
                                    global_qabias_cand1[qanum][0]
                            else:
                                # use the first candidate, but reset the
                                # rounding
                                conv_obj = self.internal.cvt_tmp.\
                                    global_qabias_cand1[qanum][0]
                                reset = conv_obj.rounding
                        else:
                            # use the first candidate from global_qabias_cand2
                            # and reset rounding
                            conv_obj = self.internal.cvt_tmp.\
                                global_qabias_cand2[qanum][0]
                            reset = conv_obj.rounding

                        origval = qa_.qa_bias[0]
                        value_list = [origval]
                        conv_obj.convert_data(value_list)
                        newval = value_list[0]
                        qa_.qa_bias = (newval, conv_obj.to_unit)
                        cnvstr = conv_obj.conversion_string(from_val=origval,
                                                            to_val=newval)
                        self.warning(
                            "Converting file global 'QA{} bias' for "
                            "component {} {}.".format(
                                str(qanum) if qanum != -1 else '',
                                self.metadata.comp_name,
                                cnvstr))
                        if reset != False:
                            conv_obj.rounding = reset  # reset the rounding

            if self.internal.cvt_tmp.global_qavariab_cand1[qanum] or \
               self.internal.cvt_tmp.global_qavariab_cand2[qanum]:
                if 'qa_variability' in qa_ and isvalid(qa_.qa_variability):
                    used_var = []
                    for vnum in range(len(self.variables)):
                        varqa = self.get_qa_by_number(qanum, vnum)
                        if ('qa_variability' not in varqa or \
                                    varqa.qa_variability is None) and \
                                self.variables[vnum].metadata.unit == \
                                    qa_.qa_variability[1]:
                            used_var.append(vnum + 1)
                    if used_var:
                        self.warning(
                            "File global 'QA{} variability' cannot be unit "
                            "converted because it is still used in "
                            "variable{} {}".format(
                                str(qanum) if qanum != -1 else '',
                                "s" if len(used_var) > 1 else "",
                                ', '.join(used_var)))
                    else:
                        reset = False
                        if self.internal.cvt_tmp.global_qavariab_cand1[qanum]:
                            if len(set(
                                    [x.rounding
                                     for x in \
                                     self.internal.cvt_tmp.\
                                        global_qavariab_cand1[qanum]])) == 1:
                                # all candidates use the same rounding -- use
                                # the same
                                conv_obj = self.internal.cvt_tmp.\
                                    global_qavariab_cand1[qanum][0]
                            else:
                                # use the first candidate, but reset the
                                # rounding
                                conv_obj = self.internal.cvt_tmp.\
                                    global_qavariab_cand1[qanum][0]
                                reset = conv_obj.rounding
                        else:
                            # use the first candidate from global_qavariab_cand2
                            # and reset rounding
                            conv_obj = self.internal.cvt_tmp.\
                                global_qavariab_cand2[qanum][0]
                            reset = conv_obj.rounding

                        origval = qa_.qa_variability[0]
                        value_list = [origval]
                        conv_obj.convert_data(value_list)
                        newval = value_list[0]
                        qa_.qa_variability = (newval, conv_obj.to_unit)
                        cnvstr = conv_obj.conversion_string(from_val=origval,
                                                            to_val=newval)
                        self.warning(
                            "Converting file global 'QA{} variability' for "
                            "component {} {}.".format(
                                str(qanum) if qanum != -1 else '',
                                self.metadata.comp_name,
                                cnvstr))
                        if reset != False:
                            conv_obj.rounding = reset  # reset the rounding

    def _convert_variable_input(self, vnum, conv_obj):
        """
        Convert one variables on import from one unit to another.
        E.g.: convert 'nitrogen_dioxide, nmol/mol' to
                      'nitrogen_dioxide, ug N/m3'
        Parameters:
            vnum         variable number
            conv_obj     converison object
        Returns:
            None
        """
        file_vnum, _, file_metalnum = self.msgref_vnum_lnum(vnum)
        comp = self.get_meta_for_var(vnum, 'comp_name')
        self._check_convert_global_metadata(vnum, conv_obj)

        # first, convert the data, to get the rounding right according to data:
        if len(self.sample_times) < 100 and \
                'read_tmp' in self.internal and self.internal.read_tmp and \
                'vmiss' in self.internal.read_tmp and \
                self.internal.read_tmp.vmiss and \
                re.match(r'^9+(\.9*)?$', self.internal.read_tmp.vmiss[vnum]):
            # special case for input conversion if not enough values:
            # use missing value in addition to esimate precision
            # (only 99.99 notation missing values can be used,
            # 0x are not needed and 9E9 format does not help for rounding....
            self.variables[vnum].values_.append(
                    float(self.internal.read_tmp.vmiss[vnum]))
            conv_obj.convert_data(self.variables[vnum].values_)
            del self.variables[vnum].values_[-1]
        else:
            conv_obj.convert_data(self.variables[vnum].values_)

        self.variables[vnum].metadata.unit = conv_obj.to_unit  # change unit

        cnvstr = conv_obj.conversion_string()
        self.warning("variable {}: Component '{}', converting unit {}."
                      .format(file_vnum, comp, cnvstr), lnum=file_metalnum)
        conv_remark = "Data converted on import into EBAS {}.".format(cnvstr)

        # change uncertainty, detection limit and upper range limit, qa_qa_bias
        # and qa_variability
        if 'uncertainty' in self.variables[vnum].metadata and \
                isvalid(self.variables[vnum].metadata.uncertainty) and \
                self.variables[vnum].metadata.uncertainty[1] == \
                    conv_obj.from_unit:
            uncert = self.variables[vnum].metadata.uncertainty
            if conv_obj.rounding is None:
                # rounding needs to be reset after conversion
                reset = True
            else:
                reset = False
            origval = uncert[0]
            value_list = [origval]
            conv_obj.convert_data(value_list)
            newval = value_list[0]
            self.variables[vnum].metadata.uncertainty = (newval,
                                                         conv_obj.to_unit)
            cnvstr = conv_obj.conversion_string(from_val=origval, to_val=newval)
            self.warning(
                "variable {}: converting 'Measurement uncertainty' for "
                "component {} {}.".format(file_vnum, comp, cnvstr),
                lnum=file_metalnum)
            conv_remark += " Measurement uncertainty converted {}.".format(
                cnvstr)
            if reset:
                conv_obj.rounding = None  # reset the rounding
        if 'detection_limit' in self.variables[vnum].metadata and \
                isvalid(self.variables[vnum].metadata.detection_limit) and \
                self.variables[vnum].metadata.detection_limit[1] == \
                    conv_obj.from_unit:
            detect = self.variables[vnum].metadata.detection_limit
            if conv_obj.rounding is None:
                # rounding needs to be reset after conversion
                reset = True
            else:
                reset = False
            origval = detect[0]
            value_list = [origval]
            conv_obj.convert_data(value_list)
            newval = value_list[0]
            self.variables[vnum].metadata.detection_limit = (newval,
                                                             conv_obj.to_unit)
            cnvstr = conv_obj.conversion_string(from_val=origval, to_val=newval)
            self.warning(
                "variable {}: converting 'Detection limit' for component {} {}."
                .format(file_vnum, comp, cnvstr), lnum=file_metalnum)
            conv_remark += " Detection limit converted {}.".format(cnvstr)
            if reset:
                conv_obj.rounding = None  # reset the rounding
        if 'upper_range_limit' in self.variables[vnum].metadata and \
                isvalid(self.variables[vnum].metadata.upper_range_limit) and \
                self.variables[vnum].metadata.upper_range_limit[1] == \
                    conv_obj.from_unit:
            upper = self.variables[vnum].metadata.upper_range_limit
            if conv_obj.rounding is None:
                # rounding needs to be reset after conversion
                reset = True
            else:
                reset = False
            origval = upper[0]
            value_list = [origval]
            conv_obj.convert_data(value_list)
            newval = value_list[0]
            self.variables[vnum].metadata.upper_range_limit = (newval,
                                                               conv_obj.to_unit)
            cnvstr = conv_obj.conversion_string(from_val=origval, to_val=newval)
            self.warning(
                "variable {}: converting 'Upper range limit' for component "
                "{} {}." .format(file_vnum, comp, cnvstr),
                lnum=file_metalnum)
            conv_remark += " Upper range limit converted {}.".format(cnvstr)
            if reset:
                conv_obj.rounding = None  # reset the rounding
        for qanum in self.get_qa_numbers():
            qa_ = self.get_qa_by_number(qanum, vnum)
            if 'qa_bias' in qa_ and qa_.qa_bias[1] == conv_obj.from_unit:
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
                self.warning(
                    "variable {}: converting 'QA{} bias' for component "
                    "{} {}." .format(
                        file_vnum,
                        str(qa_.qa_number) if qa_.qa_number != -1 else '',
                        comp, cnvstr),
                    lnum=file_metalnum)
                conv_remark += " QA{} bias converted {}.".format(
                    str(qa_.qa_number) if qa_.qa_number != -1 else '',
                    cnvstr)
                if reset:
                    conv_obj.rounding = None  # reset the rounding
            if 'qa_variability' in qa_ and \
                    qa_.qa_variability[1] == conv_obj.from_unit:
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
                self.warning(
                    "variable {}: converting 'QA{} variability' for component "
                    "{} {}." .format(
                        file_vnum,
                        str(qa_.qa_number) if qa_.qa_number != -1 else '',
                        comp, cnvstr),
                    lnum=file_metalnum)
                conv_remark += " QA{} variability converted {}.".format(
                    str(qa_.qa_number) if qa_.qa_number != -1 else '',
                    cnvstr)
                if reset:
                    conv_obj.rounding = None  # reset the rounding

        # add comment
        comment = self.get_meta_for_var(vnum, 'comment')
        if comment:
            comment += " -- " + conv_remark
        else:
            comment = conv_remark
        self.variables[vnum].metadata.comment = comment
