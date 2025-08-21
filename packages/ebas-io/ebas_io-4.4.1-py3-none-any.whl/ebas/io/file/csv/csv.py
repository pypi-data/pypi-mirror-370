"""
ebas/input_output/ebas_csv/ebas_csv.py
$Id: csv.py 1527 2017-02-15 18:36:36Z pe $

EBAS CSV module

! Attention !
Basic CSV functionality is implemented in the Csv class.
The ebas/ebas_csv (this) module
implements an interface to the ebas domain class (DB)

History:
V.1.0.0  2014-07-16  toh  initial version

"""

from .write import EbasCSVPartialWrite

class EbasCSV(EbasCSVPartialWrite):  # pylint: disable=R0901
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    """
    EBAS I/O CSV object.
    This is a partial class distributed over many source files.
    """
