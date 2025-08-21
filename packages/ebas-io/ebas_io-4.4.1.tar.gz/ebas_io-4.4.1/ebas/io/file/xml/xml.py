"""
ebas/nasa_ames/ebas_xml.py
$Id: xml.py 1527 2017-02-15 18:36:36Z pe $

EBAS XML module

! Attention !
Basic XML functionality is implemented in the Xml class.
The ebas/ebas_xml (this) module
implements an interface to the ebas domain class (DB)

History:
V.1.0.0  2014-08-05  toh  initial version

"""

from .write import EbasXMLPartialWrite

class EbasXML(EbasXMLPartialWrite):  #pylint: disable-msg=R0901
    # R0901: Too many ancestors
    # This is a quite big partial class, therefore we ignore this warning
    """
    EBAS I/O XML object.
    This is a partial class distributed over many source files.
    """
