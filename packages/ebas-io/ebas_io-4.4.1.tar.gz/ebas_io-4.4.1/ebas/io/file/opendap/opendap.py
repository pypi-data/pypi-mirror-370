"""
$Id: opendap.py 1625 2017-05-23 11:25:04Z pe $

EBAS OPeNDAP module
"""

from .write import EbasOPeNDAPPartialWrite

class EbasOPeNDAP(EbasOPeNDAPPartialWrite):
    """
    EBAS I/O OPeNDAP.
    This is a partial class (only write is implemented for OPeNDAP).
    """
    pass
