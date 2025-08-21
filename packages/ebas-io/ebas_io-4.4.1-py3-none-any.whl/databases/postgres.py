"""
$Id: postgres.py 2599 2021-01-27 16:27:04Z pe $

Helper module fro accessing PostgreSQL databases.

# Synopsis:

## Build an application db access class

Advantage: convert strings to unicode, log executes as debug, make use of
           _convert_row2dict and _convert_rows2dictlist

```python
class MyDbAccess(PostgresDbBase):
    def seltestdata(self):
        curs = self.conn.cursor()
        curs.execute('select * from test')
        return self._convert_rows2dictlist(curs.fetchall(), curs.description)

...

db = MyDbAccess(host=host, user=user, password=password, dbname=dbname)
print db.seltestdata()
print db.seltestdata()[1].columnname
```

## Use customized classes w/o creating a dedicated db layer class:

e.g. for small scripts.
Advantage: convert strings to unicode, log executes as debug.

```python
import databases.postgres
import psycopg2

con = psycopg2.connect(
    host=None, user='paul', password=None, dbname='paul',
    connection_factory=databases.postgres.PostgresDbConnection,
    cursor_factory=databases.postgres.PostgresDbCursor)
curs = con.cursor()
curs.execute('select * from test')
print list(curs.fetchall())
```
"""

import logging
import uuid
from textwrap import dedent
import psycopg2
from psycopg2 import Error as DbError  # for import in clients
from psycopg2.extras import execute_values
import six
import re
import datetime
import psycopg2.extensions
from nilutility.datetime_helper import DatetimeInterval
from nilutility.datatypes import DataObject
from .base import DbBase

# make sure strings are converted form database character set to unicode
# in python2 (in python3 it's default)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

class PostgresDbConnection(psycopg2.extensions.connection):
    # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Derived class for a postgeres connection object.
    """

    def commit(self):
        """
        Log commit with severity debug.
        """
        logger = logging.getLogger('PostgresDb')
        logger.debug(
            'commit transaction (%s)', self.appname)
        psycopg2.extensions.connection.commit(self)

    def rollback(self):
        """
        Log commit with severity debug.
        """
        logger = logging.getLogger('PostgresDb')
        logger.debug(
            'rollback transaction (%s)', self.appname)
        psycopg2.extensions.connection.rollback(self)

    @property
    def appname(self):
        """
        Get the application_name from dsn_parameters, None as fallback
        """
        try:
            return self.get_dsn_parameters()['application_name']
        except KeyError:
            return None


class PostgresDbCursor(psycopg2.extensions.cursor):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Logging cursor object. Logs every execute with severity debug, logs
    exceptions as error.
    """
    def execute(self, query, vars_=None):
        """
        Log execute with severity debug, log exceptions as error.
        Parameters
        """
        logger = logging.getLogger('PostgresDb')
        logger.debug(u'execute: %s', self.mogrify(query, vars_))
        try:
            psycopg2.extensions.cursor.execute(self, query, vars_)
        except Exception as exc:
            logger.error("%s: %s", exc.__class__.__name__, exc)
            raise

    def executemany(self, query, vars_list):
        """
        Log executemany with severity debug, log exceptions as error.
        Parameters
        """
        logger = logging.getLogger('PostgresDb')
        logger.warning(
            'executemany method is not performing well, consider using '
            'the execute_values method')
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug('executemany: %s', query)
            for _, vars_ in enumerate(vars_list):
                if isinstance(vars_, dict):
                    logger.debug(
                        'executemany vars: %s',
                        ', '.join(
                            ['{0}: {1} ({2})'.format(key, value, type(value))
                             for (key, value) in list(vars_.items())]))
                else:
                    logger.debug('executemany vars_list: %s', vars_)
        try:
            psycopg2.extensions.cursor.executemany(self, query, vars_list)
        except Exception as exc:
            logger.error("%s: %s", exc.__class__.__name__, exc)
            raise

    def execute_values(self, sql, argslist, template=None, page_size=100,
                       fetch=False):
        """
        Log execute_values with severity debug, log exceptions as error.
        Parameters:
            sql        the query to execute.
                       It must contain a single %s placeholder, which will be
                       replaced by a VALUES list.
            argslist   sequence of sequences or dictionaries with the arguments
                       to send to the query.
            template   the snippet to merge to every item in argslist to compose
                       the query.
                       (e.g. "(%s, %s, %s)", or "(%s, %s, 42)" for const values)
                       If not specified, assume the arguments are sequence and
                       use a simple positional template (i.e. (%s, %s, ...))
            page_size  maximum number of argslist items to include in every
                       statement. If there are more items the function will
                       execute more than one statement.
            fetch      if True return the query results into a list (like in a
                       fetchall()). Useful for queries with RETURNING clause.
        Returns:
            None or list
        """
        logger = logging.getLogger('PostgresDb')
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug('execute_values: %s', sql)
            logger.debug('execute_values template: %s', template)
            logger.debug('execute_values page_size: %s', page_size)
            logger.debug('execute_values fetch: %s', fetch)
            for _, args in enumerate(argslist):
                if isinstance(args, dict):
                    logger.debug(
                        'execute_values args: %s',
                        ', '.join(
                            ['{0}: {1} ({2})'.format(key, value, type(value))
                             for (key, value) in list(args.items())]))
                else:
                    logger.debug('execute_values args: %s', args)
        try:
            execute_values(self, sql, argslist, template=template,
                           page_size=page_size, fetch=fetch)
        except Exception as exc:
            logger.error("%s: %s", exc.__class__.__name__, exc)
            raise


