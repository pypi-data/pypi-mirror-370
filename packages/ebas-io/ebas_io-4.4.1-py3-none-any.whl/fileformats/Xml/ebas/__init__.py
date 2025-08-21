"""
Xml/__init__.py
$Id: __init__.py 1198 2016-03-10 09:05:39Z pe $

XML module

History:
V.1.0.0  2013-04-15  pe  initial version

"""

from .base import XmlError
from .write import XmlWrite
from nilutility.datatypes import HexInt

class Xml(XmlWrite):
    """
    Partial class EbasXml: Put together the parts to the final class (only write, no read class).
    """
    pass