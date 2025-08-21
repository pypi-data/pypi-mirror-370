"""
$Id: write.py 2519 2020-10-30 16:13:09Z pe $

EBAS OPeNDAP Module: output functionality
"""

import os
import sys
import itertools
from six import string_types
from six.moves import urllib
from .base import EbasOPeNDAPBase
from ..base import FLAGS_ALL
from ...ebasmetadata import EbasMetadata
from ebas.domain.basic_domain_logic.time_period import estimate_period_code, \
    period_code_iso8601_duration
from ..base import EBAS_IOFORMAT_OPENDAP
from .base import EBAS_OPENDAP_REQUESTTYPE_DAS, \
    EBAS_OPENDAP_REQUESTTYPE_DATA
try:
    from pydap.exceptions import ConstraintExpressionError
    from pydap.model import DatasetType, BaseType, GridType, StructureType, \
        SequenceType
    from pydap.lib import walk, get_var
    from pydap.responses.dods import DODSResponse
    import numpy as np
except ImportError:
    # pydap and numpy are NOT dependencies for ebas-io. Thus, ebas-io can
    # be used w/o this modules.
    # However the functionality is limited. An error message will be thrown
    # in the entry points of ebas opendap writer (methods write, make_dataset)
    pass

import datetime
from ...fileset.xmlwrap import xmlwrap_fileheader, xmlwrap_filetrailer
from nilutility.string_helper import list_joiner
from nilutility.datetime_helper import DatetimeISO8601Duration, DatetimeInterval

