"""
$Id: read_precip.py 2770 2021-12-08 22:36:25Z pe $

File input functionality for EbasEanetPrecip
"""

import datetime
from nilutility.datatypes import DataObject, recursive_data_object
from ebas.domain.basic_domain_logic.flags import get_flag_summary
from fileformats.EANET import EanetPrecip, EanetError
from .eanet_cfg import EANET_SITES, EANET_PRECIP_ANALYTICAL_LABS, \
    EANET_PRECIP_REPORTERS, EANET_PRECIP_GLOBAL, EANET_PRECIP_PARAMS, \
    EANET_PRECIP_DETAIL
from .base import EbasEanetPrecipBase, EbasEanetReadError

EANET_SITES = recursive_data_object(EANET_SITES)
EANET_PRECIP_ANALYTICAL_LABS = recursive_data_object(
    EANET_PRECIP_ANALYTICAL_LABS)
EANET_PRECIP_REPORTERS = recursive_data_object(EANET_PRECIP_REPORTERS)
EANET_PRECIP_GLOBAL = recursive_data_object(EANET_PRECIP_GLOBAL)
EANET_PRECIP_PARAMS = recursive_data_object(EANET_PRECIP_PARAMS)
EANET_PRECIP_DETAIL = recursive_data_object(EANET_PRECIP_DETAIL)


