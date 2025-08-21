"""
ebas/db_fileindex
$Id: __init__.py 2721 2021-10-22 23:02:49Z pe $

Database I/O for EBAS fileindex database (sqlite3)

This module provides the class IndexDb

History:
V.1.0.0  2015-04-02  pe  initial version

"""

import re

# expose main class to users
from sqlite3 import OperationalError
from .indexdb import IndexDb
from .indexdb_internal import IndexDbInternal
