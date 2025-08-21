"""
Fallback class to be used when ebas.domain is not available (e.g. EbasIO Module
published for 3rd parties).

$Id: from_domain.py 1527 2017-02-15 18:36:36Z pe $
"""

from .base import EbasFileBase
class EbasFileFromDomain(EbasFileBase):
    """
    Fallback class to be used when ebas.domain is not available (e.g. EbasIO
    Module published for 3rd parties).
    """
    pass