class EbasOPeNDAPPartialWrite(EbasOPeNDAPBase):
    """
    Conversion of EBAS data to OPeNDAP
    """

    def write(self, createfiles=False, destdir=None, xmlwrap=False,
              fileobj=None, flags=FLAGS_ALL, datadef='EBAS_1.1',
              metadata_options=0, suppress=0):
        """
        Writes the I/O object to a dap file (or stdout).
        Parameters:
            createfiles   write to file, else write to stdout
                          (special case for fileobj)
            destdir       destination directory path for files
            fileobj       write to filehandle
            flags         flag column options: FLAGS_ONE_OR_ALL (only allowed
                          value for OPeNDAP)
            datadef       ebas data definition (EBAS_1 or EBAS_1.1)
            metadata_options
                          options for output, bitfield:
                          currently only EBAS_IOMETADATA_OPTION_SETKEY
            suppress      suppress selected consolidations (bitfield):
                              SUPPRESS_SORT_VARIABLES
                              SUPPRESS_METADATA_OCCURRENCE
        Returns:
            None
        """
        self.check_requirements()
        fil = self.prepare_write(
            True, createfiles=createfiles, destdir=destdir, xmlwrap=xmlwrap,
            fileobj=fileobj, datadef=datadef, metadata_options=metadata_options,
            suppress=suppress)
        self.make_dataset(EBAS_OPENDAP_REQUESTTYPE_DATA, datadef,
                          metadata_options=metadata_options)

        resp = DODSResponse(self.dataset)
        for data in resp:
            fil.write(data)
        self.finish_write(createfiles, xmlwrap)
        self.write_indexdb()

    def make_dataset(self, requesttype, projection=None, datadef='EBAS_1.1',
                     metadata_options=None):
        """
        Build the pydap dataset object according to the (ebas domain) content of
        the obect. Sets the dataset attributes.
        Entry point for the pydap webservice.
        Parameters:
            requesttype   type of request for which the dataset should be built
                          EBAS_OPENDAP_REQUESTTYPE_DDS,
                          EBAS_OPENDAP_REQUESTTYPE_DAS
                          EBAS_OPENDAP_REQUESTTYPE_DATA
            datadef       EBAS metadata standard (to be used in the metadata
                          variables (json encoded))
            projection    pydap projection object (in order to constrain the
                          result dataset)
            metadata_obtions
                          options for output, bitfield:
                          currently only EBAS_IOMETADATA_OPTION_SETKEY
        Returns:
            None
        """
        self.check_requirements()
        self.prepare_write(False, datadef=datadef,
                           metadata_options=metadata_options)
        self._make_dataset(requesttype, projection, metadata_options)
        
    def _make_dataset(self, requesttype, projection, metadata_options):
        """
        Build the pydap dataset object according to the (ebas domain) content of
        the obect. Sets the dataset attributes.
        Entry point for the pydap webservice.
        Parameters:
            requesttype   type of request for which the dataset should be built
                          EBAS_OPENDAP_REQUESTTYPE_DDS,
                          EBAS_OPENDAP_REQUESTTYPE_DAS
                          EBAS_OPENDAP_REQUESTTYPE_DATA
            projection    pydap projection object (in order to constrain the
                          result dataset)
        Returns:
            None
        """
        set_data = True if requesttype == EBAS_OPENDAP_REQUESTTYPE_DATA \
                        else False
        set_attributes = True \
                         if requesttype in (EBAS_OPENDAP_REQUESTTYPE_DAS, \
                                            EBAS_OPENDAP_REQUESTTYPE_DATA) \
                         else False

        # set up the dataset
        self.dataset = DatasetType(name='Dataset')
        if set_attributes:
            # das or data: global attributes are needed
            self.add_global_attributes(metadata_options)
        # set up the time variables
        self._setup_dataset_time(set_data=set_data,
                                 set_attributes=set_attributes)
        self._setup_dataset_variables(set_attributes=set_attributes)
        # project:
        if projection:
            self.dataset = self._apply_projection(projection)
        if set_data:
            self._fill_data()

    def check_requirements(self):
        """
        Check requirements for opendap output.
        pydap and numpy are NOT dependencies for ebas-io generally.
        Thus, ebas-io can  be used w/o this modules.
        However the functionality is limited. An error message is thrown here
        and no output produced.
        # Info: make dataset is also a direct entry point (from the webservice)
        """
        try:
            import pydap  # @UnusedImport pylint: disable=W0612
            # W0612: Unused variable 'pydap'
            # Unused import: pydap
            # --> this line is just used to get a nice error message instead
            # of an exception in case of requirements not been installed
        except ImportError:
            self.error("The python pydap module is not installed. OPeNDAP "
                       "output is not available.")
            return
        try:
            import numpy  # @UnusedImport pylint: disable=W0612
            # W0612: Unused variable 'numpy'
            # Unused import: numpy
            # --> this line is just used to get a nice error message instead
            # of an exception in case of requirements not been installed
        except ImportError:
            self.error("The python numpy module is not installed. OPeNDAP "
                       "output is not available.")
            return

    def add_global_attributes(self, metadata_options):
        """
        Add global netCFD, CF and ACDD attributes.
        See generate_global_acdd_attributes for details.
        """
        self.dataset.attributes['NC_GLOBAL'] = {}
        # ACDD attributes
        for att in self.generate_global_acdd_attributes(metadata_options):
            self.dataset.attributes['NC_GLOBAL'][att[0]] = att[1]
        # EBAS attributes
        for att in self.generate_global_ebas_attributes():
            self.dataset.attributes['NC_GLOBAL'][att[0]] = att[1]
        # some DODS specific GAs:
        self.dataset.attributes['DODS_EXTRA'] = {}
        self.dataset.attributes['DODS_EXTRA']['unlimited_dimension'] = \
            "time"

    def _apply_projection(self, projection):
        """
        Applies the projection to the pydap dataset.
        Parameters:
            projection
        Return:
            new (projected) dataset
        (Copy/Paste from pydap DefaultHandler (v.3.2))
        """
        res = DatasetType(name=self.dataset.name,
                          attributes=self.dataset.attributes)

        # first collect all the variables
        for p in projection:
            target, template = res, self.dataset
            for i, (name, slice_) in enumerate(p):
                candidate = template[name]

                # add variable to target
                if isinstance(candidate, StructureType):
                    if name not in target.keys():
                        if i < len(p) - 1:
                            # if there are more children to add we need to clear
                            # the candidate so it has only explicitly added
                            # children; also, Grids are degenerated into Structures
                            if isinstance(candidate, GridType):
                                candidate = StructureType(
                                    candidate.name, candidate.attributes)
                            candidate._keys = []
                        target[name] = candidate
                    target, template = target[name], template[name]
                else:
                    target[name] = candidate

        # fix sequence data to include only variables that are in the sequence
        for seq in walk(res, SequenceType):
            seq.data = get_var(self.dataset, seq.id)[tuple(seq.keys())].data

        # apply slices
        for p in projection:
            target = res
            for name, slice_ in p:
                name = urllib.parse.unquote(name).decode('utf8')
                target, parent = target[name], target
                if slice_:
                    if name in self.cdm_variables:
                        self.cdm_variables[name]['slice'] = slice_
                    if isinstance(target, BaseType):
                        target.data = target[slice_]
                    elif isinstance(target, SequenceType):
                        parent[name] = target[slice_[0]]
                    elif isinstance(target, GridType):
                        parent[name] = target[slice_]
                    else:
                        raise ConstraintExpressionError("Invalid projection!")
        return res

    def _fill_data(self):
        """
        Fill the data after projection.
        """
        for var in walk(self.dataset, BaseType):
            if var.name in ['time', 'time_bounds', 'metadata_time',
                            'metadata_time_bounds']:
                # time variables are always filled, and have been correctly
                # sliced, nothing to do
                continue

            name = urllib.parse.unquote(var.name).decode('utf8')
            if name not in self.cdm_variables:
                # must be a dimension... those are filled with data and
                # sliced already
                continue
            # prepare variable flags according to dimensions
            odv = self.cdm_variables[name]
            if 'slice' in odv:
                dims = []
                indxs = []
                if (name.endswith('_qc') and \
                    len(odv['dimensions']) != len(odv['slice'])-2) or \
                   (not name.endswith('_qc') and \
                    len(odv['dimensions']) != len(odv['slice'])-1):
                    raise ValueError('wrong number of dimensions in projection')
                for i in range(len(odv['dimensions'])):
                    # iterate over n-1 dimensions (exclude time dim for now)
                    # and for _qc variables: exclude the flag dimension for now 
                    dims.append([(odv['dimensions'][i], k) for k in odv['dimextents'][i][odv['slice'][i]]])
                    indxs.append([(slice(j, j+1),) for j in range(len(odv['dimextents'][i][odv['slice'][i]]))])
            else:
                dims = [[tuple([odv['dimensions'][i], k]) for k in odv['dimextents'][i]] for i in range(len(odv['dimensions']))]
                indxs = [[slice(j, j+1) for j in range(len(odv['dimextents'][i]))] for i in range(len(odv['dimensions']))]

            # ebasmetadata: calculate max stringlen first:
            maxlen_ebasmeta = 1
            grid_ebasmeta = []
            if var.name.endswith('_ebasmetadata'):
                # slice the metadata_time?
                if 'slice' in odv:
                    t_slc = odv['slice'][-1]
                else:
                    t_slc = slice(0, None)
                for elem in itertools.product(*dims):
                    idx = odv['variable_dimensions'].index(elem)
                    var_index = odv['ebas_variables'][idx]
                    # generate all metadta in json encoding here, reuse
                    # when filling the data below.
                    # quoting:
                    # ebas_metadata_json returns unicode or str (if only 7bit)
                    dims_ebasmeta = [
                        mdi[2].ebas_metadata_json(var_index)
                        for mdi in self.metadata_intervals[t_slc]]
                    grid_ebasmeta.append(dims_ebasmeta)
                    maxlen_ebasmeta = max(maxlen_ebasmeta,
                                          max([len(x) for x in dims_ebasmeta]))
                shape = var.data.shape
                #shape = tuple([len(odv['dimextents'][i])
                #               for i in range(len(odv['dimensions']))] + \
                #               [len(self.metadata_intervals)])
                dtype = 'U{}'.format(maxlen_ebasmeta)
                var.data = np.empty(shape, dtype=dtype)

            # now fill the data according to the dims list
            index_perm = itertools.product(*indxs) # index permutations
            iter_grid_ebasmeta = iter(grid_ebasmeta)
            for elem in itertools.product(*dims):
                data_ind = next(index_perm)
                idx = odv['variable_dimensions'].index(elem)
                var_index = odv['ebas_variables'][idx]
                # slice the time?
                if 'slice' in odv:
                    t_slc = odv['slice'][-1]
                else:
                    t_slc = slice(0, None)
                if var.name.endswith('_qc'):
                    # prepare variable flags according to dimensions
                    flagdim = 3
                    # slice the flag dimension?
                    if 'slice' in odv:
                        f_slc = odv['slice'][-2]
                    else:
                        f_slc = slice(0, None)
                    fdim = len(([0] * flagdim)[f_slc])
                    tdim = len(self.sample_times[t_slc])
                    data = np.empty(shape=(fdim, tdim), dtype=np.int32)
                    for i in range(fdim):
                        lst = [flag[f_slc][i] if len(flag[f_slc]) >= i+1 else 0  for flag in self.variables[var_index].flags[t_slc]]
                        data[i] = np.array(lst, dtype=float)
                elif var.name.endswith('_ebasmetadata'):
                    # prepare variable metadata according to metadata_time dimension
                    dtype = 'U{}'.format(maxlen_ebasmeta)
                    dims_ebasmeta = next(iter_grid_ebasmeta)
                    data = np.array(dims_ebasmeta, dtype=dtype)
                else:
                    data = np.array(
                        self.variables[var_index].values_[t_slc],
                        # last dimension is slice is time
                        dtype=float)
                    if self.access_log:
                        # TODO: call siblings to log the access, 2 reasons:
                        # - right now, a joined file does not even know whether it should log accesss (access_log is not inherited when the join method creates a new parent object
                        # - single intervals need to be logged, not the overall interval
                        self.access_log.access_dataset(
                            self.get_meta_for_var(var_index, 'setkey'),
                            #self.variables[var_index].values_.lazies[0].hdi_obj.ds.DS_SETKEY,
                            # does not work for non compound lazy read objects!
                            DatetimeInterval(self.sample_times[t_slc][0][0],
                                             self.sample_times[t_slc][-1][-1]))

                target = var.data 
                for slc in data_ind:
                    target = target[slc][0]
                target[:] = data
                        
                    

        # self.cdm_variables =
        # 'grid_name' : {
        #         'ebas_variables' = [index, index, ...]
        #         'dimensions' = (name, name, ....)
        #         'dimextents' = ([value, value, ...], ...)
        #                          ... for each dimension
        #         'variable_dimensions': (((dimension, value), ...), ...)
        #                          ... for each variable (for each dimension)
        #         'slice': None,
        # }
