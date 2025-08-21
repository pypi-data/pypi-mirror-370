"""
/Xml/base.py
$Id: ebas_diffexport.py 2466 2020-07-10 13:20:48Z pe $

Base class for XML.
Has (still) all attributes as base class for Nasa Ames 1001.

History:
V.1.0.0  2015-02-16  pe   initial version

"""
import logging
from .generateDS_ebas_diffexport import ebas_diffexport
import sys
import os
import pytz
from six import string_types

class DiffXmlError(Exception):
    """
    Error class for XML.
    """
    pass

class DiffXmlFileExists(DiffXmlError):
    """
    Exception class raised when the DB file already exists.
    """
    pass

class EbasDiffExportXML(object):
    """
    EbasDiffExportXML
    """

    def __init__(self, db_state, diff_state, xmlfile):
        """
        Initialize diffExport xml object
        Paramaters:
            db_state     database state for export. datetime.datetime
            diff_state   diff state for database export datetime.datetime
            Both parameters must be either tz naive or tz=UTC (if naive, time
            zone is set to UTC)
        Returns:
            None
        Raises:
            IOError            if xmlfile cannot be opened
            DiffXmlFileExists  if xmlfile exists already
            DiffXmlError       on other errors
        """
        self.logger = logging.getLogger("diffExportXML")
        if xmlfile is None or xmlfile == '-':
            self.file = sys.stdout
            self.logger.debug("writing diffxml to stdout")
        elif isinstance(xmlfile, string_types):
            if os.path.exists(xmlfile):
                raise DiffXmlFileExists('file {} exists'.format(xmlfile))
            self.logger.debug("writing diffxml to file %s", xmlfile)
            self.file = open(xmlfile, "w")
        else:
            self.file = xmlfile
            self.logger.debug("writing diffxml to stream")

        if db_state.tzinfo and db_state.tzinfo != pytz.timezone('UTC'):
            raise DiffXmlError('time zone: only UTC or naive allowed')
        elif not db_state.tzinfo:
            db_state = pytz.utc.localize(db_state)
        if diff_state.tzinfo and diff_state.tzinfo != pytz.timezone('UTC'):
            raise DiffXmlError('time zone: only UTC or naive allowed')
        elif not diff_state.tzinfo:
            diff_state = pytz.utc.localize(diff_state)

        self.diff_export = ebas_diffexport.diffExportType(dbState=db_state,
                                                          diffState=diff_state)



    def add_deleted(self, dataset_key, start_time, end_time):
        """
        Adds a deleted interval entry.
        Parameters:
            datasetKey     the ds_setkey for the data
            startTime      start time of the deleted interval
            endTime        end time of the deleted interval
        Returns:
            None
        """
        if start_time.tzinfo and start_time.tzinfo != pytz.timezone('UTC'):
            raise DiffXmlError('time zone: only UTC or naive allowed')
        elif not start_time.tzinfo:
            start_time = pytz.utc.localize(start_time)
        if end_time.tzinfo and end_time.tzinfo != pytz.timezone('UTC'):
            raise DiffXmlError('time zone: only UTC or naive allowed')
        elif not end_time.tzinfo:
            end_time = pytz.utc.localize(end_time)
        deleted = ebas_diffexport.dataIntervalType(datasetKey=dataset_key,
                                                   startTime=start_time,
                                                   endTime=end_time)
        self.diff_export.add_deleted(deleted)

    def add_added(self, dataset_key, start_time, end_time):
        """
        Adds an added interval entry.
        Parameters:
            datasetKey     the ds_setkey for the data
            startTime      start time of the added interval
            endTime        end time of the added interval
        Returns:
            None
        """
        if start_time.tzinfo and start_time.tzinfo != pytz.timezone('UTC'):
            raise DiffXmlError('time zone: only UTC or naive allowed')
        elif not start_time.tzinfo:
            start_time = pytz.utc.localize(start_time)
        if end_time.tzinfo and end_time.tzinfo != pytz.timezone('UTC'):
            raise DiffXmlError('time zone: only UTC or naive allowed')
        elif not end_time.tzinfo:
            end_time = pytz.utc.localize(end_time)
        added = ebas_diffexport.dataIntervalType(datasetKey=dataset_key,
                                                 startTime=start_time,
                                                 endTime=end_time)
        self.diff_export.add_added(added)

    def write(self):
        """
        Writes the file.
        Parameters:
            filespec    file name (incl. path) or file like object (stream)
                        stdout if not passed
        Returns:
            None
        """
        self.diff_export.export(self.file, 0, name_='diffExport')
        self.file.close()

