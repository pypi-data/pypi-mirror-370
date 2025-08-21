"""
ebas/io/netcdf/base.py
$Id$

EBAS NetCDF base class

"""

from ..basefile.file import EbasJoinedFile
from ..base import EBAS_IOFORMAT_NETCDF

class EbasNetcdfBase(EbasJoinedFile):  # pylint: disable=R0901, W0223,
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Base class for all EBAS netcdf classes.
    """

    # IOFORMAT = EBAS_IOFORMAT_NETCDF  # set in final object, as long as we have
    # two versions.... 

    def __init__(self, *args, **kwargs):
        """
        Class initialization.
        """
        EbasJoinedFile.__init__(self, *args, **kwargs)
        self.ncfile = None
        # self.strict_global depends on version 1 or two, see netcdf.py

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
        EbasJoinedFile.gen_filename(self, createfiles=createfiles,
                                    destdir=destdir, extension=".nc")
