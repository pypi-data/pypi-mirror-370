"""
Base classes for (file) I/O.

$Id: write.py 2739 2021-11-19 23:46:25Z pe $
"""

import sys, os, math
from six import PY2
from nilutility.string_helper import list_joiner
from nilutility.datetime_helper import DatetimeISO8601Duration
from ebas.domain.basic_domain_logic.time_period import period_code_iso8601_duration
from .consolidate import EbasFileConsolidate
from ...fileset.xmlwrap import xmlwrap_fileheader, xmlwrap_filetrailer
from ebas.domain.masterdata.dl import EbasMasterDL
from ebas.domain.masterdata.pr import EbasMasterPR
from ebas.domain.masterdata.ps import EbasMasterPS
import json
from ..base import FLAGS_ONE_OR_ALL


# constants for variable types (used internally)
VAL = 0  # measurement values
FLG = 1  # flags
MTA = 2  # metadata

class EbasFileWriteCDM(EbasFileConsolidate):  # pylint: disable=W0223
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Partial class for EbasFile (Base class for file objects).
    This part handles methods used for output of CDM related file formats
    (NetCDF, OPeNDAP).
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the object.
        """
        super(EbasFileWriteCDM, self).__init__(*args, **kwargs)
        # cdm variables, provided by gen_cdm_variables and used by derived
        # classes (NetCDF, OPeNDAP)
        # self.cdm_variables data structure:
        # self.cdm_variables =
        # 'cdm_varname' : {
        #         'var_type' = VAL | FLG | MTA
        #         'cdm_varname' = <key>
        #         'ebas_variables' = [index, index, ...]
        #         'dimensions' = (name, name, ....)
        #         'dimextents' = ([value, value, ...], ...)
        #                          ... for each dimension
        #         'variable_dimensions': (((dimension, value), ...), ...)
        #                          ... for each variable (for each dimension)
        #         'slice': None,
        # }
        self.cdm_variables = None


    def _global_project_list(self):
        """
        Returns a unique, sorted list of global projects.
        Parameters:
            None
        Returns:
            list of strings (proj acronym)
        """
        # generate a sorted list of unique projects
        projset = set()
        for val in self.get_metadata_set('projects'):
            for proj in val:
                projset.add(proj)
        return sorted(list(projset))

    def _global_open_access(self):
        """
        Returns true/flas whether ALL data in the file re open.
        Parameters:
            None
        Returns:
            bool
        """
        for val in self.get_metadata_set('projects'):
            for proj in val:
                projset.add(proj)
        return sorted(list(projset))

    def generate_global_acdd_attributes(self, metadata_options):
        """
        Generator for global ACDD (including netCDF COARDS and CF) attributes.
        ACDD is compatible with netCDF basic metadata and CF metadata:
            "The NetCDF User Guide (NUG) provides basic recommendations for
            creating NetCDF files; the NetCDF Climate and Forecast Metadata
            Conventions (CF) provides more specific guidance.
            The ACDD builds upon and is compatible with these conventions;
            it may refine the definition of some terms in those conventions,
            but does not preclude the use of any attributes defined by the NUG
            or CF."
            http://wiki.esipfed.org/index.php/Category:Attribute_Conventions_
                Dataset_Discovery
        Parameters:
            None
        Returns:
            generator, each a tuple (global_attriubute_name, value)
        """
        yield ('Conventions', "CF-1.8, ACDD-1.3")
        yield ('featureType', "timeSeries")

        if self.metadata.comp_name:
            what = self.metadata.comp_name
        elif self.metadata.instr_type:
            what = self.metadata.instr_type
        elif self.metadata.matrix:
            what = self.metadata.matrix
        else:
            what = "diverse"

        # title: CF, ACDD:
        yield ('title', self.title())

        # keywords: ACDD
        keywords = set()
        if self.metadata.station_name:
            keywords.add(self.metadata.station_name)
        keywords.add(self.metadata.station_code)
        for val in self.get_metadata_set('comp_name', exclude_aux=True):
            keywords.add(val)
        for val in self.get_metadata_set('matrix', exclude_aux=True):
            keywords.add(val)
        compdesc_list = []
        for val in self.get_metadata_set(
                ('regime', 'matrix', 'comp_name', 'statistics', 'unit',
                 'datalevel'), exclude_aux=True):
            desc = "{} in {}".format(val[2], val[1])
            if None not in val:
                cfname, _ = self.cfparams(*val)
                if cfname:
                    keywords.add(cfname)
                    desc += " ({})".format(cfname)
            compdesc_list.append(desc)
        projects = self._global_project_list()  # use variable, reuse later
        for proj in projects:
            keywords.add(proj)
        yield ('keywords', u', '.join(keywords))

        # id/naming_authority: ACDD
        yield ('id', self.metadata.filename)
        yield ('naming_authority', 'no.nilu.ebas')

        # project, recommended global attribute ACDD (specified that multiple
        # projects should be separated by commas)
        yield ('project', u', '.join(projects))
        
        # Acknowledgement, recommended global attribute ACDD
        yield ('acknowledgement', self.get_metadata_set('acknowledgements'))
        
        yield ('doi',
               [a for b in self.get_metadata_set('doi_list') for a in b])

        # license: recommended global attribute ACDD
        license = "https://creativecommons.org/licenses/by/4.0/"
        for fil in [elem[2] for elem in self.metadata_intervals
                    if elem[2] is not self]:
            if fil.metadata.license != license:
                yield ('license', 'Various, see detailed metadata')
                break
        else:
            yield ('license', license)

        # TODO: Find a new place for data policy!
        # we need to specify the data policy in the ISO19139 document,
        # which is mapped by TDS from the NetCDF attributes
        # This used the license element so far, we need a differenet!
        # datapol = []
        # for proj in projects:
        #     pr_ = EbasMasterPR()[proj]
        #     datapol.append("{}: {}".format(
        #         proj, pr_.PR_DATAPOLICY if pr_.PR_DATAPOLICY else ''))
        # yield ('license', u', '.join(datapol))

        # citation (not in ACDD). Just use ebas_citation for now
        if self.metadata.citation:
            yield ('citation', self.metadata.citation)
        

        # summary: ACDD recommended attribute
        yield (
            'summary',
            u"{}. These measurements are gathered as a part of the following projects {} and they are stored in the EBAS database (http://ebas.nilu.no/). Parameters measured are: {}".format(
                self.title(),
                ', '.join(projects),
                ', '.join(compdesc_list)))
        
        # source: CF, ACDD
        yield (
            'source',
            'airborn observation' if self.metadata.station_code.endswith('A') \
            else 'surface observation')

        # institution: ACDD
        inst = ''
        for org in self.get_metadata_set('org'):
            lst = [
                org['OR_CODE'],
                org['OR_NAME'],
                org['OR_ACRONYM'],
                org['OR_UNIT'],
                org['OR_ADDR_LINE1'],
                org['OR_ADDR_LINE2'],
                org['OR_ADDR_ZIP'],
                org['OR_ADDR_CITY'],
                org['OR_ADDR_COUNTRY']]
            i = 0
            while i < len(lst):
                if lst[i] is None:
                    del lst[i]
                else:
                    i += 1
            inst += u', '.join(lst)
        yield ('institution', inst)

        # processing level: ACDD
        if self.metadata.datalevel:
            dl_ = EbasMasterDL()[self.metadata.datalevel]
            yield (
                'processing_level',
                "{}: {} ({})".format(self.metadata.datalevel,
                                     dl_.DL_NAME, dl_.DL_DESC))

        # date_created: ACDD
        revdate = max(list(self.get_metadata_set('revdate')))
        yield('date_created', revdate.strftime('%Y-%m-%dT%H:%M:%S UTC'))
        # date_metadata_modified: ACDD
        yield('date_metadata_modified',
              revdate.strftime('%Y-%m-%dT%H:%M:%S UTC'))

        # creator_name, creator_email, creator_institution, creator_type: ACDD
        # use Data Originator as creator_type person
        lst = []
        if self.metadata.originator is not None:
            for ps_ in self.metadata.originator:
                elem = []
                elem.append("{} {}".format(ps_.PS_FIRST_NAME, ps_.PS_LAST_NAME))
                elem.append(ps_.PS_EMAIL)
                elem.append(", ".join([
                    x for x in (ps_.PS_ORG_NAME, ps_.PS_ORG_UNIT, ps_.PS_ORG_ACR)
                    if x]))
                lst.append(elem)
        if lst:
            yield (
                'creator_name',
                list_joiner([x[0] for x in lst], ',', insert_space=True))

            yield ('creator_type', 'person')
            yield (
                'creator_email',
                list_joiner([x[1] for x in lst], ',', insert_space=True))
            yield (
                'creator_institution',
                list_joiner([x[2] for x in lst], ',', insert_space=True))

        # contributor_name, contributor_role: ACDD
        # use Data Submitter as contributoe_role data submitter
        lst = []
        if self.metadata.submitter is not None:
            for ps_ in self.metadata.submitter:
                lst.append(u"{} {}".format(ps_.PS_FIRST_NAME, ps_.PS_LAST_NAME))
            if lst:
                yield (
                    'contributor_name',
                    list_joiner(lst, ',', insert_space=True))
                yield (
                    'contributor_role',
                    list_joiner(['data submitter'] * len(lst), ',',
                                insert_space=True))

        # publisher_name, publisher_email, publisher_url, publisher_type,
        # publisher_institution: ACDD
        yield ('publisher_type', 'institution')
        yield (
            'publisher_name',
            'NILU - Norwegian Institute for Air Research, ATMOS, EBAS')
        # publisher_institution should be the same as publisher_name if
        # publisher_type is institution.
        yield (
            'publisher_institution',
            'NILU - Norwegian Institute for Air Research, ATMOS, EBAS')
        yield ('publisher_email', 'ebas@nilu.no')
        yield ('publisher_url', 'http://ebas.nilu.no/')

        # geospatial_bounds,
        # geospatial_lat_min, geospatial_lat_max, geospatial_lon_min,
        # geospatial_lon_max, geospatial_vertical_min, geospatial_vertical_max,
        # geospatial_vertical_positive:
        #  ALL ACDD
        if not self.metadata.station_code.endswith('A'):
            # this works only for stations, TODO: airplane obs
            latlonalt = set()
            latmin, latmax, lonmin, lonmax, altmin, altmax = (None, ) * 6
            for i in range(len(self.variables)):
                pos = [self.get_meta_for_var(i, 'mea_latitude'),
                       self.get_meta_for_var(i, 'mea_longitude'),
                       self.get_meta_for_var(i, 'mea_altitude')]
                if pos[0] is None:
                    pos[0] = self.get_meta_for_var(i, 'station_latitude')
                if pos[1] is None:
                    pos[1] = self.get_meta_for_var(i, 'station_longitude')
                if pos[2] is None:
                    pos[2] = self.get_meta_for_var(i, 'station_altitude')
                if not None in pos:
                    latlonalt.add(tuple(pos))
                if pos[0] is not None:
                    latmin = min(latmin, pos[0]) if latmin is not None \
                    else pos[0]
                    latmax = max(latmax, pos[0]) if latmax is not None \
                    else pos[0]
                if pos[1] is not None:
                    lonmin = min(lonmin, pos[1]) if lonmin is not None \
                    else pos[1]
                    lonmax = max(lonmax, pos[1]) if lonmax is not None \
                    else pos[1]
                if pos[2] is not None:
                    altmin = min(altmin, pos[2]) if altmin is not None \
                    else pos[2]
                    altmax = max(altmax, pos[2]) if altmax is not None \
                    else pos[2]
            if len(latlonalt) > 1:
                yield (
                    'geospatial_bounds',
                    "MULTIPOINT Z (" + ', '.join(["({} {} {})".format(*x)
                                                  for x in latlonalt]) + ")")
            elif len(latlonalt) == 1 and \
                    list(latlonalt)[0] != (None, None, None):
                yield (
                    'geospatial_bounds',
                    "POINT Z ({} {} {})".format(*(list(latlonalt)[0])))
            else:
                yield ('geospatial_bounds', "POINT Z EMPTY")
            yield ('geospatial_bounds_crs', "EPSG:4979")


            if latmin is not None:
                yield ('geospatial_lat_min', latmin)
            if latmax is not None:
                yield ('geospatial_lat_max', latmax)
            if lonmin is not None:
                yield ('geospatial_lon_min', lonmin)
            if lonmax is not None:
                yield ('geospatial_lon_max', lonmax)
            if altmin is not None:
                yield ('geospatial_vertical_min', altmin)
            if altmax is not None:
                yield ('geospatial_vertical_max', altmax)
            yield ('geospatial_vertical_positive', "up")

        yield (
            'time_coverage_start',
            self.sample_times[0][0].strftime('%Y-%m-%dT%H:%M:%S UTC'))

        yield (
            'time_coverage_end',
            self.sample_times[-1][-1].strftime('%Y-%m-%dT%H:%M:%S UTC'))

        dur = DatetimeISO8601Duration()
        dur.diff(self.sample_times[0][0], self.sample_times[-1][-1])
        yield ('time_coverage_duration', dur.format(2))

        dur = period_code_iso8601_duration(self.metadata.resolution)
        yield ('time_coverage_resolution', dur.format(2))

        # timezone: neither CF nor ACDD but definitely useful
        yield ('timezone', "UTC")

    def generate_global_ebas_attributes(self, version=2):
        """
        Generator for global EBAS attributes.
        Those are:
        in Version 1:
         - attributes which contain important information we need for
           further mapping into other metadata standards
         - an attribute 'ebas_metadata' which contains all global EBAS metadata
           as json encoded string
        in Version2:
         - all gloabal metadata with the nc_tag names as ebas_XXX attributes
        Parameters:
            version    attribute and metadata verision (EBAS NetCDF V1 or V2)
                       (the plan is to discontinue V1 after some time, then
                       all this can be thrown away and the code cleaned up)
        Returns:
            generator, each a tuple (global_attriubute_name, value)
        """
        if version == 1:
            # those attributes were implemented in V1, but in V2 they come with
            # the default metadata handling together with all the other metadata
            # in global attributes
            projects = self._global_project_list()
            name = []
            description = []
            contact_name = []
            contact_email = []
            for proj in projects:
                pr_ = EbasMasterPR()[proj]
                name.append(pr_.PR_NAME if pr_.PR_NAME else '')
                description.append(pr_.PR_DESC if pr_.PR_DESC else '')
                if pr_.PS_ID is not None:
                    ps_ = EbasMasterPS()[pr_.PS_ID]
                    contact_name.append(' '.join(
                        [x for x in [ps_.PS_FIRST_NAME, ps_.PS_LAST_NAME]
                         if x]))
                    contact_email.append(ps_.PS_EMAIL if ps_.PS_EMAIL else '')
                else:
                    contact_name.append('')
                    contact_email.append('')
            yield ('ebas_framework_acronym', u', '.join(projects))
            yield ('ebas_framework_name', u', '.join(name))
            yield ('ebas_framework_description', u', '.join(description))
            yield ('ebas_framework_contact_name', u', '.join(contact_name))
            yield ('ebas_framework_contact_email', u', '.join(contact_email))
            # finally, add the file global ebas metadata (common over all
            # variables and time intervals (discontinued in V2)
            yield ('ebas_metadata', self.ebas_metadata_json(version=version))
        else:
            # Version 2:
            # all ebas metadata as separate global attributes with name:
            #  ebas_<nc_tag>
            for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(
                    self, nc_tags=True):
                if meta[1] != "":
                    yield ('ebas_'+meta[0], meta[1])
            # additional for V2: unfortunately we need the V1 style
            # ebas_metadata variable for backward compatibility (NextGEOSS)
            # TODO: get rid of this requirement!
            yield ('ebas_metadata', self.ebas_metadata_json(version=1))

    def generate_variable_ebas_attributes(self, var_index):
        """
        Generator for EBAS variable attributes. Currently only used in NetCDF V2
        Those are:
         - all variable metadata for variable vnum with the nc_tag names as
           ebas_XXX attributes
        Parameters:
            var_index   variable number in EbasFile object
        Returns:
            generator, each a tuple (variable_attriubute_name, value)
        """
        # Version 2:
        for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(
                self, var_index=var_index, explicit_only=False, nc_tags=True):
            if meta[1] != "":
                yield ('ebas_'+meta[0], meta[1])

    def ebas_metadata_json(self, var_index=None, version=2):
        """
        Encodes the ebas metadata for a variable in json.
        Parameters:
            var_index   variable number in nasa ames object
                        Use file global metadata if var_index==None
        Returms:
            The json encoded metadata
        """
        from collections import OrderedDict
        ebas_metadata = OrderedDict()
        for meta in self.internal.ebasmetadata.metadata_list_tag_valuestr(
                self, var_index=var_index, explicit_only=False,
                nc_tags=False if version == 1 else True):
            if meta[1] != "":
                ebas_metadata[('ebas_' if version != 1 else '') + meta[0]] = \
                    meta[1]
        # characteristics: are implemented as dimensions
        # so usually this here will only apply to the _ebasmetadata variables
        # (where we have metadata for each dimension).
        # In V1 we have a global ebas_metadata attribute, but usually
        # characteristics will not be file global (if more than one single
        # DS is exported)
        # In V2, we do not generate the global JSON attribute at all
        meta = self.metadata if var_index is None \
            else self.variables[var_index].metadata
        if 'characteristics' in meta and meta.characteristics is not None:
            for char in meta.characteristics.sorted():
                ebas_metadata[
                    ('ebas_characteristic ' if version != 1 else '') + \
                    char.CT_TYPE] = char.value_string()
        # json.dumps with ensure_ascii=False keeps unicode encoding, and does
        # not ' \uXXXX' encode it).
        # encoding: just to be sure, if there are str instances with
        # characters > 127 in the input objects, they are considered utf-8
        # (should not be the case, as ebas operates with the unicode type
        # internally)
        return json.dumps(ebas_metadata, indent=4, ensure_ascii=False)

    @staticmethod
    def cfparams(regime, matrix, comp_name, statistics, unit, datalevel):
        """
        Get the CF name for an EBAS  regime/matrix/component combination.
        Parameters:
            regime       EBAS regime code
            matrix       EBAS matrix name
            comp_name    EBAS component name
            unit         EBAS unit
            statistics   EBAS statistics code
                         (can overrule unit, cfname and cfunit)
            datalevel    used for exceptional PM (masterdata not in database,
                         for lev0 and lev1)
        Returns:
            CF name
            None if no CF name exists
        TODO: this should maybe go somewhere else, not in IO?
        """
        from ebas.domain.masterdata.pm import EbasMasterPM
        pm_ = EbasMasterPM()
        # pm masterdata lookup with additional data level:
        # if pm is not defined in DB masterdata, lookup in exceptional
        # masterdata (data level dependent, not meant to be imported)
        elem = pm_[(regime, matrix, comp_name, statistics, datalevel)]
        if elem['PM_UNIT'] != unit:
            # unit converted on export!
            elem = pm_.exceptional_unit_exp((
                regime, matrix, comp_name, unit))
        return (elem['PM_CFNAME'], elem['PM_CFUNIT'])

    def cell_methods(self, var_index):
        """
        Get the cell_methods attribute (CF) for a variable.
        Parameters:
            var_index   variable number in EbasIO object
        Returms:
            the respective cell_methods attribute value
        """
        # perfect translations, where CF has actually a term:
        translations = {
            #'68.27% lower confidence bound': ,
            #'68.27% upper confidence bound': ,
            #'absolute error': ,
            #'accuracy': ,
            'arithmetic mean': 'mean',
            #'detection limit': 'det.lim.',
            #'expanded uncertainty 2sigma': 'ExpUnc2s',
            #'expanded uncertainty 3sigma': 'ExpUnc3s',
            #'geometric mean': 'gmean',
            'maximum': 'maximum',
            'median': 'median',
            'minimum': 'minimum',
            #'percentile:15.87': 'prec1587',
            #'percentile:84.13': 'perc8413',
            #'precision': 'precision',
            'stddev': 'standard_deviation',
            'uncertainty': 'uncertainty',
            'sample count': 'sample_count',
        }
        stat = self.get_meta_for_var(var_index, 'statistics')
        if self.get_meta_for_var(var_index, 'comp_name').startswith(
                'precipitation_amount') and stat == 'arithmetic mean':
            # special case: precipitation amount is a sum
            return "time: sum"
        if stat in translations:
            return "time: {}".format(translations[stat])
        return "time: {}".format(stat)


    def var_dimensions(self, var_index):
        """
        Get the dimensions (and their value) for a variable.
        Parameters:
            var_index   variable number in EbasIO object
        Returms:
            tupel ([dimensions], {dimvals})
                dimensions is a list of dimension names
                dimvals is a dict (key=dimension names)
            example: (['D'], {'D': 28.5})
        """
        dimensions = []
        dimval = {}
        dcdict = self.get_characteristics_for_var(var_index)

        # special casefor particle diameter: Dmin and Dmax are in reality _one_
        # dimension, convert or D (geom. mean):
        if 'Dmin' in dcdict and 'Dmax' in dcdict and 'D' not in dcdict:
            dcdict['D'] = math.sqrt(dcdict['Dmin'] * dcdict['Dmax'])
        if 'Dmin' in dcdict and 'D' in dcdict:
            del dcdict['Dmin']
        if 'Dmax' in dcdict and 'D' in dcdict:
            del dcdict['Dmax']
        if dcdict:
            from ebas.domain.masterdata.dc import DCListBase
            sortorder = DCListBase.META['SORTORDER']
            for char in sorted(
                    [(sortorder.index(k) if k in sortorder else 999, k)
                     for k in dcdict]):
                #@ fix the dimension name. / not allowed in NetCDF
                fix_dim = char[1].replace('/','_')
                dimensions.append(fix_dim)
                dimval[fix_dim] = dcdict[char[1]]
        return (dimensions, dimval)

    def cdm_flag_dimsize(self, cdm_var):
        """
        Get the size needed for the flag dimension of a _qc variable.
        Parameters:
            cdm_var    the cdm variable description (dict)
        Returns:
            None
        """
        return max([1] + [len(flags)
                          for var_ind in cdm_var['ebas_variables']
                          for flags in self.variables[var_ind].flags])
        
    def gen_cdm_variables(self):
        """
        Find a unique variable name for each variable
        """
        def _statistics_ext(stat_value):
            """
            Generate a short version of statistics metadata for use in variable
            name.
            Parameters:
                stat_value    value of metadata element 'statistics'
            Return:
                short version to be used as extension in variable name
            """
            statistics = {
                '68.27% lower confidence bound': '6827lcb',
                '68.27% upper confidence bound': '6827ucb',
                'absolute error': 'abs_err',
                'accuracy': 'accuracy',
                'arithmetic mean': 'amean',
                'detection limit': 'det_lim',
                'expanded uncertainty 2sigma': 'ExpUnc2s',
                'expanded uncertainty 3sigma': 'ExpUnc3s',
                'geometric mean': 'gmean',
                'maximum': 'max',
                'median': 'median',
                'minimum': 'min',
                'percentile:15.87': 'prec1587',
                'percentile:84.13': 'perc8413',
                'precision': 'precision',
                'stddev': 'stddev',
                'uncertainty': 'uncertainty',
                }
            if stat_value in statistics:
                return statistics[stat_value]
            else:
                return stat_value.replace(' ', '_')

        def _unit_ext(unit_value):
            """
            Generate a modified version of unit metadata for use in variable
            name as an extension. (Background: / is not 100% supported as
            variable name, and is not allowd at all as dimension (flag vars
            will have an additional dimesnion which is generated from the var
            name))
            Parameters:
                unit          value of metadata element 'unit'
            Return:
                modified version to be used as extension in variable name
                this will conform to both var name and dim name conventions
            """
            return unit_value.replace('/', '_per_')

        # frame is a helper structure for sorting and structuring the variables
        # framekey=(compname, matrix, unit, stat, dimensions)
        # dimkey = tupel(tupel(dim: dimval), ...)
        # frame =  {
        #     framekey:
        #         [
        #             'cdm_varname':
        #             'ebas_variables' = {dimkey: var_index}
        #         ]}
        frame = {}
        # find possible additional dimensions (i.e. characteristics):
        for i in range(len(self.variables)):
            dimensions, dimval = self.var_dimensions(i)
            key = (self.get_meta_for_var(i, 'comp_name'),
                   self.get_meta_for_var(i, 'matrix'),
                   self.get_meta_for_var(i, 'unit'),
                   self.get_meta_for_var(i, 'statistics'),
                   tuple(dimensions))
            dimkey = tuple((dim, dimval[dim]) for dim in dimensions)
            if key in frame:
                # there is already at least one variable with the same core data
                # note: dimensions is correctly sorted, so will be dimkey
                for elem in frame[key]:
                    if dimkey in elem['ebas_variables']:
                        # See comment NOTE_DUPLICATE_VARIABLES below!
                        # Same comp, matrix, unit, statistics, dimensions
                        # and duplicate value for dimensions?
                        # This might be a co-located measurement (2 instruments
                        # 2 methods)?
                        # Else, we need to add an element to the frame key!
                        # Here we continue, which means there is another cdm
                        # variable already in the list, or we create a new one  .
                        continue
                    else:
                        # add this to ebas_variables:
                        elem['ebas_variables'][dimkey] = i
                        break
                else:
                    # add a new variable
                    frame[key].append({
                        'cdm_varname': self.get_meta_for_var(i, 'comp_name'),
                        'ebas_variables': {dimkey: i}})
            else:
                # add a new key:
                frame[key] = [{
                    'cdm_varname': self.get_meta_for_var(i, 'comp_name'),
                    'ebas_variables': {dimkey: i}}]

        # Solve duplicate cdm variable names:
        for key in frame.keys():
            jdiff = set()
            change = set()
            for other in frame.keys():
                if key == other:
                    continue
                # We only need to check the first list element, the other
                # elements are numbered sequentially.
                # (See comments NOTE_DUPLICATE_VARIABLES above and below)
                if frame[key][0]['cdm_varname'] == \
                   frame[other][0]['cdm_varname']:
                    change.add(key)
                    change.add(other)
                    if key[1] != other[1]:
                        jdiff.add('matrix')
                    if key[2] != other[2]:
                        jdiff.add('unit')
                    if key[3] != other[3]:
                        jdiff.add('statistics')
                    if key[4] != other[4]:
                        jdiff.add('dimensions')
                    if not jdiff:
                        raise RuntimeError(
                            'duplicate cdm variable name: {}'.format(
                                frame[key][0]['cdm_varname']))
            for other in change:
                if 'matrix' in jdiff:
                    for elem in frame[other]:
                        elem['cdm_varname'] += '_' + other[1]
                if 'unit' in jdiff:
                    for elem in frame[other]:
                        elem['cdm_varname'] += '_' + _unit_ext(other[2])
                if 'statistics' in jdiff:
                    for elem in frame[other]:
                        elem['cdm_varname'] += '_' + _statistics_ext(other[3])
                if 'dimensions' in jdiff:
                    for elem in frame[other]:
                        if other[4]:
                            elem['cdm_varname'] += '_' + '_'.join(other[4])
        # Double check: still dulpicate variables?
        for key in frame.keys():
            for other in frame.keys():
                if key == other:
                    continue
                if frame[key][0]['cdm_varname'] == \
                   frame[other][0]['cdm_varname']:
                    raise RuntimeError(
                        'duplicate cdm variable name: {}'.format(
                            frame[key][0]['cdm_varname']))

        # See comment NOTE_DUPLICATE_VARIABLES above!
        # Sequentially number duplicate cdm variables within one framekey:
        for key in frame:
            if len(frame[key]) > 1:
                for i, elem in enumerate(frame[key]):
                    elem['cdm_varname'] += '_{}'.format(i)

        # now the cdm_varnames are unique, lets build the cdm var structure:
        # structure layout see __init__
        self.cdm_variables = {}
        for key in frame.keys():
            for elem in frame[key]:
                newvar = \
                    {
                        'var_type': VAL,
                        'cdm_varname': elem['cdm_varname'],
                        'ebas_variables': [],
                        'dimensions': key[4],
                        'dimextents': [[] for i in range(len(key[4]))],
                        'variable_dimensions': []
                    }
                for dimkey in sorted(elem['ebas_variables']):
                    newvar['ebas_variables'].append(
                        elem['ebas_variables'][dimkey])
                    for i in range(len(dimkey)):
                        if dimkey[i][1] not in newvar['dimextents'][i]:
                            newvar['dimextents'][i].append(dimkey[i][1])
                    newvar['variable_dimensions'].append(dimkey)
                self.cdm_variables[elem['cdm_varname']] = newvar.copy()
                self.cdm_variables[elem['cdm_varname']+'_qc'] = newvar.copy()
                self.cdm_variables[elem['cdm_varname']+'_qc']['var_type'] = FLG
                self.cdm_variables[elem['cdm_varname']+'_qc']['flag_dimsize'] =\
                    self.cdm_flag_dimsize(
                        self.cdm_variables[elem['cdm_varname']+'_qc'])
                self.cdm_variables[elem['cdm_varname']+'_qc']['cdm_varname'] +=\
                    '_qc'
                self.cdm_variables[elem['cdm_varname']+'_ebasmetadata'] = \
                    newvar.copy()
                self.cdm_variables[elem['cdm_varname']+'_ebasmetadata']\
                    ['var_type'] = MTA
                self.cdm_variables[elem['cdm_varname']+'_ebasmetadata']\
                    ['cdm_varname'] += '_ebasmetadata'

        # check if variable with same dimensions names have the same diemstein
        # entents:
        cdm_vnames = list(self.cdm_variables.keys())
        for vind1 in range(len(cdm_vnames)):
            var1 = self.cdm_variables[cdm_vnames[vind1]]
            for vind2 in range(vind1+1, len(cdm_vnames)):
                var2 = self.cdm_variables[cdm_vnames[vind2]]
                for dind1 in range(len(self.cdm_variables[cdm_vnames[vind1]]
                                       ['dimensions'])):
                    for dind2 in range(len(self.cdm_variables[cdm_vnames[vind2]]
                                           ['dimensions'])):
                        if var1['dimensions'][dind1] == \
                                var2['dimensions'][dind2] and \
                           var1['dimextents'][dind1] != \
                                var2['dimextents'][dind2]:
                            # if the dimension name is the same, but the
                            # dimension extents is different, use a new name
                            # for the dimension:
                            # tuple is immutable, convert to list and back...
                            lst = list(var2['dimensions'])
                            lst[dind2] += 'x'
                            var2['dimensions'] = tuple(lst)
                            var2['variable_dimensions'] = \
                                [tuple(y[1] if y[0]!=0
                                       else (y[1][0]+'x', y[1][1])
                                       for y in enumerate(x))
                                 for x in var2['variable_dimensions']]
                            lst = list(var2['variable_dimensions'][dind2])

class EbasFileWrite(EbasFileWriteCDM):  # pylint: disable=W0223
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Partial class for EbasFile (Base class for file objects).
    This part handles generic methods for file output.
    """

    def prepare_write(
            self, open_file, createfiles=False, destdir=None, xmlwrap=False,
            fileobj=None, flags=FLAGS_ONE_OR_ALL, datadef='EBAS_1.1',
            metadata_options=0, suppress=0):
        """
        Prepare the IO object for writing.
        Used for all output formats (Nasa Ames, CSV, NetCDF, OPeNDAP, XML)
        Parameters:
            open_file  wheter the oputut file should be opened and the file
                       handle be returned. (Should net be done for certain
                       types of output objects (e.g. EbasNetCDF) or on the
                       atomic files within an EbasJoinedFile container)
            createfiles   write to file? else write to stdout
                          (special case for fileobj)
            destdir       destination directory path for files
            xmlwrap       wrap output in xml container
            fileobj       write to filehandle
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
            datadef       ebas data definition (EBAS_1 or EBAS_1.1)
            metadata_options
                          options for output, bitfield:
                          currently only EBAS_IOMETADATA_OPTION_SETKEY
            suppress      suppress selected consolidations (bitfield):
                              SUPPRESS_SORT_VARIABLES
                              SUPPRESS_METADATA_OCCURRENCE
        Returns
            filehandle (None if not open_file)
        """
        # must be implemented here, because ebasmetadata can't be imported in
        # ..base
        self.metadata.datadef = datadef
        # make sure datadef is not defined in any variable:
        for var in self.variables:
            if 'datadef' in var.metadata:
                del(var.metadata.datadef)
        self.setup_ebasmetadata(datadef, metadata_options)
        # finalize the EbasFile metadata structure:
        self.set_timespec_metadata()
        self.set_default_metadata()
        self.consolidate_metadata(flags=flags, suppress=suppress)
        # set_citation after consolidate_metadata:
        # originators and revdate are consolidated
        self.set_citation(metadata_options)

        self.gen_filename(createfiles, destdir)
        # Used for header and filename if physical file is written).
        # A "genuine" filename is generated already in consolidate_metadata,
        # but this time it's also checked for uniqueness if needed.

        if not createfiles and xmlwrap:
            xmlwrap_fileheader(self.metadata.filename)
        if not open_file:
            return

        if createfiles:
            fnam = self.metadata.filename
            if destdir:
                fnam = os.path.join(destdir, self.metadata.filename)
            if PY2:
                mod = "w"
            else:
                mod = "wb"
            fil = open(fnam, mod)
            self.logger.info("writing to file " + fnam)
        elif fileobj:
            # redirect output to given file-like object
            fil = fileobj
        else:
            if PY2:
                fil = sys.stdout

            else:  # PY3
                from io  import _io
                if isinstance(sys.stdout, _io.TextIOWrapper):
                    # std stream in py3 is an encoding wrapper. We need to use
                    # the unencoded buffer directly in order to write bytes.
                    # We need to check if it's really a TextIOWrapper, otherwise
                    # we get problems with jupyter.
                    fil = sys.stdout.buffer
                else:
                    fil = sys.stdout
        return fil

    @staticmethod
    def finish_write(createfiles, xmlwrap):
        """
        Finish file write.
        Parameters:
            createfiles   output to file or stdout
            xmlwrap       whether the xml wrapper must be closed
        Returns
            None
        """
        if not createfiles and xmlwrap:
            xmlwrap_filetrailer()

    # Methods for the generation of NetCDF like output objetcs
    # (OPeNDAP, NetCDF, ...)
