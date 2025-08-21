"""
$Id: base.py 2640 2021-03-26 22:51:02Z pe $
"""

import re
import six

class DbBase(object):
    """
    Base class for database helper class.
    """

    # Specifics about database system, MUST be set by derived class:
    # Is there a limit for column name length? None, no limit, otherwise int
    DB_MAXLEN_IDENTIFIER = None

    @classmethod
    def addsql_crit(cls, column, crit, params, dbh=None, negation=False):
        # pylint: disable=R0912,R0915
        # R0912: too many branches
        # R0915: Too many statements
        # --> refactoring does not make much sense currently
        """
        Add one criteria to SQL where clause.

        Parameters:
            column  name of criteria column (db column name)
            crit    either:
                    -single value (criteria -> equal)
                    -list of values ("in" options)
                    -dictionary (min, max)
            params  params dictionary for the execution (bind variables)
                    (will be added)
            negation
                    True/False: True: do the opposit (not equal, not in list...)
            dbh     EbasDb database access object (substitute for self)
                    Only provide this parameter when the connected database has
                    a table TMP_SQL_CRIT.
                    This method should generally be a static method, thus we add
                    an optional "self" as dbh.
                    Used to insert into temp table for criteria selection
                    with many criteria in list.
                    If ommitted, addsql_crit will only be able to create
                    statements with long "in ()" ists, which might crash in
                    extreme cases (some hundred list elements?)
        Returns:
            string  SQL text for this criteria

        Example:
            addsql_in("DS.DS_SETKEY", [1,10,100,1000], params)
            --> " where DS.DS_SETKEY in (@DS.DS_SETKEY1,@DS.DS_SETKEY2,...)"
                and params = {'@DS.DS_SETKEY1': 1, '@DS.DS_SETKEY2': 10, ...}
        """
        sql = ""
        var = cls.get_hostvar_name(column, params)
        if isinstance(crit, list) and crit:
            # criteria is a list
            like_list = []
            in_list = []
            for (i, elem) in enumerate(crit):
                if isinstance(elem, six.string_types) and re.search('%', elem):
                    like_list.append((i, elem))
                elif isinstance(elem, six.string_types):
                    in_list.append((i, elem))
                else:
                    in_list.append((i, elem))
            if len(like_list) > 1 or (like_list and in_list):
                sql += "("
            if len(in_list) == 1:
                sql += "{}{}{}".format(
                    column, "!=" if negation else "=",
                    cls._hostvar_sql(var+'_'+str(in_list[0][0])))
                params[cls._hostvar_param(var+'_'+str(in_list[0][0]))] = \
                    in_list[0][1]
            elif dbh and len(in_list) > 20:
                # insert criteria values into temp table:
                # pylint: disable=W0212
                # W0212: Access to a protected member _insert_addsql_crit of a
                #        client  class
                # --> dbh is in fact an optiona "self", i.e. dbh is an instance
                #     of this class
                subsel = dbh._insert_addsql_crit(in_list)
                # add subselect using temp table:
                sql += "{} {}in ({})".format(column, "not " if negation else "",
                                             subsel)
            elif len(in_list) > 1:
                sql += "{} {}in (".format(column, "not " if negation else "")
                comma = ""
                for (i, elem) in in_list:
                    # get a modified name with underscor and number
                    in_var = cls.get_hostvar_name(var, params, offset=i)
                    sql += comma + cls._hostvar_sql(in_var)
                    params[cls._hostvar_param(in_var)] = elem
                    comma = ","
                sql += ")"
            if like_list:
                bind = ""
                if in_list:
                    if negation:
                        bind = " and "
                    else:
                        bind = " or "
                for (i, elem) in like_list:
                    # get a modified name with underscor and number
                    in_var = cls.get_hostvar_name(var, params, offset=i)
                    sql += "{}{} {}like {}".format(
                        bind, column, "not " if negation else "",
                        cls._hostvar_sql(in_var))
                    params[cls._hostvar_param(in_var)] = elem
                    bind = " and " if negation else " or "
            if len(like_list) > 1 or (like_list and in_list):
                sql += ")"
        elif isinstance(crit, list) and not crit:
            # special case, empty list. ... where in () is not valid sql, sq use
            # where 1=2 instead
            # same for negated where in (): use the alway true 1=1
            sql += "1=1" if negation else "1=2"
        elif isinstance(crit, dict):
            if crit["min"] != None and crit["max"] != None:
                sql += "{} {}between {} and {}".format(
                    column, "not " if negation else "",
                    cls._hostvar_sql(var+'_min'),
                    cls._hostvar_sql(var+'_max'))
                params[cls._hostvar_param(var+'_min')] = crit["min"]
                params[cls._hostvar_param(var+'_max')] = crit["max"]
            elif crit["min"] != None:
                sql += "{} {} {}_min".format(
                    column, "<" if negation else ">=", cls._hostvar_sql(var))
                params[cls._hostvar_param(var+'_min')] = crit["min"]
            elif crit["max"] != None:
                sql += "{} {} {}_max".format(
                    column, ">" if negation else "<=", cls._hostvar_sql(var))
                params[cls._hostvar_param(var+'_max')] = crit["max"]
        elif crit is None:
            sql += "{} is{} NULL".format(column, " not" if negation else "")
        elif isinstance(crit, six.string_types) and re.search('%', crit):
            sql += "{} {}like {}".format(
                column, "not " if negation else "", cls._hostvar_sql(var))
            params[cls._hostvar_param(var)] = crit
        else:
            sql += "{}{}{}".format(
                column, "!=" if negation else "=", cls._hostvar_sql(var))
            params[cls._hostvar_param(var)] = crit
        return sql

    @classmethod
    def get_hostvar_name(cls, column, params, offset=None):
        """
        Get a name for host variable in the sql string, add numbers for
        duplicates and check maxlen.
        """
        # check if this column name has already been used as bind variable
        var = re.sub(r'\.', '_', column)
        if cls.DB_MAXLEN_IDENTIFIER and \
                len(cls._hostvar_sql(var)) > cls.DB_MAXLEN_IDENTIFIER:
            # Just truncating is not optimal (name collitions may occur), but
            # best first approach
            trunc = cls.DB_MAXLEN_IDENTIFIER - len(cls._hostvar_sql(var))
            var = var[:trunc]  # trunc is negative, so tuncate the last charars
        # try to add _ and a number as long as column name is not unique:
        if offset:
            i = offset
        else:
            i = 1
        testvar = cls._hostvar_sql(var)  # syntax is DB dependent...
        while offset or \
                sum([1 if re.match(cls._hostvar_param(var), x) else 0
                     for x in params]) > 0:
            offset = None  # reset offset for 2nd loop (only to force entering)
            var = re.sub(r'\.', '_', column) + '_' + str(i)
            if cls.DB_MAXLEN_IDENTIFIER:
                if len(cls._hostvar_sql(var)) > cls.DB_MAXLEN_IDENTIFIER:
                    trunc = cls.DB_MAXLEN_IDENTIFIER - \
                            len(cls._hostvar_sql(var))
                    var = re.sub(r'\.', '_', column[:trunc]) + '_' + str(i)
            i += 1
            testvar = cls._hostvar_sql(var)
        return var

    @staticmethod
    def _hostvar_sql(varname):
        """
        Returns the sql part of a host variable name.
        Must be implemented in derived classes.
        """
        raise NotImplementedError()

    @staticmethod
    def _hostvar_param(varname):
        """
        Returns the parameter dictionary key for a host variable.
        Must be implemented in derived classes.
        """
        raise NotImplementedError()

    def _insert_addsql_crit(self, in_list):
        """
        Insert table entries for addsql_crit.
        Parameters:
            in_list    list of criteria values
        Returns:
            temp_id    id for the values in the temp table

        Must be implemented in derived classes.
        """
        raise NotImplementedError()

    def _cleanup_addsql_crit(self):
        """
        Cleanup temp table entries from addsql_crit
        Parameters:
            None
        Returns:
            None

        Must be implemented in derived classes.
        """
        raise NotImplementedError()
