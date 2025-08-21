# coding: utf-8
"""
$Id$

output functionality for EBAS NetCDF
"""

import os.path
import sys
import itertools
from collections import defaultdict
from six import string_types
from .base import EbasNetcdfBase
from ..base import FLAGS_ALL, EBAS_IOFORMAT_NETCDF1, \
    SUPPRESS_SORT_VARIABLES, SUPPRESS_METADATA_OCCURRENCE

try:
    import netCDF4
    import numpy
    NETCDFSTRING = numpy.unicode_ if numpy.__version__ < '2.0' else numpy.str_
except ImportError:
    # pydap and numpy are NOT dependencies for ebas-io. Thus, ebas-io can
    # be used w/o this modules.
    # However the functionality is limited. An error message will be thrown
    # in the entry points of ebas opendap writer (methods write, make_dataset)
    pass


from ..basefile.write import VAL, FLG, MTA

class EbasNetCDFPartialWrite(EbasNetcdfBase):  # pylint: disable=R0901, W0223,
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Output of I/O object to NetCDF
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the object.
        """
        super(EbasNetCDFPartialWrite, self).__init__(*args, **kwargs)
        # dimensions added to the netCFD file only used during write():
        self.dims = None

    def write(self, createfiles=False, destdir=None, xmlwrap=False,
              fileobj=None, flags=FLAGS_ALL,  # @UnusedVariable
              datadef='EBAS_1.1', metadata_options=0, suppress=0):
        # pylint: disable=R0913,W0613
        # R0913: Too many arguments
        # W0613: Unused argument flags (not used for NetCDF)
        """
        Writes the I/O object to a NetCDF file (or stdout)
        Parameters:
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
        Returns:
            None
        """
        self.check_requirements()

        # prepare write used without opening the output file because the netCDF4
        # module cannot handle output to open files. This is somewhere deep in
        # the NetCDF C library and cannot be changed easily. Instead we will
        # pass the file name to netCDF4.
        # Instead, the file logic needs to be handled here, includeing some
        # workaround for stdout/stream outpot (diskleess object, seralized in
        # the end)
        self.prepare_write(
            False, createfiles=createfiles, destdir=destdir, xmlwrap=xmlwrap,
            fileobj=fileobj, datadef=datadef, metadata_options=metadata_options,
            suppress=suppress)

        if createfiles:
            if destdir:
                fnam = os.path.join(destdir, self.metadata.filename)
            else:
                fnam = self.metadata.filename
            # NETCDF3_64BIT_OFFSET ???
            ncfile = netCDF4.Dataset(fnam, mode='w',
                                     format='NETCDF4')
            self.logger.info("writing to file " + fnam)

        else:
            ncfile = netCDF4.Dataset(self.metadata.filename, diskless=True,
                                     mode='w', format='NETCDF4')
        self.ncfile = ncfile

        self.add_global_attributes(metadata_options)
        self.add_time_variables()
        self.add_variables()
        #self.parse_characteristics(ncfile)
        #self.create_variables(ncfile, var_time)
        if not createfiles:
            sys.stdout.write(str(ncfile))
        self.finish_write(createfiles, xmlwrap)
        ncfile.close()
        #if xmlwrap:
        #    xmlwrap_filetrailer()
        #self.set_data(flags=flags)
        self.write_indexdb()

    def check_requirements(self):
        """
        Check requirements for opendap output.
        pydap and numpy are NOT dependencies for ebas-io generally.
        Thus, ebas-io can  be used w/o this modules.
        However the functionality is limited. An error message is thrown here
        and no output produced.
        # Info: make dataset is also a direct entry point (from the webservice)
        """
        # netCDF4 and numpy are NOT dependencies for ebas-io. Thus, ebas-io can
        # be used w/o this modules.
        # However the functionality is limited. An error message is thrown
        # here and no output produced.
        try:
            import netCDF4  # @UnusedImport pylint: disable=W0612, W0621
            # W0612: Unused variable 'netCDF4'
            # W0621: Redefining name 'netCDF4' from outer scope
            # Unused import: netCDF4
            # --> this line is just used to get a nice error message instead
            # of an exception in case of requirements not been installed
        except ImportError:
            self.error("The python netCDF4 module is not installed. NetCDF "
                       "output is not available.")
            return
        try:
            import numpy  # @UnusedImport pylint: disable=W0612, W0621
            # W0612: Unused variable 'netCDF4'
            # W0621: Redefining name 'netCDF4' from outer scope
            # Unused import: netCDF4
            # --> this line is just used to get a nice error message instead
            # of an exception in case of requirements not been installed
        except ImportError:
            self.error("The python numpy module is not installed. NetCDF "
                       "output is not available.")
            return

    def add_global_attributes(self, metadata_options):
        """
        Add global attributes.
        See generate_global_acdd_attributes and generate_global_ebas_attributes
        for details.
        """
        # ACDD atttributes
        for att in self.generate_global_acdd_attributes(metadata_options):
            self.ncfile.setncattr(att[0], att[1])
        for att in self.generate_global_ebas_attributes(
                version=1 if self.__class__.IOFORMAT == EBAS_IOFORMAT_NETCDF1
                else 2):
            self.ncfile.setncattr(att[0], att[1])

    def add_time_variables(self):
        """
        Add the time variables and the time dimenstion.
        """
        self.ncfile.createDimension('time', len(self.sample_times))
        self.ncfile.createDimension('metadata_time',
                                    len(self.metadata_intervals))
        self.ncfile.createDimension('tbnds', 2)

        # Create time variable
        var_time = self.ncfile.createVariable('time', numpy.float64, ('time', ))
        # Add varaible attributes
        var_time.standard_name = 'time'
        var_time.long_name = 'time of measurement'
        var_time.units = 'days since 1900-01-01 00:00:00 UTC'
        var_time.axis = 'T'
        var_time.calendar = 'gregorian'
        var_time.bounds = "time_bnds"
        # values for the time variable:
        var_time[:] = netCDF4.date2num(
            [intv[0]+(intv[1]-intv[0])/2 for intv in self.sample_times],
            var_time.units, calendar=var_time.calendar)

        # Create time_bounds variable
        var_time_bounds = self.ncfile.createVariable(
            'time_bnds', numpy.float64, ('time', 'tbnds',))
        
        # Add variable attributes
        var_time_bounds.long_name = 'time bounds for measurement'
        # CF-1.8 (Chapter 7.1): for cell boundaries those attributes are NOT
        # reccommended: units, standard_name, axis, positive, calendar,
        #   leap_month, leap_year
        # var_time_bounds.standard_name = 'time'
        # var_time_bounds.units = 'days since 1900-01-01 00:00:00 UTC'

        # values for the var_time_bounds variable:
        var_time_bounds[:] = numpy.column_stack((
            netCDF4.date2num([intv[0] for intv in self.sample_times],
                             var_time.units, calendar=var_time.calendar),
            netCDF4.date2num([intv[1] for intv in self.sample_times],
                             var_time.units, calendar=var_time.calendar)))

        # Create metadata_time variable
        var_metadata_time = self.ncfile.createVariable(
            'metadata_time', numpy.float64, ('metadata_time', ))
        # Add varaible attributes
        var_metadata_time.standard_name = 'time'
        var_metadata_time.long_name = 'time of ebas metadata intervals'
        var_metadata_time.units = 'days since 1900-01-01 00:00:00 UTC'
        var_metadata_time.axis = 'T'
        var_metadata_time.calendar = 'gregorian'
        var_metadata_time.bounds = "metadata_time_bnds"
        # values for the metadata_time variable:
        var_metadata_time[:] = netCDF4.date2num(
            [intv[0]+(intv[1]-intv[0])/2 for intv in self.metadata_intervals],
            var_metadata_time.units, calendar=var_metadata_time.calendar)

        # Create time_bounds variable
        var_metadata_time_bounds = self.ncfile.createVariable(
            'metadata_time_bnds', numpy.float64, ('metadata_time', 'tbnds',))
        # Add variable attributes
        var_metadata_time_bounds.long_name = \
            'time bounds for ebas metadata intervals'
        # CF-1.8 (Chapter 7.1): for cell boundaries those attributes are NOT
        # reccommended: units, standard_name, axis, positive, calendar,
        #   leap_month, leap_year
        # var_metadata_time_bounds.standard_name = 'time'
        # var_metadata_time_bounds.units = 'days since 1900-01-01 00:00:00 UTC'
        # var_metadata_time_bounds.calendar = 'gregorian'

        # values for the metadata_time_bounds variable:
        var_metadata_time_bounds[:] = numpy.column_stack((
            netCDF4.date2num([intv[0] for intv in self.metadata_intervals],
                             var_metadata_time.units,
                             calendar=var_metadata_time.calendar),
            netCDF4.date2num([intv[1] for intv in self.metadata_intervals],
                             var_metadata_time.units,
                             calendar=var_metadata_time.calendar)))

    def add_var_dimensions(self, cdm_var):
        """
        Add additional dimensions needed by the cdm variable.
        Parameters:
            cdm_var    the cdm variable description (dict)
        Returns:
            None
        """
        for i in range(len(cdm_var['dimensions'])):
            dim = cdm_var['dimensions'][i]
            if dim not in self.dims:
                self.dims.add(dim)
                self.ncfile.createDimension(
                    dim, len(cdm_var['dimextents'][i]))
                if isinstance(cdm_var['dimextents'][i][0], string_types):
                    var = self.ncfile.createVariable(dim, NETCDFSTRING,
                                                     (dim, ))
                    var[:] = numpy.array([ext
                                          for ext in cdm_var['dimextents'][i]],
                                         NETCDFSTRING)
                elif isinstance(cdm_var['dimextents'][i][0], int):
                    var = self.ncfile.createVariable(dim, numpy.int32, (dim, ))
                    var[:] = numpy.array([ext
                                          for ext in cdm_var['dimextents'][i]],
                                         numpy.int32)
                else:
                    var = self.ncfile.createVariable(dim, numpy.float64,
                                                     (dim, ))
                    var[:] = numpy.array([ext
                                          for ext in cdm_var['dimextents'][i]],
                                         numpy.float64)

    def add_var_attributes(self, var, cdm_var):
        """
        Set the variable attributes for a cdm variable.
        Parameters:
            var        the netCDF variable
            cdm_var    the cdm variable description (dict)
        Returns:
            None
        """
        # use the first variable (of all dimensions) for the attributes
        ebas_var_ind = cdm_var['ebas_variables'][0]
        cfname, cfunit = self.cfparams(
            self.get_meta_for_var(ebas_var_ind, 'regime'),
            self.get_meta_for_var(ebas_var_ind, 'matrix'),
            self.get_meta_for_var(ebas_var_ind, 'comp_name'),
            self.get_meta_for_var(ebas_var_ind, 'statistics'),
            self.get_meta_for_var(ebas_var_ind, 'unit'),
            self.get_meta_for_var(ebas_var_ind, 'datalevel'))
        if cdm_var['var_type'] == FLG:
            var.setncatts({'standard_name': "status_flag"})
            var.setncatts({'missing_value': numpy.int32(0)})
            var.setncatts({'_FillValue': numpy.int32(0)})
            var.setncatts({'units': '1'})
        elif cdm_var['var_type'] == MTA:
            var.setncatts({
                'long_name':
                    "ebas metadata for different time intervals; json encoded"})
        else:
            if cfname:
                var.setncatts({'standard_name': cfname})
            var.setncatts({'missing_value': numpy.float64(numpy.nan)})
            var.setncatts({'_FillValue': numpy.float64(numpy.nan)})
            if cfunit:
                var.setncatts({'units': cfunit})
            else:
                var.setncatts({'units':
                               self.get_meta_for_var(ebas_var_ind, 'unit')})
            var.setncatts({
                'ancillary_variables':
                    "{0}_qc {0}_ebasmetadata".format(cdm_var['cdm_varname'])})
            var.setncatts({'cell_methods': self.cell_methods(ebas_var_ind)})
            if self.__class__.IOFORMAT != EBAS_IOFORMAT_NETCDF1:
                # In version 2 we use all the ebas_XXX attributes:
                atts = defaultdict(int)
                for var_index in cdm_var['ebas_variables']:
                    # In case of addtitional dimensions (characteristics), we
                    # need to make sure, only attributes which are the same for
                    # all variables are used.
                    for att in self.generate_variable_ebas_attributes(
                            var_index=var_index):
                        atts[(att[0], att[1])] += 1
                for tag_val in atts:
                    if atts[tag_val] == len(cdm_var['ebas_variables']):
                        var.setncatts({tag_val[0]: tag_val[1]})

    def add_var_data(self, var, cdm_var):
        """
        Set the variable data for a cdm variable.
        Parameters:
            var        the netCDF variable
            cdm_var    the cdm variable description (dict)
        Returns:
            None
        """
        maxlen_ebasmeta = 3   # TODO?
        # now fill the data according to the dims list
        dims = [[tuple([cdm_var['dimensions'][i], k]) for k in cdm_var['dimextents'][i]] for i in range(len(cdm_var['dimensions']))]
        indxs = [[slice(j, j+1) for j in range(len(cdm_var['dimextents'][i]))] for i in range(len(cdm_var['dimensions']))]
        index_perm = itertools.product(*indxs) # index permutations
        for elem in itertools.product(*dims):
            data_ind = next(index_perm)
            idx = cdm_var['variable_dimensions'].index(elem)
            var_index = cdm_var['ebas_variables'][idx]
            if cdm_var['var_type'] == VAL:
                data = numpy.array(
                    self.variables[var_index].values_,
                    dtype=float)
            if cdm_var['var_type'] == FLG:
                # prepare variable flags according to dimensions
                fdim = cdm_var['flag_dimsize']
                tdim = len(self.sample_times)
                data = numpy.empty(shape=(fdim, tdim), dtype=numpy.int32)
                for i in range(fdim):
                    lst = [flag[i] if len(flag) >= i+1 else 0 for flag in self.variables[var_index].flags]
                    data[i] = numpy.array(lst, dtype=numpy.int32)
            if cdm_var['var_type'] == MTA:
                # prepare variable metadata according to metadata_time dimension
                #dtype = 'U{}'.format(maxlen_ebasmeta)
                ebasmeta = [
                    mdi[2].ebas_metadata_json(
                        var_index=var_index,
                        version=1 if self.__class__.IOFORMAT == \
                            EBAS_IOFORMAT_NETCDF1 else 2)
                    for mdi in self.metadata_intervals]
                data = numpy.array(ebasmeta, dtype=NETCDFSTRING)
            var[data_ind] = data

    def add_variables(self):
        """
        Add the time variables and the time dimenstion.
        """
        self.gen_cdm_variables()
        self.dims = set()
        for cdm_var in self.cdm_variables.values():
            self.add_var_dimensions(cdm_var)
            if cdm_var['var_type'] == VAL:
                # only for data variable: add additionsl variable dimensions
                # add the variable for holding the measurements
                var = self.ncfile.createVariable(
                    cdm_var['cdm_varname'], numpy.float64,
                    cdm_var['dimensions']+('time', ),
                    fill_value=numpy.float64(numpy.nan))
            if cdm_var['var_type'] == MTA:
                # add the variable for holding the variable metadata
                var = self.ncfile.createVariable(
                    cdm_var['cdm_varname'], NETCDFSTRING,
                    cdm_var['dimensions']+('metadata_time', ))
            if cdm_var['var_type'] == FLG:
                # add the flag dimension for this variable:
                dimname = cdm_var['cdm_varname'] + '_flags'
                self.ncfile.createDimension(dimname, cdm_var['flag_dimsize'])
                #var = self.ncfile.createVariable(dimname, numpy.int32,
                #                                 (dimname, ))
                # add the variable for holding the flags
                var = self.ncfile.createVariable(
                    cdm_var['cdm_varname'], numpy.int32,
                    cdm_var['dimensions']+(dimname, 'time'),
                    fill_value=numpy.int32(0))

            self.add_var_attributes(var, cdm_var)
            self.add_var_data(var, cdm_var)
