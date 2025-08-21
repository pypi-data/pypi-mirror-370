"""
$Id: sqlite.py 2599 2021-01-27 16:27:04Z pe $

Helper module fro accessing sqlite3 databases.
"""

import logging
import uuid
import six
from textwrap import dedent
import sqlite3
from sqlite3 import OperationalError  # @UnusedImport pylint: disable=W0611
# W0611: Unused OperationalError imported from sqlite3 (unused-import)
# --> needed for re-export
from nilutility.datatypes import DataObject
from .base import DbBase

class SqliteDb(DbBase):
    """
    Base class for sqlite3 database access.
    """

    # Used by base class
    DB_MAXLEN_IDENTIFIER = None

    def __init__(self, filename):
        """
        Initialize DB connection. Open DB.
        Parameters:
            filename   filename for the database.
        Returns:
            None
        Raises:
            e.g. sqlite3.OperationalError, most usual exceptions to catch by
            caller:
                except OperationalError as excpt:
                    if excpt.message == 'unable to open database file':
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.filename = filename
        self.dbh = None
        self.tmp_addsql_crit_tables = []
        self.open()

    def open(self):
        """
        Open the database. If the file does not exists, create anew one.
        Parameters:
            None
        Returns:
            None
        Raises:
        Raises:
            e.g. sqlite3.OperationalError, most usual exceptions to catch by
            caller:
                except OperationalError as excpt:
                    if excpt.message == 'unable to open database file':
        """
        self.logger.info('open database %s', self.filename)
        self.dbh = sqlite3.connect(
            self.filename,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
        # not needed, returns unicode in python2 and str in python3
        # self.dbh.text_factory =
        self.execute("pragma foreign_keys=1")
        self.logger.debug("database opened")

    def close(self):
        """
        Close the db connection, cleanup.
        """
        self.dbh.close()
        self.filename = None

    def commit(self):
        """
        Commit changes in the connection.
        """
        # Make sure the temporary entries in TMP_ADDSQL_CRIT are never committed
        self._cleanup_addsql_crit()  # just in case...
        self.dbh.commit()

    def rollback(self):
        """
        Rollback changes in the connection.
        """
        self.dbh.rollback()

    def execute(self, sql, parameters=None):
        """
        Perform a DB execute on a new cursor, additionally add error logging.

        Parameters:
            sql         the sql statement
            parameters  parameters for the statement (eiter tuple or dict)
                        (both handled down to curs.execute)
        Returns:
            new cursor object
        """
        self.logger.debug("execute: %s", sql)
        # parameters is either a dict or an iterable (list, tuple etc)
        # no mixed form allowed in sqlite3 API
        if parameters and isinstance(parameters, dict):
            self.logger.debug(
                "execute - PARAMS:\n %s",
                '\n '.join(['{}: {} ({})'.format(key, value, type(value))
                            for (key, value) in list(parameters.items())]))
        elif parameters:
            self.logger.debug(
                "execute - PARAMS:\n %s",
                '\n '.join(['{} ({})'.format(val, type(val))
                            for val in parameters]))
        curs = self.dbh.cursor()
        if parameters:
            curs.execute(sql, parameters)
        else:
            curs.execute(sql)
        return curs

    def executemany(self, sql, parameters):
        """
        Perform a DB execute on a new cursor, additionally add error logging.

        Parameters:
            sql         the sql statement
            parameters  parameters for the statement (eiter tuple or dict)
                        (both handled down to curs.execute)
        Returns:
            new cursor object
        """
        self.logger.debug("execute: %s", sql)
        # parameters is an iterable of iterables (list, tuple etc)
        if parameters:
            self.logger.debug(
                "execute - PARAMS:\n %s",
                '\n '.join(['{} ({})'.format(val, type(val))
                            for row in parameters[:100]
                            for val in row]))
        curs = self.dbh.cursor()
        curs.executemany(sql, parameters)
        return curs

    @staticmethod
    def _convert_row2dict(result, desc):
        """
        Converts a fetched row (tupel) to a dictionary (keys=colnames).

        Parameters:
            result    fetched result row (tupel)
            desc      cursor description
        """
        ret = DataObject()
        for i, item in enumerate(result):
            colnam = desc[i][0]
            ret[colnam] = item
        return ret

    @classmethod
    def _convert_rows2dictlist(cls, resultlist, desc):
        """
        Converts a fetched row (tupel) to a dictionary (keys=colnames).

        Parameters:
            resultlist  fetched result rows (list of tupel)
            desc        cursor description
        """
        ret = []
        for row in resultlist:
            ret.append(cls._convert_row2dict(row, desc))
        return ret

    @staticmethod
    def _hostvar_sql(varname):
        """
        Returns the sql part of a host variable name.
        """
        return ":{}".format(varname)

    @staticmethod
    def _hostvar_param(varname):
        """
        Returns the parameter dictionary key for a host variable.
        """
        return varname

    def _insert_addsql_crit(self, in_list):
        """
        Insert table entries for addsql_crit.
        Parameters:
            in_list    list of criteria values
        Returns:
            temp_id    id for the values in the temp table
        """
        if any([isinstance(elem[1], six.string_types) for elem in in_list]):
            valtype = 'VAL_CHR'
        elif any([isinstance(elem[1], float) for elem in in_list]):
            valtype = 'VAL_DBL'
        else:
            valtype = 'VAL_INT'
        temp_sql = dedent("""\
             insert into TMP_ADDSQL_CRIT (ID, TIME, {})
                 values (:ID, CURRENT_TIMESTAMP, :VAL)""".format(valtype))
        temp_id = uuid.uuid1().hex
        self.tmp_addsql_crit_tables.append(temp_id)
        temp_params = {'ID': temp_id}
        for elem in in_list:
            temp_params['VAL'] = elem[1]
            self.execute(temp_sql, temp_params)
        return "select {} from TMP_ADDSQL_CRIT where ID='{}'".format(
            valtype, temp_id)

    def _cleanup_addsql_crit(self):
        """
        Cleanup temp table entries from addsql_crit
        Parameters:
            None
        Returns:
            None
        """
        sql = "delete from TMP_ADDSQL_CRIT where ID=:ID"
        params = {}
        for id_ in self.tmp_addsql_crit_tables:
            params['ID'] = id_
            self.execute(sql, params)
        self.tmp_addsql_crit_tables = []