class EanetPrecipPartialRead(EbasEanetPrecipBase):
    """
    Read fuctionality for EbasEanetPrecip I/O object.
    """

    UNIQUE_ID = 0

    def get_unique_id(self):
        """
        Get a unique int id
        """
        self.__class__.UNIQUE_ID += 1
        return self.__class__.UNIQUE_ID

    def _read(self, filename, skip_unitconvert=False, **args):
        """
        Reads a EANET precip file into an EBAS I/O object.
        Parameters:
            filename          path and filename
            other paramters are ignored: ignore_rescode, ignore revdate,
                ignore_parameters, skip_data, skip_unitconvert, skip_variables,
                encoding, ignore_numformat

        Returns:
            None
        Raises:
            IOError (from builtin, file open)
            EbasEanetReadError
        """
        # EANET precip file has no revdata metadata, use now:
        self.metadata.revdate = datetime.datetime.utcnow()
        self.sourcefile = EanetPrecip()
        try:
            self.sourcefile.read(filename)
        except EanetError:
            pass
        self.errors += self.sourcefile.errors
        self.warnings += self.sourcefile.warnings
        if self.errors:
            self.logger.info("Exiting because of previous errors")
            raise EbasEanetReadError(
                "{} Errors, {} Warnings".format(self.errors,
                                                self.warnings))
        self.parse()
        if self.errors:
            self.logger.info("Exiting because of previous errors")
            raise EbasEanetReadError(
                "{} Errors, {} Warnings".format(self.errors,
                                                self.warnings))
        self.prepare_write(False)
        if self.errors:
            self.logger.info("Exiting because of previous errors")
            raise EbasEanetReadError(
                "{} Errors, {} Warnings".format(self.errors,
                                                self.warnings))

    def parse(self):
        """
        Parse all metadata and data from the source file object to the ebas-io
        object.
        """
        self._prec_values = None

        global_meta = EANET_PRECIP_GLOBAL.EBAS.copy()
        global_eanet_meta = DataObject()
        global_eanet_meta.update(EANET_PRECIP_GLOBAL.EANET)
        try:
            global_eanet_meta.update(
                EANET_SITES[self.sourcefile.site_code]['EANET'])
            global_meta.update(EANET_SITES[self.sourcefile.site_code]['EBAS'])
        except KeyError:
            self.error("Site '{}' not found in configuration".format(
                self.sourcefile.site_code))
            raise EbasEanetReadError(
                "{} Errors, {} Warnings".format(self.errors,
                                                self.warnings))
        if self.sourcefile.site_name != global_eanet_meta.site_name:
            self.error(
                "Site name mismatch: file '{}' inconsistent with "
                "configuration".format(self.sourcefile.file_name))

        self._map_analytical_lab(global_meta)
        self._map_person(global_meta)

        self.sample_times = self.sourcefile.sample_times
        for var_key, conf in EANET_PRECIP_PARAMS.items():
            # first round, only amount
            if conf.EBAS.comp_name.startswith('precipitation_amount'):
                self._add_var(var_key, global_meta, global_eanet_meta)
        for var_key, conf in EANET_PRECIP_PARAMS.items():
            # second round, all other variables
            if not conf.EBAS.comp_name.startswith('precipitation_amount'):
                self._add_var(var_key, global_meta, global_eanet_meta)

    def _add_var(self, var_key, global_meta, global_eanet_meta):
        """
        Convert a single variable.
        Parameters:
            var_key            the variable key in the eanet configuration
            global_meta        global metadata
            global_eanet_meta  global eanet metadata
        Returns:
            tuple (metadata, values, flags)
        """
        metadata = global_meta.copy()
        eanet_meta = global_eanet_meta.copy()
        metadata.update(EANET_PRECIP_PARAMS[var_key].EBAS)
        eanet_meta.update(EANET_PRECIP_PARAMS[var_key].EANET)

        # Update/override metadata from EANET_PRECIP_DETAIL configuration
        try:
            EANET_PRECIP_DETAIL[self.sourcefile.site_code]
        except KeyError:
            self.error(
                "Site '{}' not found in EANET_PRECIP_DETAIL "
                "configuration".format(self.sourcefile.site_code))
            return
        else:
            try:
                conf = EANET_PRECIP_DETAIL[self.sourcefile.site_code][var_key]
            except KeyError:
                conf = EANET_PRECIP_DETAIL[self.sourcefile.site_code][None]
            metadata.update(conf.EBAS)
            eanet_meta.update(conf.EANET)

        self._set_station(metadata)
        self._set_org(metadata)
        self._set_method(metadata)

        form_number = eanet_meta.form_number
        var_name = eanet_meta.variable_name

        var = self.sourcefile.forms[form_number].var_by_name(var_name)

        if var.unit != eanet_meta.unit:
            self.error(
                "{} ({}): EANET unit mismatch between file and "
                "configuration".format(var_name, var_key))
            return

        if not [x for x in var.samples if x is not None]:
            self.warning("{} ({}): no valid values; skipping".format(
                var_name, var_key))
            return

        flags = var.flags
        if flags is None:
            # This variable has no flags in the EANET file. Set empty flags.
            flags = [[] for _ in range(len(var.samples))]
        # add some missing flags:
        for i, val in enumerate(var.samples):
            if val is None:
                _, _, missing = get_flag_summary(flags[i], want_issues=False)
                if self._prec_values and self._prec_values[i] == 0.0 and \
                        890 not in flags[i]:
                    # no precipitation: add flag 890
                    flags[i].append(890)
                elif not missing:
                    # value is missing, but no missing flag set:
                    flags[i].append(999)
        if not self._prec_values and \
                metadata.comp_name.startswith('precipitation_amount'):
            self._prec_values = var.samples
        self._add_variable_nondomain(
            self.get_unique_id(), metadata, var.samples, flags, 0)

    def _map_analytical_lab(self, metadata):
        """
        Map the analytical lab code.
        """
        # override #ana_lab_code even when it is set in station config
        # needed for precip mapping (filter needes #ana_lab_code from station
        # config, but precip uses this mapping.
        # If setting in config is needed, set in EANET_PRECIP_DETAIL
        try:
            metadata['#ana_lab_code'] = EANET_PRECIP_ANALYTICAL_LABS[
                self.sourcefile.laboratory]
        except KeyError:
            self.error("Organisation '{}' not found in configuration".format(
                       self.sourcefile.laboratory))
            metadata['#ana_lab_code'] = ''

    def _map_person(self, metadata):
        """
        Map originater and submitter from reporter
        """
        nobody = DataObject({
            'PS_LAST_NAME': None,
            'PS_FIRST_NAME': None,
            'PS_EMAIL': None,
            'PS_ORG_NAME': None,
            'PS_ORG_ACR': None,
            'PS_ORG_UNIT': None,
            'PS_ADDR_LINE1': None,
            'PS_ADDR_LINE2': None,
            'PS_ADDR_ZIP': None,
            'PS_ADDR_CITY': None,
            'PS_ADDR_COUNTRY': None,
            'PS_ORCID': None,
            })
        if self.sourcefile.reporter not in EANET_PRECIP_REPORTERS:
            self.warning(
                "Repoorter '{}' not found in configuration, "
                "using as is.".format(self.sourcefile.reporter))
            person = nobody.copy()
            person.update({'PS_LAST_NAME': self.sourcefile.reporter})
            pers_list = [person]
        else:
            pers_list = []
            for pers in EANET_PRECIP_REPORTERS[self.sourcefile.reporter]:
                person = nobody.copy()
                person.update(pers)
                pers_list.append(person)
        metadata['originator'] = pers_list
        metadata['submitter'] = pers_list
