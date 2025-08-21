"""
ebas/io/csv/base.py
$Id: base.py 2519 2020-10-30 16:13:09Z pe $

EBAS CSV base class

"""

from ..basefile.file import EbasFile
from ..base import EBAS_IOFORMAT_CSV

class EbasCSVBase(EbasFile):  # pylint: disable=R0901
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    """
    Base class for all EBAS CSV classes.
    """

    IOFORMAT = EBAS_IOFORMAT_CSV

    def __init__(self, *args, **kwargs):
        """
        Class initioalization.
        """
        EbasFile.__init__(self, *args, **kwargs)
        self.strict_global = False   # EBAS CSV does NOT use strict_global
        # add additional attributes:
        self.csv = None
        self.header = None
        self.var_metadata = None
        self.var_meta_tags = None
        self.var_characteristics = None
        self.var_char_keys = None

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
                              extension=".csv")

    def _read(self, *args, **kwargs):  # pylint: disable=W0613
        # W0613: Unused argument
        """
        Read is not implemented for csv.
        """
        raise RuntimeError('Read is not implemented for csv.')
