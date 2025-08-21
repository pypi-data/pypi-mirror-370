"""
five: extensions to six module
pyhon 2+3=five
"""

import six

def raise_from(exc_value, exc_value_from):
    """
    Raise an exception from a context.
    Python 3 is handled well by six, python2 needs improvement.
    Parameters:
        exc_value       exception value for the exception to rise
        exc_value_from  causing exception, print context for this one
    Returns:
        None
    """

    if six.PY2:
        import traceback
        import sys
        traceback.print_exception(*sys.exc_info())
        sys.stderr.write(
            "\nThe above exception was the direct cause of the following "
            "exception:\n\n")
        raise exc_value
    six.raise_from(exc_value, exc_value_from)

