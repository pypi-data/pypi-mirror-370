"""
Ebas IO base classes

$Id: base.py 1528 2017-02-15 18:45:40Z pe $
"""

class EbasIOError(Exception):
    """Error base class for EBAS IO."""
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg
    def __str__(self):
        return self.msg