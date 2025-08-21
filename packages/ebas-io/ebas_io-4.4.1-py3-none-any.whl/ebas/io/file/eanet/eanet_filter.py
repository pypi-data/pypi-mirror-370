"""
$Id: eanet_filter.py 2749 2021-11-25 00:34:17Z pe $

Basic EANET Filter functionality is implemented in the EanetFilter class in
fileformats/EANET.
The ebas/io/eanet_filter (this) module is about mapping the EANET files to the
ebas IO data model.
"""

from .read_filter import EanetFilterPartialRead

class EbasEanetFilter(EanetFilterPartialRead):
    """
    EANET Filter I/O object.
    """

