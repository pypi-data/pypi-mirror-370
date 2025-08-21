"""
ebas/nasa_ames/parse_base.py
$Id: parse_base.py 1527 2017-02-15 18:36:36Z pe $

base class for parser for file input functionality for EBAS NASA Ames module

History:
V.1.0.0  2013-06-22  pe  initial version

"""
from ..base import EbasNasaAmesBase

class NasaAmesPartialReadParserBase(# pylint: disable=R0901, W0223,
        EbasNasaAmesBase):
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    # W0223: ... is abstract in base class but is not overridden
    # this class is abstract as well (does not have any NotImplementedError)
    # R0903: Too few public methods
    #     This is a base class.
    """
    Base class for Parser object.
    """
    pass
