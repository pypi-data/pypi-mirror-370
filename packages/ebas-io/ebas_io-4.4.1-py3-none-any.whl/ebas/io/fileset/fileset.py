"""
ebas/nasa_ames/fileset.py
$Id: fileset.py 2721 2021-10-22 23:02:49Z pe $

EBAS NASA Ames module

History:
V.1.0.0  2012-09-20  pe  initial version

"""

import logging
from nilutility.datetime_helper import DatetimeInterval
from ebas.domain.basic_domain_logic.unit_convert import UnitConvert, \
    NoConversion
from .xmlwrap import xmlwrap_header, xmlwrap_trailer
from ..file.base import EBAS_IOFORMAT_NASA_AMES, EBAS_IOFORMAT_CSV, \
    EBAS_IOFORMAT_XML, EBAS_IOFORMAT_NETCDF1, EBAS_IOFORMAT_NETCDF, \
    EBAS_IOFORMAT_OPENDAP, \
    EBAS_IOSTYLE_SINGLECOLUMN, EBAS_IOSTYLE_MULTICOLUMN, \
    EBAS_IOSTYLE_MULTICOLUMN_PRECIP, EBAS_IOSTYLE_KEEP, \
    FLAGS_ONE_OR_ALL


class NoDataDOI(Exception):
    pass


