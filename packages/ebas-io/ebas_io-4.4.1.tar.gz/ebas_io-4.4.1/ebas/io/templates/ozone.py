"""
EBAS submission templates and template checks: Ozone Template
"""

from .base import EbasTemplateBase, NoTemplate


class EbasTemplateOzone(EbasTemplateBase):
    """
    Ebas template for ozone
    """

    TEMPLATE_NAME = 'Ozone'

    def match(self):
        """
        See if this template matches a file.
        """
        # Ozone Template exists only for Lev 2
        # Contains only ozone variables
        comp_names = [x.metadata.comp_name for x in self.file.variables]
        if not any([x == 'ozone' for x in comp_names]):
            raise NoTemplate()
        if not all([x == 'ozone' for x in comp_names]):
            self.warning(
                'Ozone template: no match because of variobles: {}'.format(
                    ', '.join([x.metadata.comp_name
                               for x in self.file.variables
                               if x != 'ozone'])))
            raise NoTemplate()
        if self.file.metadata.datalevel != '2':
            self.warning(
                'Ozone template: no match because of data level {}'.format(
                    self.file.metadata.datalevel))
            raise NoTemplate()

    def special_checks(self):
        """
        Special checks which cannot be done in the defailt checks.
        """
        for vnum, var in enumerate(self.file.variables):
            if var.metadata.comp_name == 'ozone':
                file_vnum, _, file_metalnum = self.file.msgref_vnum_lnum(vnum)
                if not self.file.get_meta_for_var(vnum, 'vol_std_temp'):
                    self.error(
                        ("Variable {}: 'Volume std. temperature' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                if not self.file.get_meta_for_var(vnum, 'vol_std_pressure'):
                    self.error(
                        ("Variable {}: 'Volume std. pressure' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)
                if not self.file.get_meta_for_var(vnum, 'abs_cross_section'):
                    self.error(
                        ("Variable {}: 'Absorption cross section' metadata "
                         "missing").format(file_vnum), lnum=file_metalnum)

                # cross check standard method and absorption cross section:
                # 2023-06-07: AGH maybe this is not true, double check GAW 209!
                # from ebas.io.file.basefile.base import isvalid
                # acs = self.file.get_meta_for_var(vnum, 'abs_cross_section')
                # sme = self.file.get_meta_for_var(vnum, 'std_method')
                # if (sme == 'SOP=GAW_209(2013)' and isvalid(acs) and 
                #     acs != 'Hearn, 1961'):
                #     self.error(
                #         ("Variable {}: Standard method 'SOP=GAW_209(2013)' "
                #          "does not allow absorption cross section '{}' (only "
                #          "'Hearn, 1961')").format(
                #              file_vnum, acs), lnum=file_metalnum)
