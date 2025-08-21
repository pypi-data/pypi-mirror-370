"""
EBAS submission templates and template checks: NOx Template
"""

from .base import EbasTemplateBase, NoTemplate


class EbasTemplateNOxLev0(EbasTemplateBase):
    """
    Ebas template for NOx
    """

    TEMPLATE_NAME = 'NOx lev0'

    def match(self):
        """
        See if this template matches a file.
        """
        if (not self.file.metadata.datalevel or
                not self.file.metadata.datalevel.startswith('0')):
            raise NoTemplate()
        # Contains only NOx variables
        comp_names = [x.metadata.comp_name for x in self.file.variables]
        # identifying components (any of those makes the file a NOx file)
        ident_comps = ('NO_#counts', 'NO_converter_#counts', 'NO_sensitivity',
                       'nitrogen_monoxide', 'nitrogen_dioxide')
        # additional components
        add_comps = ('pressure', 'temperature', 'status',
                     'converter_efficiency')
        if not any([x in ident_comps for x in comp_names]):
            raise NoTemplate()
        if not all([x in ident_comps + add_comps for x in comp_names]):
            self.error(
                'no match because of additional variobles: {}'.format(
                    ', '.join([x for x in comp_names
                               if x not in ident_comps + add_comps])))
            raise NoTemplate()

        instr_types = set([self.file.get_meta_for_var(vnum, 'instr_type')
                      for vnum in range(len(self.file.variables))])
        if len(instr_types) != 1:
            self.error('only one instrumennt type for all variables allowed')
        self.instr_type = next(iter(instr_types))

        projs = self.file.metadata.projects
        strict_projs = ['ACTRIS', 'ACTRIS_NRT']
        self.actris = any([x in strict_projs for x in projs])
        self.actriserror = self.error if self.actris else self.warning

    def special_checks(self):
        """
        Special checks which cannot be done in the defailt checks.
        """
        if self.instr_type == 'chemiluminescence_molybdenum' and self.actris:
            self.error(
                'Instrument type {} not apporved by ACTRIS'.format(
                    self.instr_type))

        for vnum, var in enumerate(self.file.variables):
            comp = var.metadata.comp_name
            stat = self.file.get_meta_for_var(vnum, 'statistics')
            file_vnum, _, file_metalnum = self.file.msgref_vnum_lnum(vnum)
            if (comp in ('nitrogen_monoxide', 'nitrogen_dioxide') and
                    stat == 'arithmetic mean'):
                cal_scale = self.file.get_meta_for_var(vnum, 'cal_scale')
                if not cal_scale:
                    self.actriserror(
                        ("Variable {}: 'Calibration scale' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                stdtemp = self.file.get_meta_for_var(vnum, 'vol_std_temp')
                if not stdtemp:
                    self.actriserror(
                        ("Variable {}: 'Volume std. temperature' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                elif not isinstance(stdtemp, float):
                    self.actriserror(
                        ("Variable {}: 'Volume std. temperature' metadata "
                         "must be numeric").format(file_vnum),
                        lnum=file_metalnum)
                stdpres = self.file.get_meta_for_var(vnum, 'vol_std_pressure')
                if not stdpres:
                    self.actriserror(
                        ("Variable {}: 'Volume std. pressure' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                elif not isinstance(stdpres, float):
                    self.actriserror(
                        ("Variable {}: 'Volume std. pressure' metadata "
                         "must be numeric").format(file_vnum),
                        lnum=file_metalnum)
        checkvariables = [
            {
                'comp_name': 'pressure',
                'matrix': 'instrument',
                'characteristics': {
                    'Location': 'inlet',
                }
            },
            {
                'comp_name': 'pressure',
                'matrix': 'instrument',
                'characteristics': {
                    'Location': 'detector',
                }
            },
            {
                'comp_name': 'temperature',
                'matrix': 'instrument',
                'characteristics': {
                    'Location': 'inlet',
                }
            },
            {
                'comp_name': 'temperature',
                'matrix': 'instrument',
                'characteristics': {
                    'Location': 'detector',
                }
            },
            {
                'comp_name': 'status',
                'matrix': 'instrument',
                'characteristics': {
                    'Status type': 'calibration standard',
                }
            },
            {
                'comp_name': 'status',
                'matrix': 'instrument',
                'characteristics': {
                    'Status type': 'zero mode',
                }
            },
            {
                'comp_name': 'NO_#counts',
            },
            {
                'comp_name': 'NO_converter_#counts',
            },
            {
                'comp_name': 'NO_sensitivity',
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'arithmetic mean'
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'expanded uncertainty 2sigma'
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'precision'
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'detection limit'
            },
        ]
        checkvariables_converter = [
            {
                'comp_name': 'converter_efficiency',
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'arithmetic mean'
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'expanded uncertainty 2sigma'
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'precision'
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'detection limit'
            },
        ]
        if self.instr_type != 'chemiluminescence_photometer':
            checkvariables += checkvariables_converter

        # check if all variables are included (and appear exactly once)
        for elem in checkvariables:
            try:
                var = self.file.find_variable(elem)
            except ValueError as excpt:
                # variable is either missing, or more then one variable matches
                # "flatten" the characteristics:
                new = {x: elem[x] for x in elem if x != 'characteristics'}
                if 'characteristics' in elem:
                    new.update({x: elem['characteristics'][x]
                                for x in elem['characteristics']})
                self.actriserror("{}: {}".format(
                    str(excpt),
                    ', '.join(['='.join(
                        (self.file.internal.ebasmetadata.metadata_keys[x]['tag']
                         if x in self.file.internal.ebasmetadata.metadata_keys
                         else x, new[x])) 
                         for x in new.keys()])))
        # check for extrs variables:
        for vnum, unused_ in enumerate(self.file.variables):
            file_vnum, _, file_metalnum = self.file.msgref_vnum_lnum(vnum)
            if not any([self.file.match_variable(vnum, elem)
                        for elem in checkvariables]):
                # variable is not allowed
                self.error(
                    "Variable {}:  variable is not allowed".format(file_vnum),
                    lnum=file_metalnum)

        # check mandatory metadata:
        mandatory_global_metadata = {
            'ozone_corr': 'Not corrected for reaction with O3 in the inlet',
            'watervapor_corr': 'Not corrected for water vapor quenching in CLD',
        }
        if self.instr_type != 'chemiluminescence_photometer':
            mandatory_global_metadata.update({
                'time_inlet_to_converter': None,
                'time_converter_or_bypass_line': None,
                'time_stay_converter': None,
                'converter_temp': None,
            })
        for meta in mandatory_global_metadata:
            if not self.file.metadata[meta]:
                self.actriserror(
                    "Mandatory global metadata element '{}' missing".format(
                        self.file.internal.ebasmetadata.metadata_keys[meta]['tag']))
            elif (mandatory_global_metadata[meta] is not None and
                    self.file.metadata[meta] !=
                        mandatory_global_metadata[meta]):
                self.actriserror(
                    "Global metadata element '{}' must be '{}'".format(
                        self.file.internal.ebasmetadata.metadata_keys[meta]['tag'],
                        mandatory_global_metadata[meta]))

class EbasTemplateNOxLev1(EbasTemplateBase):
    """
    Ebas template for NOx
    """

    TEMPLATE_NAME = 'NOx lev1'

    def match(self):
        """
        See if this template matches a file.
        """
        if (not self.file.metadata.datalevel or
                not self.file.metadata.datalevel.startswith('1')):
            raise NoTemplate()
        # Contains only NOx variables
        comp_names = [x.metadata.comp_name for x in self.file.variables]
        # identifying components (any of those makes the file a NOx file)
        ident_comps = ('nitrogen_monoxide', 'nitrogen_dioxide', 'NOx')
        # additional components
        add_comps = ('pressure', 'temperature')
        if not any([x in ident_comps for x in comp_names]):
            raise NoTemplate()
        if not all([x in ident_comps + add_comps for x in comp_names]):
            self.error(
                'no match because of additional variobles: {}'.format(
                    ', '.join([x for x in comp_names
                               if x not in ident_comps + add_comps])))
            raise NoTemplate()

        instr_types = set([self.file.get_meta_for_var(vnum, 'instr_type')
                      for vnum in range(len(self.file.variables))])
        if len(instr_types) != 1:
            self.error('only one instrumennt type for all variables allowed')
        self.instr_type = next(iter(instr_types))

        projs = self.file.metadata.projects
        strict_projs = ['ACTRIS', 'ACTRIS_NRT']
        self.actris = any([x in strict_projs for x in projs])
        self.actriserror = self.error if self.actris else self.warning

    def special_checks(self):
        """
        Special checks which cannot be done in the defailt checks.
        """
        if self.instr_type == 'chemiluminescence_molybdenum' and self.actris:
            self.error(
                'Instrument type {} not apporved by ACTRIS'.format(
                    self.instr_type))

        for vnum, var in enumerate(self.file.variables):
            comp = var.metadata.comp_name
            stat = self.file.get_meta_for_var(vnum, 'statistics')
            file_vnum, _, file_metalnum = self.file.msgref_vnum_lnum(vnum)
            if (comp in ('nitrogen_monoxide', 'nitrogen_dioxide', 'NOx') and
                    stat == 'arithmetic mean'):
                cal_scale = self.file.get_meta_for_var(vnum, 'cal_scale')
                if not cal_scale and comp != 'NOx':
                    # TODO: shouldn't NOX have Cal. scale NPL+GPT?
                    self.actriserror(
                        ("Variable {}: 'Calibration scale' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                stdtemp = self.file.get_meta_for_var(vnum, 'vol_std_temp')
                if not stdtemp:
                    self.actriserror(
                        ("Variable {}: 'Volume std. temperature' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                elif not isinstance(stdtemp, float):
                    self.actriserror(
                        ("Variable {}: 'Volume std. temperature' metadata "
                         "must be numeric").format(file_vnum),
                        lnum=file_metalnum)
                stdpres = self.file.get_meta_for_var(vnum, 'vol_std_pressure')
                if not stdpres:
                    self.actriserror(
                        ("Variable {}: 'Volume std. pressure' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                elif not isinstance(stdpres, float):
                    self.actriserror(
                        ("Variable {}: 'Volume std. pressure' metadata "
                         "must be numeric").format(file_vnum),
                        lnum=file_metalnum)
        checkvariables = [
            {
                'comp_name': 'pressure',
                'matrix': 'instrument',
                'characteristics': {
                    'Location': 'inlet',
                }
            },
            {
                'comp_name': 'temperature',
                'matrix': 'instrument',
                'characteristics': {
                    'Location': 'inlet',
                }
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'arithmetic mean'
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'expanded uncertainty 2sigma'
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'precision'
            },
            {
                'comp_name': 'nitrogen_monoxide',
                'statistics': 'detection limit'
            },
        ]
        checkvariables_converter = [
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'arithmetic mean'
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'expanded uncertainty 2sigma'
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'precision'
            },
            {
                'comp_name': 'nitrogen_dioxide',
                'statistics': 'detection limit'
            },
            {
                'comp_name': 'NOx',
                'statistics': 'arithmetic mean'
            },
            {
                'comp_name': 'NOx',
                'statistics': 'expanded uncertainty 2sigma'
            },
            {
                'comp_name': 'NOx',
                'statistics': 'precision'
            },
            {
                'comp_name': 'NOx',
                'statistics': 'detection limit'
            },
        ]
        if self.instr_type != 'chemiluminescence_photometer':
            checkvariables += checkvariables_converter

        # check if all variables are included (and appear exactly once)
        for elem in checkvariables:
            try:
                var = self.file.find_variable(elem)
            except ValueError as excpt:
                # variable is either missing, or more then one variable matches
                # "flatten" the characteristics:
                new = {x: elem[x] for x in elem if x != 'characteristics'}
                if 'characteristics' in elem:
                    new.update({x: elem['characteristics'][x]
                                for x in elem['characteristics']})
                self.actriserror("{}: {}".format(
                    str(excpt),
                    ', '.join(['='.join(
                        (self.file.internal.ebasmetadata.metadata_keys[x]['tag']
                         if x in self.file.internal.ebasmetadata.metadata_keys
                         else x, new[x])) 
                         for x in new.keys()])))
        # check for extrs variables:
        for vnum, unused_ in enumerate(self.file.variables):
            file_vnum, _, file_metalnum = self.file.msgref_vnum_lnum(vnum)
            if not any([self.file.match_variable(vnum, elem)
                        for elem in checkvariables]):
                # variable is not allowed
                self.error(
                    "Variable {}:  variable is not allowed".format(file_vnum),
                    lnum=file_metalnum)

        # check mandatory metadata:
        mandatory_global_metadata = {
            'ozone_corr': 'Not corrected for reaction with O3 in the inlet',
            'watervapor_corr': 'Not corrected for water vapor quenching in CLD',
        }
        #if self.instr_type != 'chemiluminescence_photometer':
        #    mandatory_global_metadata.update({
        #    })
        for meta in mandatory_global_metadata:
            if not self.file.metadata[meta]:
                self.actriserror(
                    "Mandatory global metadata element '{}' missing".format(
                        self.file.internal.ebasmetadata.metadata_keys[meta]['tag']))
            elif (mandatory_global_metadata[meta] is not None and
                    self.file.metadata[meta] !=
                        mandatory_global_metadata[meta]):
                self.actriserror(
                    "Global metadata element '{}' must be '{}'".format(
                        self.file.internal.ebasmetadata.metadata_keys[meta]['tag'],
                        mandatory_global_metadata[meta]))
