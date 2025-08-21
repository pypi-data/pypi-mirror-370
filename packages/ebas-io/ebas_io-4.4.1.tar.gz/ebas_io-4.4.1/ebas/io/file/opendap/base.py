"""
$Id: base.py 2519 2020-10-30 16:13:09Z pe $

EBAS OPeNDAP base class

"""

from ..basefile.file import EbasFile, EbasJoinedFile
from ..base import EBAS_IOFORMAT_OPENDAP
\
EBAS_OPENDAP_REQUESTTYPE_DDS = 1
EBAS_OPENDAP_REQUESTTYPE_DAS = 2
EBAS_OPENDAP_REQUESTTYPE_DATA = 3

class EbasOPeNDAPBase(EbasJoinedFile):  # pylint: disable=R0901, W0223,
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Base class for all EBAS OPeNDAP classes.
    """

    # EbasOPeNDAP should use lazy read (do not read all data from DB while
    # setting up the opject). Depending on the request, only parts or even
    # nothing is needed.
    LAZY_READ = True
    IOFORMAT = EBAS_IOFORMAT_OPENDAP

    def __init__(self, access_log=None, *args, **kwargs):
        """
        Class initialization.
        """
        EbasJoinedFile.__init__(self, *args, **kwargs)
        self.strict_global = True   # OPeNDAP should use strict_global
        self.dataset = None   # pydap dataset object (destination for output)
        self.cdm_variables = {}
        self.access_log = access_log 

    def gen_filename(self, createfiles=False, destdir=None):
        # pylint: disable-msg=W0221
        # W0221: Arguments number differs from overridden method
        """
        Generates a file name according to NILU file name convention.
        Use the base class functionality but set the file name extension.
        Parameter:
            createfiles   write to physical file?
            destdir       destination directory path for files
        Return:
            None
        """
        EbasFile.gen_filename(self, createfiles=createfiles, destdir=destdir,
                              extension=".dods")
