"""
$Id: read_filter.py 2759 2021-11-30 11:41:16Z pe $

File input functionality for EbasEanetFilter
"""

import datetime
from nilutility.datatypes import DataObject, recursive_data_object
from fileformats.EANET import EanetFilter, EanetError
from .eanet_cfg import EANET_SITES, EANET_FILTER_GLOBAL, EANET_FILTER_PARAMS, \
    EANET_FILTER_DETAIL
from .base import EbasEanetFilterBase, EbasEanetReadError

EANET_SITES = recursive_data_object(EANET_SITES)
EANET_FILTER_GLOBAL = recursive_data_object(EANET_FILTER_GLOBAL)
EANET_FILTER_PARAMS = recursive_data_object(EANET_FILTER_PARAMS)
EANET_FILTER_DETAIL = recursive_data_object(EANET_FILTER_DETAIL)


class EanetFilterPartialRead(EbasEanetFilterBase):
    """
    Read fuctionality for EbasEanetFilter I/O object.
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
        Reads a EANET filter file into an EBAS I/O object.
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
        # EANET filter file has no revdata metadata, use now:
        self.metadata.revdate = datetime.datetime.utcnow()
        self.sourcefile = EanetFilter()
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
        self.prepare_write(False)

    def parse(self):
        """
        Parse all metadata and data from the source file object to the ebas-io
        object.
        """
        global_meta = EANET_FILTER_GLOBAL.EBAS.copy()
        global_eanet_meta = DataObject()
        global_eanet_meta.update(EANET_FILTER_GLOBAL.EANET)
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
        self.sample_times = self.sourcefile.sample_times
        for var in self.sourcefile.variables:
            metadata = global_meta.copy()
            if not [x for x in var.samples if x is not None]:
                self.warning(
                    "Parameter: '{}': no valid values; skipping".format(
                        var.name))
                continue
            eanet_meta = global_eanet_meta.copy()
            try:
                eanet_meta.update(EANET_FILTER_PARAMS[var.name]['EANET'])
                metadata.update(EANET_FILTER_PARAMS[var.name]['EBAS'])
            except KeyError:
                self.error(
                    "Parameter '{}' not found in configuration".format(
                        var.name))
                continue

            # Update/override metadata from EANET_PRECIP_DETAIL configuration
            try:
                EANET_FILTER_DETAIL[self.sourcefile.site_code]
            except KeyError:
                self.error(
                    "Site '{}' not found in EANET_FILTER_DETAIL "
                    "configuration".format(self.sourcefile.site_code))
                raise EbasEanetReadError(
                    "{} Errors, {} Warnings".format(self.errors,
                                                    self.warnings))
            else:
                try:
                    cfg = EANET_FILTER_DETAIL[
                        self.sourcefile.site_code][var.name]
                except KeyError:
                    try:
                        cfg = EANET_FILTER_DETAIL[
                            self.sourcefile.site_code][None]
                    except KeyError:
                        self.error(
                            "Configuration error {} / {}/None".format(
                                self.sourcefile.site_code, var.name))
                        continue
                eanet_meta.update(cfg.EANET)
                metadata.update(cfg.EBAS)

            self._set_station(metadata)
            self._set_org(metadata)
            self._set_method(metadata)

            if var.unit != eanet_meta.unit:
                self.error(
                    "Parameter: '{}': EANET unit mismatch between file and "
                    "configuration".format(var.name))
            self._add_variable_nondomain(
                self.get_unique_id(), metadata, var.samples, var.flags, 0)
