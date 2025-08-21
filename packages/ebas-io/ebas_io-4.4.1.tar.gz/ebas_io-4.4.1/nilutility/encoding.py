"""
nilutility/encoding.py
$Id: encoding.py 2464 2020-07-07 14:05:22Z pe $

Module for setting the default encoding.
"""

import sys
from six.moves import reload_module

def fix_io_encoding(default='UTF-8'):
    """
    Sets the default encloding (for files, stdin/out/err if redirected etc)
    Generally:
        Is set to ascii if the environment variable PYTHONIOENCODING is not set
        else, it was set to PYTHONIOENCODING.
        For cases where PYTHONIOENCODING was not set, we can set the default
        encoding to utf-8 here.
    """
    if sys.getdefaultencoding() in (None, 'ascii'):
        # six.moves.reload_module is builtin in python2, importlib.reload in
        # python3
        reload_module(sys)
        sys.setdefaultencoding(default) # @UndefinedVariable pylint: disable=E1101
        # @UndefinedVariable: make pydev shut up
        # E1101: Module 'sys' has no 'setdefaultencoding' member