class PostgresDbBase(DbBase):
    """
    Base class for application database layer classes (should be derived from
    this class).
    """

    # Used by base class
    DB_MAXLEN_IDENTIFIER = 63

    def __init__(self):
        """
        Initialize DB connection. Open DB.
        Parameters:
            all parameters accepted by psycopg2.connect
            most prominent:
                dbname, user, password, host, port
        Returns:
            None
        Additional parameters can be either suplied by keyword parameters or a
        dsn connection sting. See:
        https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cursor_fetch_buffer = 1000
        self.tmp_addsql_crit_tables = []
        self.conn = None

    def _connect(self, connection_factory=None, cursor_factory=None, **kwargs):
        """
        Connect the database.
        Parameters:
            all parameters accepted by psycopg2.connect
        Returns:
            connection   can't sett self.conn (must also work for additional
                         conn's (e.g. EbasDb.conn_ts)
                         thus, the conn is returned and self.xxx is set by the
                         caller
        Additional parameters can be either suplied by keyword parameters or a
        dsn connection sting. See:
        https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        """
        if connection_factory is None:
            connection_factory = PostgresDbConnection
        if cursor_factory is None:
            cursor_factory = PostgresDbCursor
        conn = psycopg2.connect(
            connection_factory=connection_factory,
            cursor_factory=cursor_factory, **kwargs)
        self.logger.debug('connected database %s', conn.get_dsn_parameters())
        # Set the default timezone to UTC
        # The database default is also set to UTC, but to be sure, in case the
        # user set something different on the client side (e.g. env var PGTZ).
        curs = conn.cursor()
        curs.execute("set timezone to 'Etc/UTC'")
        curs.execute("set datestyle to 'ISO'");
        self._typecast_adapt_utc(conn)
        return conn

    def close(self):
        """
        Close the db connection, cleanup.
        """
        self.conn.close()

    def commit(self):
        """
        Commit changes in the connection.
        """
        # Make sure the temporary entries in TMP_ADDSQL_CRIT do not persist
        self._cleanup_addsql_crit()
        self.conn.commit()


    def check_constraints(self):
        """
        Check deferred constraints and constraint triggers.
        (Can be checked in case of no commit)
        """
        self._execute('SET CONSTRAINTS ALL IMMEDIATE')

    def rollback(self):
        """
        Rollback changes in the connection.
        """
        self.conn.rollback()

    def _execute(self, query, vars_=None):
        """
        Provides an execute method for the object (private, only to be used
        internally by derived object's access methods).
        Open a new cursor, execute and return the cursor.
        Includes logging through the customized PostgresDbCursor object.
        Parmeter:
            query    the sql query
            vars_    variables for the query
        Returns:
            cursor object
        """
        curs = self.conn.cursor()
        curs.execute(query, vars_)
        return curs

    def _executemany(self, query, vars_list):
        """
        Provides an executemany method for the object (private, only to be used
        internally by derived object's access methods).
        Open a new cursor and executemany on it.
        Includes logging through the customized PostgresDbCursor.
        WARNING: executemany does not perform well. Use _execute_values for
        better performance if possible (needs different parameters).

        Parmeter:
            query      the sql query
            vars_list  list of variables for the query
        Returns:
            None
        """
        if self.conn.cursor_factory != PostgresDbCursor:
            self.logger.warning(
                'executemany method is not performing well, consider using '
                'PostgresDbCursor as cursor_factoy and the execute_values '
                'method')
        curs = self.conn.cursor()
        curs.executemany(query, vars_list)

    def _execute_values(self, sql, argslist, template=None, page_size=100,
                        fetch=False):
        """
        Provides an execute_values method for the object (private, only to be
        used internally by derived object's access methods).
        Open a new cursor and execute_values on it.
        Includes logging through the customized PostgresDbCursor and is faster
        than the executemany method.

        Parameters:
            sql        the query to execute.
                       It must contain a single %s placeholder, which will be
                       replaced by a VALUES list.
            argslist   sequence of sequences or dictionaries with the arguments
                       to send to the query.
            template   the snippet to merge to every item in argslist to compose
                       the query.
                       (e.g. "(%s, %s, %s)", or "(%s, %s, 42)" for const values)
                       If not specified, assume the arguments are sequence and
                       use a simple positional template (i.e. (%s, %s, ...))
            page_size  maximum number of argslist items to include in every
                       statement. If there are more items the function will
                       execute more than one statement.
            fetch      if True return the query results into a list (like in a
                       fetchall()). Useful for queries with RETURNING clause.
        Returns:
            None or list
        """
        curs = self.conn.cursor()
        curs.execute_values(sql, argslist, template=template,
                            page_size=page_size, fetch=fetch)
        # Exception thrown if curs has no execute_values method, i.e. not a
        # PostgresDbCursor

    def _yield_dict(self, curs):
        """
        Yields the cursur results as dictionary per row.

        Parameters:
            curs    opened cursor object
        Returns:
            generator, dictionaries with results, None if no result
        """
        while True:
            results = curs.fetchmany(self.cursor_fetch_buffer)
            if not results:
                curs.close()
                break
            for result in results:
                yield self._convert_row2dict(result, curs.description)

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
        return "%({})s".format(varname)

    @staticmethod
    def _hostvar_param(varname):
        """
        Returns the parameter dictionary key for a host variable.
        """
        return varname

    def _insert_addsql_crit(self, in_list, alt_curs=None):
        """
        Insert table entries for addsql_crit.
        Parameters:
            in_list    list of criteria values
            alt_cur    alternative cursor to be used (special case for EbasDb)
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
             insert into tmp_addsql_crit (ID, TIME, {})
                 values (%(ID)s, current_timestamp AT TIME ZONE 'UTC',
                 %(VAL)s)""".format(valtype))
        temp_id = uuid.uuid1().hex
        self.tmp_addsql_crit_tables.append(temp_id)
        temp_params = {'ID': temp_id}
        for elem in in_list:
            temp_params['VAL'] = elem[1]
            if alt_curs:
                alt_curs.execute(temp_sql, temp_params)
            else:
                self._execute(temp_sql, temp_params)
        return "select {} from tmp_addsql_crit where ID='{}'".format(
            valtype, temp_id)

    def _cleanup_addsql_crit(self, alt_curs=None):
        """
        Cleanup temp table entries from addsql_crit
        Parameters:
            alt_cur    alternative cursor to be used (special case for EbasDb)
        Returns:
            None
        """
        sql = "delete from tmp_addsql_crit where ID=%(ID)s"
        params = {}
        for id_ in self.tmp_addsql_crit_tables:
            params['ID'] = id_
            if alt_curs:
                alt_curs.execute(sql, params)
            else:
                self._execute(sql, params)
        self.tmp_addsql_crit_tables = []


    ###
    ### timestamp related adapters and casters
    ###
    ### By default, all timestamps will be naive datetime.datetime objects
    ### (timezone unaware). All times are UTC. Always! So no use in carrying
    ### the load of timezone through the code.
    ###
    ### Maybe some application will need alternative implementations...
    ###
    ### The postgres db timestamps are mostly timestamptz, i.e. including
    ### timezone. The db module adapts and casts the types accordingly.

    # compile the regexp just once for performance:
    REG_TSTZ = re.compile(
        r'^(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)(\.\d*)?\+00$')
    REG_TSTZRANGE = re.compile(r"""
        ( \(|\[ )                   # lower bound flag
        (?:                         # lower bound:
          " ( (?: [^"] | "")* ) "   #   - a quoted string
          | ( [^",]+ )              #   - or an unquoted string
        )?                          #   - or empty (not catched)
        ,
        (?:                         # upper bound:
          " ( (?: [^"] | "")* ) "   #   - a quoted string
          | ( [^"\)\]]+ )           #   - or an unquoted string
        )?                          #   - or empty (not catched)
        ( \)|\] )                   # upper bound flag
        """, re.VERBOSE)

    def _typecast_adapt_utc(self, conn):
        """
        Set up all adapters and type casters.
        Parameters:
            conn    connection object (can't use self.conn here, as this must
                    possibly work with other connections too (e.g.
                    EbasDb.conn_ts)
        """

        def cast_timestamptz(value, curs):
            """
            Cast a postgres timstamptz to a naive datetime.datetime.
            """
            if value is None:
                return None
            reg = re.match(self.__class__.REG_TSTZ, value)
            frag = 0 if not reg.group(7) \
                else int(round(float(reg.group(7))*1000000.0))
            return datetime.datetime(
                int(reg.group(1)), int(reg.group(2)), int(reg.group(3)),
                int(reg.group(4)), int(reg.group(5)), int(reg.group(6)),
                frag)

        def adapt_dt(dt_):
            """
            Adapter for datetime.datetime (to timestamptz).
            """
            return psycopg2.extensions.AsIs(
                dt_.strftime("'%Y-%m-%d %H:%M:%S.%f+00'::timestamptz"))

        def cast_tstzrange(value, curs):
            """
            Cast a postgres tstzrange to a DatetimeInterval with naive datetime
            elements.
            """
            if value == 'empty':
                return DatetimeInterval.empty()
            reg = re.match(self.__class__.REG_TSTZRANGE, value)
            return DatetimeInterval(
                cast_timestamptz(reg.group(2), curs) if reg.group(2) else
                cast_timestamptz(reg.group(3), curs) if reg.group(3) else None,
                cast_timestamptz(reg.group(4), curs) if reg.group(4) else
                cast_timestamptz(reg.group(5), curs) if reg.group(5) else None,
                bounds=reg.group(1) + reg.group(6))

        def adapt_dtint(dt_):
            """
            Adapter for DatetimeInterval (to tstzrange).
            """
            if dt_.is_empty():
                return psycopg2.extensions.AsIs("'empty'::tstzrange")
            return psycopg2.extensions.AsIs(
                """'{}{},{}{}'::tstzrange""".format(
                    dt_.bounds[0],
                    '"{}"'.format(dt_[0].strftime('%Y-%m-%d %H:%M:%S.%f+00')) \
                        if dt_[0] else '',
                    '"{}"'.format(dt_[1].strftime('%Y-%m-%d %H:%M:%S.%f+00')) \
                        if dt_[1] else '',
                    dt_.bounds[1]))

        curs = conn.cursor()
        curs.execute("select current_timestamp")
        tstztype = psycopg2.extensions.new_type(
            (curs.description[0][1],), "timestamptz", cast_timestamptz)
        # Register type conversion, limit scope to only the two ebas.db
        # connections. Otherwise problems with other code parts which use
        # another database interface.
        psycopg2.extensions.register_type(tstztype, conn)

        psycopg2.extensions.register_adapter(datetime.datetime, adapt_dt)

        curs = conn.cursor()
        curs.execute("select '[2021-01-01, 2022-01-01)'::tstzrange")
        tstzrangetype = psycopg2.extensions.new_type(
            (curs.description[0][1],), "tstzrange", cast_tstzrange)
        # Register type conversion, limit scope to only the two ebas.db
        # connections. Otherwise problems with other code parts which use
        # another database interface.
        psycopg2.extensions.register_type(tstzrangetype, conn)

        psycopg2.extensions.register_adapter(DatetimeInterval, adapt_dtint)


class PostgresDb(PostgresDbBase):
    """
    Final class for database access in Postgres. Using mainly the execute method
    (client needs to formulate the sql).
    This class is meant to be used for more ad-hoq dataabase queries. Derived
    classes which aim to provide a set of customized db access methods for an
    application, should be derived from PostgresDbBase instead of this class.
    See e.g. ebas/db4 for amore advanced final implementation.
    """

    def __init__(self, **kwargs):
        """
        Initialize DB connection. Open DB.
        Parameters:
            all parameters accepted by psycopg2.connect
            most prominent:
                dbname, user, password, host, port
        Returns:
            None
        Additional parameters can be either suplied by keyword parameters or a
        dsn connection sting. See:
        https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        """
        PostgresDbBase.__init__(self)
        self.conn = self._connect(**kwargs)

    def execute(self, *args, **kwargs):
        """
        Wrapper method to expose base classes _execute as public.
        See PostgresDbBase._execute

        Open a new cursor, execute and return the cursor.
        Includes logging through the customized PostgresDbCursor object.
        Parmeter:
            query    the sql query
            vars     variables for the query
        Returns:
            cursor object
        """
        return self._execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        """
        Wrapper method to expose base classes _executemany as public.
        See PostgresDbBase._executemanty
        Open a new cursor and executemany on it.
        Includes logging through the customized PostgresDbCursor object.
        Parmeter:
            query      the sql query
            vars_list  list of variables for the query
        Returns:
            None
        """
        self._executemany(*args, **kwargs)

    def execute_values(self, *args, **kwargs):
        """
        Wrapper method to expose base classes _execute_values as public.
        See PostgresDbBase._execute_values
        Open a new cursor and execute_values on it.
        Includes logging through the customized PostgresDbCursor object.
        Parameters:
            sql        the query to execute.
                       It must contain a single %s placeholder, which will be
                       replaced by a VALUES list.
            argslist   sequence of sequences or dictionaries with the arguments
                       to send to the query.
            template   the snippet to merge to every item in argslist to compose
                       the query.
                       (e.g. "(%s, %s, %s)", or "(%s, %s, 42)" for const values)
                       If not specified, assume the arguments are sequence and
                       use a simple positional template (i.e. (%s, %s, ...))
            page_size  maximum number of argslist items to include in every
                       statement. If there are more items the function will
                       execute more than one statement.
            fetch      if True return the query results into a list (like in a
                       fetchall()). Useful for queries with RETURNING clause.
        Returns:
            None or list
        """
        self._execute_values(*args, **kwargs)
