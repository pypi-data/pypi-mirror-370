"""
ebas/io/nasa_ames/base.py
$Id: base.py 2519 2020-10-30 16:13:09Z pe $

EBAS NASA Ames base class

"""

from ..basefile.file import EbasFile
from ...base import EbasIOError
from ..base import EBAS_IOFORMAT_NASA_AMES

class EbasNasaAmesReadError(EbasIOError):
    """
    Exception class for NasaAmes read errors.
    """
    pass

class EbasNasaAmesBase(EbasFile):  # pylint: disable=W0223
    # W0223: Method ... is abstract in base class but is not overridden
    # This is also an abstract class, just does not raise NotImplementedError
    """
    Base class for all EBAS Nasa Ames classes.
    """
    # set exception for generic read method
    READ_EXCEPTION = EbasNasaAmesReadError
    IOFORMAT = EBAS_IOFORMAT_NASA_AMES

    def __init__(self, *args, **kwargs):
        """
        Class initioalization.
        """
        EbasFile.__init__(self, *args, **kwargs)
        # add one additional attribute:
        self.nasa1001 = None
        self.strict_global = False   # EBAS Nasa Ames does NOT use strict_global

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
        EbasFile.gen_filename(self, createfiles=createfiles,
                              destdir=destdir, extension=".nas")
