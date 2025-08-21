"""
ebas/nasa_ames/read/legacy_vnames.py
$Id: legacy_vnames.py 1728 2017-07-11 09:00:19Z pe $

Translator for legacy variable names

History:
V.1.0.0  2013-06-22  pe  initial version

"""

import re
from .parse_base import NasaAmesPartialReadParserBase

class NasaAmesPartialReadLegacyVnames(# pylint: disable=R0901, W0223,
        NasaAmesPartialReadParserBase):
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Translator for legacy variable names.
    This is a base class for NasaAmesPartialReadParserVariables
    """

    def translate_legacy_vnames(self):
        """
        Translates legacy VNAME lines to current (EBAS_1.1) standard.
        Parameters:
            None
        Returns:
            None
        Raises:
        Variable number in the object differs from variable number in file
        (because the object only stores measurements as variables, having
        flags as an attribute)
        """
        for vnum in range(self.nasa1001.data.NV):
            if vnum in self.internal.read_tmp.var_skipped:
                # already skipped?
                continue
            vname = self.nasa1001.data.VNAME[vnum]
            for tran in self.__class__.Translations:
                if re.search(tran[0], vname):
                    if tran[1] is None:
                        self.warning(
                            "VNAME[{}]: Legacy VNAME '{}' skipped".format(
                                vnum, vname), lnum=13+vnum)
                        self.internal.read_tmp.var_skipped.append(vnum)
                        break
                    vname = re.sub(tran[0], tran[1], vname)
            if vnum in self.internal.read_tmp.var_skipped:
                # now skipped?
                continue
            if self.nasa1001.data.VNAME[vnum] != vname:
                self.warning(
                    "VNAME[{}]: Legacy VNAME '{}' translated to '{}'".format(
                        vnum, self.nasa1001.data.VNAME[vnum], vname),
                    lnum=13+vnum)

            # EBAS_1 legacy: VNAME 'value'
            if re.match('^ *value *,', vname):
                if self.metadata.datadef == 'EBAS_1' and \
                   self.nasa1001.data.NV == 3:
                    if self.metadata.comp_name is None:
                        self.error("VNAME[{}]: ".format(vnum) +\
                            "generic VNAME 'value' can't be used when Metadata "
                            "'Component' is missing in NCOM", lnum=13+vnum)
                    else:
                        vname = re.sub('^ *value *', self.metadata.comp_name,
                                       vname)
                elif self.nasa1001.data.NV == 3:
                    if self.metadata.comp_name is None:
                        self.error(
                            "VNAME[{}]: legacy EBAS_1 VNAME 'value' can't be "
                            "used when Metadata 'Component' is missing in NCOM".
                            format(vnum), lnum=13+vnum)
                    else:
                        vname = re.sub('^ *value *', self.metadata.comp_name,
                                       vname, 13 + vnum)

                        self.warning(
                            "VNAME[{}]: legacy EBAS_1 VNAME 'value', "
                            "translated to '{}'".format(
                                vnum, self.metadata.comp_name),
                            lnum=13+vnum)
                else:
                    self.error("VNAME[{}]: ".format(vnum) +\
                        "VNAME 'value' is illegal for multicolumn files; "
                        "variable skipped", lnum=13+vnum)
                    self.internal.read_tmp.var_skipped.append(vnum)
                    continue # stop parsing this line

            if vname == 'numflag, no unit, max 3 flags (of 3 digits each) ' +\
                        'coded into decimals':
                if self.metadata.datadef == 'EBAS_1':
                    vname = 'numflag, no unit'
                # else: gnererate a "unconventional VNAME for flag column" error
                # message in _parse_variable_numflag()
            if re.search('nominal/measured *=', vname):
                vname = re.sub('nominal/measured *=', 'Nominal/measured=',
                               vname)
                self.warning(
                    "VNAME[{}]: Legacy characteristic 'nominal/measured' "
                    "translated to 'Nominal/measured'".format(vnum),
                    lnum=13+vnum)

            self.nasa1001.data.VNAME[vnum] = vname

    Translations = (
        (r'^start_time of measurement, *year *$', None),
        (r'^end_time of measurement, *year *$', None),
        (r'^number of wavelengths\s*$', None),
        (r'^number of wavelengths,\s*no unit', None),

        (r'^number of size bins *$', None),
        (r'^number of size bins,\s*no unit', None),
        (r'^absorption_Aangstroem_coefficient, no unit$', None),

        (r'^([^, ]*)_statistics', '\\1'),

        (r'^internal instrument pressure, *hPa',
         'pressure, hPa, Location=instrument internal'),
        (r'^Instrument internal Pressure, *hPa',
         'pressure, hPa, Location=instrument internal'),

        (r'^internal instrument temperature, *K',
         'temperature, K, Location=instrument internal'),
        (r'^Instrument internal Temperature, *K',
         'temperature, K, Location=instrument internal'),
        (r'^sample temperature measured at inlet, *K',
         'temperature, K, Location=inlet'),
        (r'^sample temperature measured at outlet, *K',
         'temperature, K, Location=outlet'),

        (r'^internal relative humidity, *%',
         'relative_humidity, %, Location=instrument internal'),
        (r'^Instrument internal relative humidity, *%',
         'relative_humidity, %, Location=instrument internal'),
        (r'^relative humidity measured at inlet, *%',
         'relative_humidity, %, Location=inlet'),
        (r'^relative humidity measured at outlet, *%',
         'relative_humidity, %, Location=outlet'),

        (r'^lamp supply voltage, V',
         'electric_tension, V, Matrix=instrument, '
         'Location=lamp lamp supply'),
        (r'^lamp supply current, A',
         'electric_current, A, Matrix=instrument, '
         'Location=lamp lamp supply'),
        (r'^status flags, hex notation',
         'status, no unit, Matrix=instrument, '
         'Status type=overall instrument status'),

        (r'^recalibrated, truncation corrected ((back)?scattering) ' +\
             r'coefficient at (\d+) nm, 1/Mm',
         'aerosol_light_\\1_coefficient, 1/Mm, Wavelength=\\3nm'),
        (r'^((back)?scattering) coefficient (\d+\.\d*) percentile at (\d+) nm, '
         '1/Mm',
         'aerosol_light_\\1_coefficient, 1/Mm, Wavelength=\\4nm, '
         'Statistics=percentile:\\3'),

        (r'^(aerosol )?absorption coefficient at (\d+) ?nm, 1/Mm',
         'aerosol_absorption_coefficient, 1/Mm, Wavelength=\\2nm'),
        (r'^(aerosol )?absorption coefficient at (\d+) ?nm, (\d+\.\d*)' +\
              r'percentile, 1/Mm',
         'aerosol_absorption_coefficient, 1/Mm, Wavelength=\\2nm, '
         'Statistics=percentile:\\3'),
        (r'^(aerosol )?absorption coefficient (\d+\.\d*) percentile at ' +\
             r'(\d+) ?nm, 1/Mm',
         'aerosol_absorption_coefficient, 1/Mm, Wavelength=\\3nm, '
         'Statistics=percentile:\\2'),

        (r'^absorption_coefficient, 1/Mm',
         'aerosol_absorption_coefficient, 1/Mm'),

        (r'^aerosol number concentration dN/dlogD at D= *(\d+\.\d*) *nm, ' +\
             r'1/cm3',
         'particle_number_size_distribution, 1/cm3, D=\\1nm'),
        (r'^sample flow rate, standard conditions', 'flow_rate'),
        (r'^aerosol flow rate, ', 'flow_rate, '),

        (r', *Arithmetic mean', ', Statistics=arithmetic mean'),
        (r', *Median', ', Statistics=median'),
        (r', *Stddev', ', Statistics=stddev'),

        ('aerosol_light_backscattering_coefficient_statistics',
         'aerosol_light_backscattering_coefficient'),

        ('global_radiation',
         'downward_solar_radiation_flux_density'),

        )
