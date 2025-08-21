"""
$Id: base.py 2466 2020-07-10 13:20:48Z pe $

EBAS Offline Masterdata base class

History:
V.1.1.0  2016-10-11  pe  initial version

"""

import pickle
import six

class OfflineMasterDataBase(object):
    """
    Base class for handling Offline Masterdata
    """
    # file name
    META_FILE = None  # To be set by client class
    META = {}
    INIT = False


    @classmethod
    def read_pickle_file(cls):
        """
        Reads the mastedata from the pickle file.
        Parameters:
            None
        Returns:
            None
        """
        _file = open(cls.META_FILE, 'rb')
        # Pickle format is different between python2 and 3
        # As long as we use python2 pickles (we need to, because the DB is
        # sybase and we have only a db module for python2), we will decode
        # the python2 pickles in python3
        if six.PY2:
            cls.META = pickle.load(_file)
        else:
            cls.META = pickle.load(_file, encoding='latin1')
            # TODO: use latin1 as long as pickles are written with py2,
            # then remove encoding (use utf-8)

    @classmethod
    def write_pickle_file(cls, dbh):
        """
        Recreates the pickle file from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.from_db(dbh)
        _file = open(cls.META_FILE, 'wb')
        pickle.dump(cls.META, _file)

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        raise NotImplementedError
        
