"""
$Id$

EBAS NetCDF module
"""

from .write import EbasNetCDFPartialWrite
from ..base import EBAS_IOFORMAT_NETCDF, EBAS_IOFORMAT_NETCDF1


class EbasNetcdf(EbasNetCDFPartialWrite):   #pylint: disable-msg=R0901
    # R0901: Too many ancestors
    # This is a quite big partial class, therefore we ignore this warning
    """
    EBAS I/O NetCDF.
    This is a partial class distributed over many source files.
    """
    IOFORMAT = EBAS_IOFORMAT_NETCDF

    def __init__(self, *args, **kwargs):
        """
        Initialize the object.
        NetCDF V2 should use strict_global.
        """
        super(EbasNetcdf, self).__init__(*args, **kwargs)
        self.strict_global = True

class EbasNetcdf1(EbasNetCDFPartialWrite):   #pylint: disable-msg=R0901
    # R0901: Too many ancestors
    # This is a quite big partial class, therefore we ignore this warning
    """
    EBAS I/O NetCDF Version 1. Should be discontinued in the future.
    This is a partial class distributed over many source files.
    """
    IOFORMAT = EBAS_IOFORMAT_NETCDF1

    def __init__(self, *args, **kwargs):
        """
        Initialize the object.
        NetCDF V1 should NOT use strict_global.
        """
        super(EbasNetcdf1, self).__init__(*args, **kwargs)
        self.strict_global = False