class EbasIOResultSet(object):
    # pylint: disable-msg=R0902
    #  R0902: Too many instance attributes
    """
    Set of results (NASA Ames, CSV, XML, netcdf).
    """
    def __init__(self, outformat=EBAS_IOFORMAT_NASA_AMES,
                 outstyle=EBAS_IOSTYLE_MULTICOLUMN, createfiles=False,
                 destdir=None, xmlwrap=False, precip_amount=False,
                 expand=False, long_timeseries=True, flags=FLAGS_ONE_OR_ALL,
                 metadata_options=0, access_log=None, indexdb=None,
                 diff_xml=None, gen_converted=False, noextract=False,
                 doi=None):
        """
        Set up resultset object.
        Parameters:
            outformat   the (file)format of the results (triggers which type of
                        result object will be generated
            outstyle    EBAS_IOSTYLE_SINGLECOLUMN, EBAS_IOSTYLE_MULTICOLUMN,
                        EBAS_IOSTYLE_MULTICOLUMN_PRECIP, EBAS_IOSTYLE_KEEP
            createfiles bool, whether actual files should be generated or output
                        should go to stdout
            destdir     destination directory for output files
            xmlwrap     bool, result should be wrapped in xml container
                        (for ACTRIS webservice)
            precip_amount
                        bool, add precipitation amout datasets for concentartion
                        measurements automatically
            expand      bool, expand multicolumn output (add all datasets from
                        the same instrument which fit in the file)
            long_timeseries
                        produce long time series, even when metadata change over
                        time. Variable metadata are only supported by some file
                        formats. Those who do not support variable metadata
                        just ignore the argument (join method does nothing).
            flags       flag output behaviour (FLAGS_ONE_OR_ALL, FLAGS_COMPRESS,
                        FLAGS_ALL, FLAGS_NONE
            metadata_options
                        triggers output of optional metadata, currently only
                        EBAS_IOMETADATA_OPTION_SETKEY
            access_log  AccessLog object for logging the data access
            indexdb     IndexDb object for creation of a file index database
            diff_xml    EbasDiffExportXML object for creation of a diffxml
                        document
            gen_converted
                        bool, trigger the unit conversion for selected
                        parameters on output (add a converted variable, e.g.
                        ozone in nmol/mol)
            noextract   bool, trigges the suppression of the actual extraction
                        (needed in a special case for the OPeNDAP server)
            doi         DOI URI; special case: This Object represents a 
                        state DOI. Consequences for filenames and metadata
                        elements doi, doi_list
        """
        # pylint: disable-msg=R0913
        #  R0913: Too many arguments
        
        self.logger = logging.getLogger('EbasIO')
        self.results = []
        self.result_num = 0   # number of results generated in total
        self.outformat = outformat
        # local import to avoid circular import
        if self.outformat == EBAS_IOFORMAT_NASA_AMES:
            from ..file.nasa_ames import EbasNasaAmes
            self.result_class = EbasNasaAmes
        elif self.outformat == EBAS_IOFORMAT_XML:
            from ..file.xml   import EbasXML
            self.result_class = EbasXML
        elif self.outformat == EBAS_IOFORMAT_CSV:
            from ..file.csv   import EbasCSV
            self.result_class = EbasCSV
        elif self.outformat == EBAS_IOFORMAT_NETCDF1:
            from ..file.netcdf import EbasNetcdf1
            self.result_class = EbasNetcdf1
        elif self.outformat == EBAS_IOFORMAT_NETCDF:
            from ..file.netcdf import EbasNetcdf
            self.result_class = EbasNetcdf
        elif self.outformat == EBAS_IOFORMAT_OPENDAP:
            from ..file.opendap import EbasOPeNDAP
            self.result_class = EbasOPeNDAP
        else:
            raise ValueError('Unknown output format')
        self.outstyle = outstyle
        self.createfiles = createfiles
        self.destdir = destdir
        self.xmlwrap = xmlwrap
        self.precip_amount = precip_amount
        self.expand = expand
        self.long_timeseries = long_timeseries
        self.prec_di_export = {}
        self.prec_var_nondomain = {}
        self.flags = flags
        self.metadata_options = metadata_options
        self.clear_caches = None
        self.access_log = access_log
        self.indexdb = indexdb
        self.diff_xml = diff_xml
        self.gen_converted = gen_converted
        self.noextract = noextract
        self.export_state = None
        self.export_filter = None
        self.doi = doi
        self.nodata = True
        self.restricted = False
        if not self.noextract and self.xmlwrap:
            xmlwrap_header()
        if not self.noextract and self.outformat == EBAS_IOFORMAT_XML and \
           not createfiles:
            print('<?xml version="1.0" encoding="utf-8"?>')
            print('<ebas:Result xmlns:ebas="http://ebas.nilu.no/EBAS">')
        self._id = -1

    @property
    def unique_id(self):
        """
        Get a unique identifier.
        """
        self._id += 1
        return self._id

    def add_datasets(self, ds_list, on_the_fly=True, clear_caches=None,
                     crit=None, time=None):
        """
        Adds datasets to the file set.

        Parameters:
            ds_list      iterator of dataset objects
            on_the_fly   export on the fly (creates output as soon as possible)
            clear_caches EbasDomainObjCache to be cleared when output is done
            crit         additional criteria to be checked for each export
                         snipplet (currently only project) (dictionary)
            time         time criteria, only used for extract_doi, else the
                         time criteria are taken from the dbctx
        Returns:
            None
        """
        prev_station = None
        self.clear_caches = clear_caches
        if self.export_state and self.export_state != ds_list.dbctx.state:
            raise RuntimeError(
                "only the same state can be added to a result set")
        self.export_state = ds_list.dbctx.state
        if self.export_filter and \
                self.export_filter != ds_list.dbctx.export_filter:
            raise RuntimeError(
                "only the same export filter can be added to a result set")
        self.export_filter = ds_list.dbctx.export_filter
        for dsobj in ds_list:
            # new station code: finalize previous results
            if on_the_fly:
                if prev_station and prev_station != dsobj.ST_STATION_CODE:
                    self.extract_all()
                prev_station = dsobj.ST_STATION_CODE
            nodata = True
            # loop through data intervals
            for di_ in dsobj.di:
                # find interval sniplets to be exported:
                # (changing projects, variable metadata or instrument metadata)
                intervals = di_.get_export_intervals(crit, time)
                for intv in intervals:
                    nodata = False
                    if intv[1]:
                        self.nodata = False
                        self.add_di(di_, intv[0])
                        if self.access_log and not self.noextract:
                            # suppress access_log when noextract is set
                            # the file object has to care for access_log
                            # if anything is output.
                            self.access_log.access_dataset(
                                di_.ds.DS_SETKEY,
                                DatetimeInterval(intv[0][0],intv[0][1]))
                        if self.diff_xml:
                            self.diff_xml.add_added(di_.ds.DS_SETKEY,
                                                    intv[0][0], intv[0][1])
                    else:
                        self.logger.warning(
                            "no access to setkey %d [%s, %s]",
                            dsobj.DS_SETKEY, intv[0][0], intv[0][1])
                        self.restricted = True
            if nodata:
                self.logger.warning(
                    "no data for setkey %d [%s, %s]",
                    dsobj.DS_SETKEY, dsobj.dbctx.time[0], dsobj.dbctx.time[1])
        # Results are possibly unsorted in the case where files are splited
        # horizontally (see below substituted in add_hdi)
        # We need to sort in order to make e.g. join_years work. 
        self.results = sorted(
            self.results,
            key=lambda x: \
               (x.sample_times[0][0],
                x.internal.fromdomain_tmp.di_obj[0].DS_SETKEY))


    def add_di(self, di_obj, intv):
        """
        Merge a data interval of one dataset into the existing file set.
        Depending on self.outformat it tries to merge the data into existing
        results, merges parts into existing results or adds a new file.
        Will be executed recursively if needed.
        Adds precipitation amount if needed/wanted.

        Parameters:
            di_obj   the di object to be added
            intv     interval to be merged in (start, end) (datetime.datetime)
        Returns:
            None
        """
        if not list(di_obj.su.sa.values(intv)):
            # no samples in interval, do not add data interval
            return
        if not self.result_class.LAZY_READ:
            # If we are not a LAZY_READ object (e.g. OPeNDAP), we prefer to
            # eagerly read here. We need to read the whole DI data anyway, and
            # fragmented output files suffered up to 30% performace decrease
            # due to lazy read.
            _ = list(di_obj.ts.values(intv))
        precip_dis = self._get_precip_dis(di_obj, intv)
        if self.outstyle in (EBAS_IOSTYLE_SINGLECOLUMN,
                             EBAS_IOSTYLE_MULTICOLUMN_PRECIP):
            # singlecolumn: always create a new file
            result = self.new_result()
            result.setup_from_domain(di_obj, intv, 0)
            for pdi in  precip_dis:
                if self.outstyle == EBAS_IOSTYLE_MULTICOLUMN_PRECIP:
                    prec_int = intv.overlap(pdi.VALIDTIME)
                    (success, rem_intv) = result.merge_var_from_domain(
                        pdi, prec_int, False, 2 if self.gen_converted else 0)
                    if success is False:
                        self._add_prec_di(
                            pdi,
                            DatetimeInterval(result.sample_times[0][0],
                                             result.sample_times[-1][1]))
                        if rem_intv:
                            raise RuntimeError(
                                'only expandable variables can force a file '
                                'split')
                else:
                    self._add_prec_di(
                        pdi,
                        DatetimeInterval(result.sample_times[0][0],
                                         result.sample_times[-1][1]))
            if self.gen_converted:
                try:
                    unit_convert = UnitConvert()
                    unit_convert.export_conv_params(
                        di_obj.ds.RE_REGIME_CODE, di_obj.ds.MA_MATRIX_NAME,
                        di_obj.ds.CO_COMP_NAME, di_obj.ds.pm.PM_UNIT,
                        di_obj.ds.DS_VOLUME_STD_PRESS,
                        di_obj.ds.DS_VOLUME_STD_TEMP)
                    # We do not care about the result here. We just know there
                    # is a possible conversion if there is no NoConversion
                    # exception.
                except NoConversion:
                    pass
                else:
                    result = self.new_result()
                    result.setup_from_domain(di_obj, intv, 1)
            return
        if self.outstyle != EBAS_IOSTYLE_MULTICOLUMN:
            raise RuntimeError('Illegal IOSTYLE for add_di')
        # multicolumn: try to merge interval into existing outputfiles
        for resnum, result in enumerate(self.results):
            (success, rem_intv) = result.merge_var_from_domain(
                di_obj, intv, True, 2 if self.gen_converted else 0)
            if success:
                for pdi in  precip_dis:
                    prec_int = intv.overlap(pdi.VALIDTIME)
                    (success, _) = result.merge_var_from_domain(
                        pdi, prec_int, False, 2 if self.gen_converted else 0)
                    if not success:
                        self._add_prec_di(pdi, prec_int)
                for di_, int_ in rem_intv:
                    # recursively add remaining intervals
                    self.add_di(di_, int_)
                return
            elif rem_intv:
                # success is False and rem_intv: we need to substitute this file
                del self.results[resnum]
                for di_, int_ in rem_intv:
                    # recursively add remaining intervals
                    self.add_di(di_, int_)
                return
            # else no merge, keep iterating

        # multicolumn: only if interval could not be merged - create new file:
        result = self.new_result()
        result.setup_from_domain(di_obj, intv, 2 if self.gen_converted else 0)
        for pdi in  precip_dis:
            prec_int = intv.overlap(pdi.VALIDTIME)
            (success, _) = result.merge_var_from_domain(
                pdi, prec_int, False, 2 if self.gen_converted else 0)
            if not success:
                self._add_prec_di(pdi, prec_int)

    def add_ebasfile(self, ebasfile):
        """
        Add an existing ebas file to the fileset.
        According to IOSTYLE, the file ist either added whole, or all variables
        are added to the fileset (in order to support single/mulicolumn etc)
        Parameters:
            ebasfile     an ebas.io file object
        Returns
            None
        """
        if self.outstyle == EBAS_IOSTYLE_KEEP:
            # no changes in single/multicolumn, just copy the file to an export
            # file
            outputfile = self.new_result()
            outputfile.from_ebasfile(ebasfile)
        else:
            precip_vars = []
            for i, _ in enumerate(ebasfile.variables):
                if ebasfile.is_precip_amount(i):
                    metadata = ebasfile.get_all_meta_for_var(i)
                    precip_vars.append({
                        'id': self.unique_id,
                        'metadata': metadata,
                        'sample_times': ebasfile.sample_times,
                        'values': ebasfile.variables[i].values_,
                        'flags': ebasfile.variables[i].flags,
                        })
            precip_vars_used = False
            for i, _ in enumerate(ebasfile.variables):
                if not ebasfile.is_precip_amount(i):
                    metadata = ebasfile.get_all_meta_for_var(i)
                    if ebasfile.is_precip_concentration(i):
                        precip_vars_used = True
                        use_precip = precip_vars
                    else:
                        use_precip = None
                    self.add_var_non_domain(
                        self.unique_id,
                        metadata,
                        ebasfile.sample_times,
                        ebasfile.variables[i].values_,
                        ebasfile.variables[i].flags,
                        is_hex=ebasfile.variables[i].is_hex,
                        precip_vars=use_precip)
            if not precip_vars_used:
                for precip in precip_vars:
                    self.add_var_non_domain(
                        precip['id'],
                        precip['metadata'],
                        precip['sample_times'],
                        precip['values'],
                        precip['flags'])

    def add_var_non_domain(
            self, id_, metadata, sample_times, values, flags,
            is_hex=False, precip_vars=None):
        """
        Adds a variable (source not from doamin) to the file set.

        Parameters:
            metadata      metadata dict
            sample_times  sample times list
            values        variable's data
            precip_vars   list of precip variables, each dict:
                          {id_, metadata, sample_times, values, flags}
        Returns:
            None
        """
        if precip_vars is None:
            precip_vars = []
        if len(sample_times) != len(values) or len(sample_times) != len(flags):
            raise RuntimeError("different sample times and values/flags")
        if not sample_times:
            # no samples in interval, do not add data interval
            return
        if self.outstyle in (EBAS_IOSTYLE_SINGLECOLUMN,
                             EBAS_IOSTYLE_MULTICOLUMN_PRECIP):
            # singlecolumn: always create a new file
            result = self.new_result()
            result.setup_non_domain()
            result.sample_times = list(sample_times)
            result._add_variable_nondomain(
                id_, metadata, values, flags,
                2 if self.gen_converted else 0,
                is_hex=is_hex)
            for prec in  precip_vars:
                if len(prec['values']) != len(sample_times) or \
                        len(prec['flags']) != len(sample_times):
                    raise RuntimeError(
                        "different sample times and precip values/flags")
                if self.outstyle == EBAS_IOSTYLE_MULTICOLUMN_PRECIP:
                    (success, _) = result.merge_var_non_domain(
                        prec['id'], prec['metadata'], sample_times,
                        prec['values'], prec['flags'],
                        2 if self.gen_converted else 0)
                    if not success:
                        self._add_prec_var_nondomain(prec)
                else:
                    self._add_prec_var_nondomain(prec)
            return

        if self.outstyle != EBAS_IOSTYLE_MULTICOLUMN:
            raise RuntimeError('Illegal IOSTYLE for add_di')

        # multicolumn: try to merge interval into existing outputfiles
        for result in self.results:
            (success, rem_intv) = result.merge_var_non_domain(
                id_, metadata, sample_times, values, flags,
                2 if self.gen_converted else 0,
                is_hex=is_hex)
            if success:
                for precip in precip_vars:
                    (success, _) = result.merge_var_non_domain(
                        precip['id'], precip['metadata'],
                        precip['sample_times'], precip['values'],
                        precip['flags'],
                        2 if self.gen_converted else 0)
                    if not success:
                        self._add_prec_var_nondomain(precip)
                for intv in rem_intv:
                    # recursively add remaining intervals
                    self.add_var_non_domain(
                        id_, metadata, intv[0], intv[1], intv[2],
                        is_hex=is_hex)
                return

        # multicolumn: only if interval could not be merged - create new file:
        result = self.new_result()
        result.setup_non_domain()
        result.sample_times = list(sample_times)
        result._add_variable_nondomain(
            id_, metadata, values, flags,
            2 if self.gen_converted else 0,
            is_hex=is_hex)
        for prec in  precip_vars:
            if len(prec['values']) != len(sample_times) or \
                    len(prec['flags']) != len(sample_times):
                raise RuntimeError(
                    "different sample times and precip values/flags")
            (success, _) = result.merge_var_non_domain(
                prec['id'], prec['metadata'], sample_times, prec['values'],
                prec['flags'],
                2 if self.gen_converted else 0,
                is_hex=False)
            if not success:
                self._add_prec_var_nondomain(prec)

    def _get_precip_dis(self, di_obj, intv):
        """
        Get the list of relevant precipitation amount di's if needed.
        Parameters:
            di_obj   the di object to be added
            intv     interval to be merged in (start, end) (datetime.datetime)
        Returns:
            precip_dis  (list of EbasDomDI relevant for export
        """
        if self.precip_amount and di_obj.ds.is_precip_concentration():
            precip_dis = list(di_obj.precip())
            i = 0
            while i < len(precip_dis):
                # overlap concentration  and amount time coverage, sample start
                # end times according to precip submission:
                prec_intv = precip_dis[i].su.sa.interval(
                    intv.overlap(precip_dis[i].VALIDTIME))
                if prec_intv is None:
                    # precip di has no coverage for interval
                    del precip_dis[i]
                elif precip_dis[i].have_access(prec_intv) == False:
                    self.logger.warning(
                        'no access to amount DS {} [{:19.19s}  {:19.19s}] '
                        'for concentration DS {}'.\
                            format(precip_dis[i].ds.DS_SETKEY,
                                   prec_intv[0].strftime('%Y-%m-%dT%H:%M:%S'),
                                   prec_intv[1].strftime('%Y-%m-%dT%H:%M:%S'),
                                   di_obj.ds.DS_SETKEY))
                    del precip_dis[i]
                else:
                    i += 1
            if not precip_dis:
                self.logger.warning(
                    'no precipitation amount for DS {} [{:19.19s}  {:19.19s}]'.\
                    format(di_obj.ds.DS_SETKEY,
                           intv[0].strftime('%Y-%m-%dT%H:%M:%S'),
                           intv[1].strftime('%Y-%m-%dT%H:%M:%S')))
        else:
            precip_dis = []
        return precip_dis

    def new_result(self):
        """
        Adds a new result to the resultset.

        Parameters:
            None
        Returns:
            result object (nasa_ames, xml, csv, netcdf)
        """
        if self.outformat == EBAS_IOFORMAT_OPENDAP:
            if self.noextract:
                # when noextract is set, access_log will be added in
                # make_dataset
                new_result = self.result_class(access_log=self.access_log,
                                               indexdb=self.indexdb)
            else:
                new_result = self.result_class(indexdb=self.indexdb)
        elif self.outformat == EBAS_IOFORMAT_XML:
            new_result = self.result_class(self.result_num,
                                           indexdb=self.indexdb)
        else:
            # EBAS_IOFORMAT_NASA_AMES, EBAS_IOFORMAT_CSV,
            # EBAS_IOFORMAT_NETCDF1, EBAS_IOFORMAT_NETCDF
            new_result = self.result_class(indexdb=self.indexdb)

        # This is important:
        # Whenever data are exported from domain to ebas.io, we set
        # the export_state and the export_filter in the output file's metadata.
        # Thus we make sure this information comes whis all files exported from
        # ebas.
        new_result.metadata.export_state = self.export_state
        new_result.metadata.export_filter = self.export_filter
        self.results.append(new_result)
        self.result_num += 1
        return new_result

    def extract_all(self):
        """
        Extracts all results in the set.
        """
        if not self.noextract:
            # first, expand all results if needed
            if self.expand and \
               self.outstyle == EBAS_IOSTYLE_MULTICOLUMN:
                for result in self.results:
                    result.expand_multicolumn()
            # then create additional precipitation results - those should be
            # single column and __not__ expanded.
            self._export_prec_di()
            self._export_prec_var_nondomain()
            if self.long_timeseries:
                self._join_years()
                if self.doi and len(self.results) == 0:
                    if self.nodata and self.restricted:
                        raise NoDataDOI(
                            'No data for DOI because of access restrictions')
                    raise RuntimeError('unexpectedly no data')
                if self.doi and self.outformat == EBAS_IOFORMAT_NETCDF and \
                        len(self.results) != 1:
                    # state DOI as NetCDF file should always go to one file...
                    # except: when for some period some ds have access
                    # restrictions. Then the files have different variables
                    # over the years.
                    # Fix here: take the longest sequence of data (#samples)
                    # and throw the rest. self.restricted is already set.
                    if self.restricted:
                        keep = max(enumerate([len(res.sample_times)
                                              for res in self.results]),
                                   key=lambda x: x[1])[0]
                        for i in reversed(range(len(self.results))):
                            if i != keep:
                                del  self.results[i]
                    else:
                        raise RuntimeError('DOI should have 1 NetCDF file')
            if self.doi:
                self.results[0].metadata.doi = [self.doi, None]
                if len(self.results) > 1:
                    i = 1
                    for result in self.results:
                        result.metadata.doi = [self.doi, i]
                        i += 1
            # now write all results
            for result in self.results:
                result.write(createfiles=self.createfiles, destdir=self.destdir,
                             xmlwrap=self.xmlwrap, flags=self.flags,
                             metadata_options=self.metadata_options)
        self.results = []
        if self.clear_caches:
            self.clear_caches.clear()

    def _join_years(self):
        """
        Join results according to the outputformat.
        """
        i = 0
        while i < len(self.results):
            j = i + 1
            while j < len(self.results):
                joined = self.results[i].join(self.results[j])
                if joined:
                    self.results[i] = joined
                    del self.results[j]
                else:
                    j += 1
            i += 1

    def close(self):
        """
        Close resultset: extract all remaining results and shut down.
        """
        self.extract_all()
        if not self.noextract and self.outformat == EBAS_IOFORMAT_XML and \
           not self.createfiles:
            print('</ebas:Result>')
        if not self.noextract and self.xmlwrap:
            xmlwrap_trailer()

    def _add_prec_di(self, pdi, time):
        """
        Add precipitation di and interval to the list of datasets that need
        to be extracted as single column results in the end.
        Parameters:
            pdi       di object of the precipitation amount
            time      time interval needed - tuple (start, end)
                      The time interval that is covered by the concentration
                      timeseries. (interval will be overlapped with amount di
                      coverage)
        Returns:
            None
        """
        # overlap concentration  and amount time coverage, sample start end
        # times according to precip submission:
        overlap = pdi.su.sa.interval(time.overlap(pdi.VALIDTIME))
        # add the overlapping interval
        if pdi in self.prec_di_export:
            self.prec_di_export[pdi].append(overlap)
        else:
            self.prec_di_export[pdi] = [overlap]


    def _export_prec_di(self):
        """
        Extracts the needed precipitation amount intervals that could not be
        added to a multicolumn file. Export is single column here.
        Parameters:
            None
        Returns:
            None
        """
        for di_ in self.prec_di_export:
            i = 0
            while i < len(self.prec_di_export[di_]):
                intv = self.prec_di_export[di_]
                j = i+1
                while j < len(intv):
                    if intv[i][0] < intv[j][1] and intv[i][1] > intv[j][0]:
                        # intervals overlap, join them!
                        intv[i][0] = min(intv[i][0], intv[j][0])
                        intv[i][1] = max(intv[i][1], intv[j][1])
                        del intv[j]
                        break
                    else:
                        j += 1
                else:
                    # if nothing changed in j loop, export and continue with
                    # next i
                    new = self.new_result()
                    new.setup_from_domain(di_, self.prec_di_export[di_][i], 0)
                    i += 1
        self.prec_di_export = {}

    def _add_prec_var_nondomain(self, prec):
        """
        Add precipitation precipitation variable to the list of variables that
        need to be extracted as single column results in the end.
        Parameters:
            prec    precipitation variable specification, dict
                    {id, metadata, sample_times, values, flags}
        Returns:
            None
        """
        if prec['id'] not in self.prec_var_nondomain:
            self.prec_var_nondomain[prec['id']] = prec

    def _export_prec_var_nondomain(self):
        """
        Extracts the needed precipitation amount variables that could not be
        added to a multicolumn file. Export is single column here.
        This handles only non domain variables (i.e. variables which were NOT
        exported from EBAS.
        Parameters:
            None
        Returns:
            None
        """
        for _, prec in self.prec_var_nondomain.items():
            result = self.new_result()
            result.setup_non_domain()
            result.sample_times = list(prec['sample_times'])
            result._add_variable_nondomain(
                prec['id'], prec['metadata'], prec['values'], prec['flags'],
                2 if self.gen_converted else 0)
        self.prec_var_nondomain = {}
