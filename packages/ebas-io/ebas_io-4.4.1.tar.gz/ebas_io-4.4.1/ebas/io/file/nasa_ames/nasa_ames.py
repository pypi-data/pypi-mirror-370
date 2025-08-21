"""
ebas/nasa_ames/nasa_ames.py
$Id: nasa_ames.py 1527 2017-02-15 18:36:36Z pe $

EBAS NASA Ames module

! Attention !
Basic Nasa Ames 1001 functionality is implemented in the NasaAmes1001 class.
The ebas/nasa_ames (this) module is about EBAS extentions for Nasa Ames and
implements an interface to the ebas domain class (DB)

History:
V.1.0.0  2012-10-15  pe  initial version

"""

from .write import NasaAmesPartialWrite
from .read.read import NasaAmesPartialRead

class EbasNasaAmes(NasaAmesPartialWrite,   #pylint: disable-msg=R0901,R0904
                   NasaAmesPartialRead):
    # R0901: Too many ancestors
    # R0904: Too many public methods
    # This is a quite big partial class, therefore we ignore this warning
    """
    Nasa Ames I/O object.
    This is a partial class distributed over many source files.
    """

