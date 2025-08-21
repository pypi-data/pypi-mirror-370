"""
nilutility/float_helper.py
$Id: float_helper.py 1167 2016-01-19 09:57:07Z pe $

Module for float helper functions.
This module is just a helper for dealing with common float manipulation tasks.
"""

import sys
import math

def float_almostequal(flt1, flt2):
    """
    Compares float values and allow epsilon for representation errors.
    Epsilon does not cover computation and rounding errors that might have
    influenced either of the two values before.
    Parameters:
        flt1, flt2    float values
    Returns:
        True if nearly equal, else False
    """
    if flt1 == flt2:
        return True

    # get binary exponent of the floats to compare
    # IEEE 754: e.g. 1.0dec --> 0.1bin ** 2^1
    exp = math.frexp(flt1)[1]
    if exp != math.frexp(flt2)[1]:
        # the two floats differ if have different exponent
        return False

    # this is the IEEE 754 machine epsilon for binary exponent == 1
    # i.e. the value that increases the rightmost digit in the (binary) mantissa
    eps = sys.float_info.epsilon
    # now multiply with binary exponent of the target
    # machine eps is given for exponent == 1, so multiplying with exp gives a
    # variation in the second bit from right in the mantissa. this is wanted.
    eps *= math.pow(2, exp)
    # now, eps == number that would just increases the 2nd rightmost digit of
    # the mantissa in flt1 and flt2

    if abs(flt1 - flt2) < eps:
        return True
    return False
