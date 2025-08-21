"""
$Id: list_helper.py 2227 2019-02-12 11:42:24Z pe $

Module for list helper functions.
This module is just a helper for dealing with common list manipulation tasks.
"""

def all_equal(iterable, ignore_none=True, single_value=False):
    """
    Highly efficient method for checking if all values are equal.
    (At least very fast if not all are equal)

    Parameters:
        iterable     iterable to be checked
        ignore_none  ignore None values (returns true if all non-None values are
                     equal)
        single_value if true, "all equal" is also triggered if there is just one
                     value (strict definition of "all")
    Returns:
        True if all the elements are equal to each other, else False
        Special cases:
            No values (length 0) return False
            Only None values and ignore_none=True returns True
            Only None values and ignore_none=False returns False
    """
    from itertools import groupby
    iterable = tuple(x for x in iterable if x is not None) if ignore_none \
        else iterable
    if not single_value and len(iterable) <= 1:
        # if single_value: "all equal" only if more then one value
        return False
    grp = groupby(iterable)
    return next(grp, False) and not next(grp, False)

def all_none(iterable):
    """
    Highly efficient method for checking if all values are None.
    (At least very fast if not all are None)

    Parameters:
        iterable     iterable to be checked
    Returns:
        True if all the elements are None, else False
        Special cases:
            No values (length 0) return False
    """
    from itertools import groupby
    grp = groupby(iterable)
    try:
        first = next(grp)
    except StopIteration:
        return False
    return first[0] is None and not next(grp, False)