#                 var_index = self.varnames.index(basename)
#                 flags = self.variables[var_index].flags[self.slices[var_index][0]]
#                 flags = [y + [0] * (flagdim-len(y)) for y in flags]
#                 var.data = np.array(flags, dtype=np.int32)
#             else:
#                 # prepare variable data according to time dimension
#                 var_index = self.varnames.index(urllib.unquote(var.name).decode('utf8'))
#                 # slice lazy read objects!!!
#                 ### this worked already...:
#                 ### data = np.array(self.variables[var_index].values_,
#                 ###                 dtype=float)
#                 ### var.data = data[self.slices[var_index]]
#                 var.data = np.array(
#                     self.variables[var_index].values_[self.slices[var_index][0]],
#                     # for now (1d): take the first dimension slice ...[0]
#                     dtype=float)

    def _setup_dataset_time(self, set_data=False, set_attributes=False):
        """
        Parameters:
            set_data          bool indicator if data should be included
            set_attributes    bool indicator if attributes should be included
        Returns:
            None
        """
        # create the time variable:
        zero = datetime.datetime(1900, 1, 1)
        if set_data:
            seq = (((intv[0]+(intv[1]-intv[0])/2)-zero).total_seconds()/86400.0
                   for intv in self.sample_times)
            data = np.fromiter(seq, dtype=float)
        else:
            data = np.empty((len(self.sample_times),), dtype=float)
        self.dataset['time'] = BaseType(
            name='time', data=data,
            shape=(len(self.sample_times),), type=float)
        if set_attributes:
            # das or data: time attributes are needed
            self.dataset['time'].attributes['standard_name'] = "time"
            self.dataset['time'].attributes['long_name'] = "time of measurement"
            self.dataset['time'].attributes['units'] = \
                "days since 1900-01-01 00:00:00"
            self.dataset['time'].attributes['axis'] = "T"
            self.dataset['time'].attributes['calendar'] = "gregorian"
            self.dataset['time'].attributes['bounds'] = "time_bnds"
            self.dataset['time'].attributes['cell_methods'] = "mean"

        # create time_bounds
        if set_data:
            seq = (((intv[0]-zero).total_seconds()/86400.0,
                    (intv[1]-zero).total_seconds()/86400.0)
                   for intv in self.sample_times)
            data = np.array(list(seq), dtype=float)
        else:
            data = np.empty((len(self.sample_times), 2), dtype=float)
        self.dataset['time_bounds'] = BaseType(
            name='time_bounds', data=data, shape=(len(self.sample_times), 2),
            type=float, dimensions=('time', 'bnds'))
        if set_attributes:
            # das or data: time_bounds attributes are needed
            self.dataset['time_bounds'].attributes['standard_name'] = "time"
            self.dataset['time_bounds'].attributes['long_name'] = "time bounds for measurement"
            self.dataset['time_bounds'].attributes['units'] = "days since 1900-01-01 00:00:00"
            self.dataset['time_bounds'].attributes['calendar'] = "gregorian"

        # Setup metadata_time
        if set_data:
            seq = (((intv[0]+(intv[1]-intv[0])/2)-zero).total_seconds()/86400.0
                   for intv in self.metadata_intervals)
            data = np.fromiter(seq, dtype=float)
        else:
            data = np.empty((len(self.metadata_intervals),), dtype=float)
        self.dataset['metadata_time'] = BaseType(
            name='metadata_time', data=data,
            shape=(len(self.metadata_intervals), ), type=float)
        self.dataset['metadata_time'].attributes['standard_name'] = "time"
        self.dataset['metadata_time'].attributes['long_name'] = \
            "time of ebas metadata intervals"
        self.dataset['metadata_time'].attributes['units'] = \
            "days since 1900-01-01 00:00:00"
        self.dataset['metadata_time'].attributes['axis'] = "T"
        self.dataset['metadata_time'].attributes['calendar'] = "gregorian"
        self.dataset['metadata_time'].attributes['bounds'] = \
            "metadata_time_bnds"
        self.dataset['metadata_time'].attributes['cell_methods'] = "mean"

        # Setup metadata_time_bounds
        if set_data:
            seq = (((intv[0]-zero).total_seconds()/86400.0,
                    (intv[1]-zero).total_seconds()/86400.0)
                   for intv in self.metadata_intervals)
            data = np.array(list(seq), dtype=float)
        else:
            data = np.empty((len(self.metadata_intervals), 2), dtype=float)
        data.shape = (len(self.metadata_intervals), 2)
        self.dataset['metadata_time_bounds'] = BaseType(
            name='metadata_time_bounds', data=data, shape=data.shape,
            type=float, dimensions=('metadata_time', 'bnds'))
        self.dataset['metadata_time_bounds'].attributes['standard_name'] = \
            "time"
        self.dataset['metadata_time_bounds'].attributes['long_name'] = \
            "time bounds for ebas metadata intervals"
        self.dataset['metadata_time_bounds'].attributes['units'] = \
            "days since 1900-01-01 00:00:00"
        self.dataset['metadata_time_bounds'].attributes['calendar'] = \
            "gregorian"

    def _setup_grid(self, gridname, set_attributes=False):
        """
        Setup a grid variable within the result dataset.
        No data should be added yet (just create the dataset frame).
        """
        if gridname.endswith('_ebasmetadata'):
            self._setup_grid_ebasmetadata(gridname, set_attributes=set_attributes)
            return
        odv = self.cdm_variables[gridname]
        flagdim = 3
        # TODO: select the right flag dim for the datatset
        # this was veeery inefficient: 
        # flagdim = max([len(y) for x in self.metadata_intervals
        #               for y in x[2].variables[i].flags])
        if gridname.endswith('qc'):
            shape = tuple([len(odv['dimextents'][i])
                           for i in range(len(odv['dimensions']))] + \
                          [flagdim] + [len(self.sample_times)])
            dim = odv['dimensions'] + ('flags',) + ('time', )
            data = np.empty(shape, dtype=np.int32)
            type = np.int32
        else:
            shape = tuple([len(odv['dimextents'][i])
                           for i in range(len(odv['dimensions']))] + \
                          [len(self.sample_times)])
            dim = odv['dimensions'] + ('time', )
            data = np.empty(shape, dtype=float)
            type = float
        grid = GridType(name=gridname)
        grid[gridname] = BaseType(name=gridname, data=data, shape=shape,
                                  type=float, dimensions=dim)

        for i in range(len(odv['dimensions'])):
            if isinstance(list(odv['dimextents'][i])[0], string_types):
                data = [x for x in odv['dimextents'][i]]
                maxlen = max([len(x) for x in data])
                dtype = 'U{}'.format(maxlen)
                shape = (len(data), )
                data = np.array(data, dtype=dtype)
                grid[dim[i]] = BaseType(name=dim[i], data=data, shape=shape,
                                        type=str, dimensions=(dim[i],))
            else:
                # int or float:
                data = [float(x) for x in odv['dimextents'][i]]
                shape = (len(data), )
                data = np.array(data, dtype=float)
                grid[dim[i]] = BaseType(name=dim[i], data=data, shape=shape,
                                        type=float, dimensions=(dim[i],))
        # DO NOT create a mapping - not 100% sure yet whether this is correct. 
        #if gridname.endswith('qc'):
        #    grid['flags'] = BaseType(name='flags',
        #                             data=np.array([i+1 for i in range(flagdim)]),
        #                             shape=(flagdim,),
        #                             type=float)
        
        grid['time'] = self.dataset['time'].__copy__()
        # make a shallow copy of the time variable. data is not copied
        # per se, but when one of the copies is projected, two different
        # data copies will exist. Thus all copies of time can be projected
        # independently: This did not work:
        # grid['time'] = self.dataset['time'] (if one grid or the base
        # variable was subsetted, the "copies" were affected too)
        
        # use the first variable (of all dimensions) for the attributes
        var_ind = odv['ebas_variables'][0] 
        cfname, cfunit = self.cfparams(
            self.get_meta_for_var(var_ind, 'regime'),
            self.get_meta_for_var(var_ind, 'matrix'),
            self.variables[var_ind].metadata.comp_name,
            self.get_meta_for_var(var_ind, 'statistics'),
            self.variables[var_ind].metadata.unit,
            self.get_meta_for_var(var_ind, 'datalevel'))
        if set_attributes and gridname.endswith('qc'):
            # das or data: variable attributes are needed
            if cfname:
                grid.attributes['standard_name'] = cfname + " status_flag"
            grid.attributes['missing_value'] = np.int32(0)
            grid.attributes['_FillValue'] = np.int32(0)
            grid.attributes['units'] = "1"
        elif set_attributes:
            if cfname:
                grid.attributes['standard_name'] = cfname
            grid.attributes['missing_value'] = np.float64(np.nan)
            grid.attributes['_FillValue'] = np.float64(np.nan)
            if cfunit:
                grid.attributes['units'] = cfunit
            else:
                grid.attributes['units'] = self.variables[var_ind].metadata.unit
            grid.attributes['ancillary_variables'] = \
                "{0}_qc {0}_ebasmetadata".format(gridname)
            cell_methods = {
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
            }
            stat = self.get_meta_for_var(var_ind, 'statistics')
            if self.variables[var_ind].metadata.comp_name.startswith(
                    'precipitation_amount') and stat == 'arithmetic mean':
                # special case: precipitation amount is a sum 
                grid.attributes['cell_methods'] = "time: sum"
            elif stat in cell_methods:
                grid.attributes['cell_methods'] = "time: {}".format(
                    cell_methods[stat])
            else:
                grid.attributes['cell_methods'] = "time: {}".format(stat)
            grid.attributes['ebas_metadata'] = self.ebas_metadata_json(var_ind)

        self.dataset[gridname] = grid

    def _setup_grid_ebasmetadata(self, gridname, set_attributes=False):
        """
        Setup a grid variable within the result dataset.
        No data should be added yet (just create the dataset frame).
        """
        odv = self.cdm_variables[gridname]
        shape = tuple([len(odv['dimextents'][i])
                       for i in range(len(odv['dimensions']))] + \
                       [len(self.metadata_intervals)])
        dim = odv['dimensions'] + ('metadata_time', )
        dtype = 'U1'
        data = np.empty(shape, dtype=dtype)            
        grid = GridType(name=gridname)
        grid[gridname] = BaseType(name=gridname, data=data, shape=shape,
                                  type=str, dimensions=dim)

        for i in range(len(odv['dimensions'])):
            if isinstance(list(odv['dimextents'][i])[0], string_types):
                data = [x for x in odv['dimextents'][i]]
                maxlen = max([len(x) for x in data])
                dtype = 'U{}'.format(maxlen)
                shape = (len(data), )
                data = np.array(data, dtype=dtype)
                grid[dim[i]] = BaseType(name=dim[i], data=data, shape=shape,
                                        type=str, dimensions=(dim[i],))
            else:
                # int or float:
                data = [float(x) for x in odv['dimextents'][i]]
                shape = (len(data), )
                data = np.array(data, dtype=float)
                grid[dim[i]] = BaseType(name=dim[i], data=data, shape=shape,
                                        type=float, dimensions=(dim[i],))

        grid['metadata_time'] = self.dataset['metadata_time'].__copy__()
        # make a shallow copy of the time variable. data is not copied
        # per se, but when one of the copies is projected, two different
        # data copies will exist. Thus all copies of time can be projected
        # independently: This did not work:
        # grid['time'] = self.dataset['time'] (if one grid or the base
        # variable was subsetted, the "copies" were affected too)

        if set_attributes:
            grid.attributes['long_name'] = \
                "ebas metadata for different time intervals; json encoded"
        self.dataset[gridname] = grid

    def _setup_dataset_variables(self, set_attributes=False):
        """
        Parameters:
            requesttype   type of request for which the dataset should be built
                          EBAS_OPENDAP_REQUESTTYPE_DDS,
                          EBAS_OPENDAP_REQUESTTYPE_DAS
                          EBAS_OPENDAP_REQUESTTYPE_DATA
            projection    pydap projection object (in order to constrain the
                          result dataset)
        Returns:
            None
        """
        self.gen_cdm_variables()

        for gridname in self.cdm_variables.keys():
            self._setup_grid(gridname, set_attributes=set_attributes)
