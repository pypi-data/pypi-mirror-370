"""
ebas/io/xml/base.py
$Id: base.py 2519 2020-10-30 16:13:09Z pe $

EBAS XML base class

"""

from ..basefile.file import EbasFile
from ..base import EBAS_IOFORMAT_XML

class EbasXMLBase(EbasFile):  # pylint: disable=R0901, W0223,
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    """
    Base class for all EBAS XML classes.
    """

    IOFORMAT = EBAS_IOFORMAT_XML

    def __init__(self, result_id, *args, **kwargs):
        """
        Class initioalization.
        Parameters:
            result_id    increasing number (id for the resultset to be
                         generated) - needed for Xml object creation
        """
        EbasFile.__init__(self, *args, **kwargs)
        self.strict_global = True   # EBAS XML should use strict_global
        # add additional attributes:
        self.xml = None
        self.result_id = result_id

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
                              extension=".xml")
