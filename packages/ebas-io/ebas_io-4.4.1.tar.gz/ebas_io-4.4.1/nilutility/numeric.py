"""
nilutility/numeric.py
$Id: numeric.py 2686 2021-08-18 11:24:59Z pe $

This module collects numerical helper functions that apply to differnt numeric
datatypes (float, Decimal, int, HexInt...), and can not be added to one specific
_helper module (e.g. float_helper).
"""

import re
import math
import string
from nilutility.ndecimal import Decimal
from nilutility.datatypes import HexInt

def frexp10(value):
    """
    Finds the mantissa m and exponent e of a number x such that x = m 10^e
    Parameters:
        value   value to be analyzed
    Returns:
        (mant, expon)
    """
    expon = int(math.floor(math.log10(abs(value))))
    mant = value/math.pow(10, expon)
    return (mant, expon)

def digits(value):
    """
    Returns the minimum and maximum digit used in a float, decimal or HexInt
    value.
    Parameters:
        value   float, Decimal or HexInt value (None allowed)
    Returns:
        digits tulple (mindig, maxdig)
        returns (None, None) if a None value is passed
        returns (0, 0) in case of 0.0

        Be aware that the number of digits are numbered starting from
        1/-1 left/right of the comma! This means that 0 is is not a valid digit.
        This also implies that the digit number (before comma) is not equal to
        the exponent of 10 of the respective digit.

        Digit 0 is only used if the number needs no digits at all (only 0.0)
        Digit None is used for None values.
    Raises:
        ValueError if the string representation does not fit to
                   float/Decimal behaviour.
        TypeError  if the type is not float, Decimal or HexInt
                   The TypeError will have an additional new_type arttribute
    """
    maxdig = None
    mindig = None
    if value is None:
        return (None, None)
    elif isinstance(value, HexInt):
        return _digits_hexint(value)
    elif isinstance(value, float):
        # special case, float is printed in full precision using repr
        # str shortens the output string in some cases.
        # However, repr cannot be used for other types - Decimal in
        # this case
        valstr = repr(value)
    elif isinstance(value, (Decimal, int)):
        valstr = str(value)
    else:
        err = TypeError('unsupported type')
        err.new_type = type(value)
        raise err
    reg = re.match(\
        r"^-?([0-9]*)(\.([0-9]*?[1-9]?)0*)?([Ee]([\+-][0-9]*))?$",
        valstr)
    if not reg:
        raise ValueError('illegal value: ' + valstr)
    vk_ = len(reg.group(1)) if reg.group(1) != None and \
                               reg.group(1) != '0' else 0
    nk_ = len(reg.group(3)) if reg.group(3) != None and \
                               reg.group(3) != '0' else 0
    if vk_ == 0 and nk_ == 0:
        # this meand value is 0.0
        return (0, 0)
    exp = int(reg.group(5)) if reg.group(5) != None else 0
    if nk_ == 0:
        # special case: if no digits after comma and some 0 before comma:
        reg2 = re.search('(0*)$', reg.group(1))
        mindig = exp + len(reg2.group(1)) + 1
        # reg.group(1)==None cannot happen (only if val was 0.0; caught before)
        if mindig <= 0:
            # correct mindig if calculated w/o nk_ but with a negative exponent
            mindig -= 1
    else:
        mindig = exp - nk_
        if nk_ and mindig >= 0:
            # zero is no digit number. If crossing zero, we nedd to add one
            mindig += 1
    if vk_ == 0:
        # special case: if no digits before comma
        reg2 = re.search('^(0*)', reg.group(3))
        maxdig = exp - len(reg2.group(1)) - 1
        # reg.group(3)==None cannot happen (only if val was 0.0; caught before)
    else:
        maxdig = exp + vk_
        if vk_ and maxdig <= 0:
            # zero is no digit number. If crossing zero, we nedd to subtract one
            maxdig -= 1
    return (mindig, maxdig)

def digits_stat(valuelist):
    """
    Calculates statistics about the values in a list of numeric values.
    digist_stat is designed and tested for float or Decimal values.
    Calculates minimum value, maximum value, minimum digit, maximum digit,
    maximum precision used.
    Parameters:
        valuelist  list of float or Decimal values (None allowed)
    Returns:
        statistics tulple (minval, maxval, mindig, maxdig, maxprec)
        (None, None, None, None, 0) if ONLY None values occurred (no data)
        (0.0, 0.0, 0, 0, 0) if 0.0 were the ONLY valid values
        (HexInt(0), HexInt(0), 0, 0, 0) if 0x0 were the ONLY valid values
    Raises:
        ValueError if the string representation does not fit to
                   float/Decimal behaviour.
        TypeError  if the type is not float or Decimal or HexInt
    """
    valuelist = [d for d in valuelist if d is not None]
    if not valuelist:
        return (None, None, None, None, 0)
    if isinstance(valuelist[0], HexInt):
        return _digits_stat_hexint(valuelist)
    t_maxdig = None
    t_mindig = None
    t_maxprec = 0
    t_minval = None
    t_maxval = None
    for val in valuelist:
        (mindig, maxdig) = digits(val)
        prec = maxdig - mindig
        if (mindig < 0 and maxdig < 0) or \
           (mindig > 0 and maxdig > 0):
            # e.g. 123., 1012   => mindig=1, maxdig=4, 4-1 = 3 (wrong)
            # but  123., 1012.1 => mindig=-1, maxdig=4, 4-(-1) = 5 (correct),
            # (it's all because we do NOT use a digit number 0)
            prec += 1
        t_maxprec = max(t_maxprec, prec)
        if t_mindig is None or t_mindig == 0:
            t_mindig = mindig
        elif mindig != 0:
            t_mindig = min(t_mindig, mindig)
        if t_maxdig is None or t_maxdig == 0:
            t_maxdig = maxdig
        elif maxdig != 0:
            t_maxdig = max(t_maxdig, maxdig)
        t_minval = val if t_minval is None else min(t_minval, val)
        t_maxval = val if t_maxval is None else max(t_maxval, val)
    return (t_minval, t_maxval, t_mindig, t_maxdig, t_maxprec)

def int2base(i, base, alphabet=string.digits+string.ascii_letters):
    """
    Convert an integer 'i' to a string representation in the number system of
    the base 'base'.
    Parameters:
        i         integer to be converted
        base      target number system
        alphabet  digit characters to be used
    Returns
        number as string the base system
    """
    if base > len(alphabet):
        raise ValueError(
            'not enough alphabet chars defined for number system {}'.format(
                base))
    if i < 0:
        sign = -1
    elif i == 0:
        return alphabet[0]
    else:
        sign = 1

    i *= sign
    digits = []

    while i:
        digits.append(alphabet[int(i % base)])
        i = int(i / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)

def _digits_hexint(value):
    """
    Returns the minimum and maximum digit used in a HexInt value.
    digits is designed and tested for float or Decimal values.
    Parameters:
        value   HexInt value (None is not allowed)
    Returns:
        digits tulple (mindig, maxdig)
        returns (0, 0) in case of 0x0

        Be aware that the number of digits are numbered starting from
        1/-1 left/right of the comma! This means that 0 is is not a valid digit.
        This also implies that the digit number (before comma) is not equal to
        the exponent of 16 of the respective digit.

        Digit 0 is only used if the number needs no digits at all (only 0.0)
    Raises:
        TypeError  if the type is not HexInt
                   The TypeError will have an additional new_type arttribute
    """
    if not isinstance(value, HexInt):
        err = TypeError('unsupported type')
        err.new_type = type(value)
        raise err
    if value == 0:
        return(0, 0)
    valstr = str(value)[2:]  # string representation without leading '0x'
    maxdig = len(valstr)
    mindig = len(valstr) - len(valstr.rstrip('0')) + 1
    return (mindig, maxdig)

def _digits_stat_hexint(valuelist):
    """
    For HexInt variables:
    Calculates statistics about the numerics of on variable (minimum digit,
    maximum digit, maximum precision used).
    Parameters:
        valuelist   list of values (all HexInt), no None values
    Returns:
        statistics tulple (minval, maxval, mindig, maxdig, maxprec)
        (HexInt(0), HexInt(0), 0, 0, 0) if 0x0 were the ONLY valid values
    Raises:
        TypeError if a non HexInt value is found in the variable.
    """
    t_maxdig = None
    t_mindig = None
    t_maxprec = 0
    t_minval = None
    t_maxval = None
    for val in valuelist:
        if not isinstance(val, HexInt):
            raise TypeError('non hex value in HexInt valuelist')
        # mindig is always 1 if there is at least one valid value != 0
        # if only 0x0, mindig is 0
        (mindig, maxdig) = _digits_hexint(val)
        t_mindig = max(t_mindig, mindig) if t_mindig is not None else mindig
        t_maxdig = max(t_maxdig, maxdig) if t_maxdig is not None else maxdig
        prec = 0 if val == 0 else maxdig-mindig+1
        t_maxprec = max(t_maxprec, prec)
        t_minval = min(t_minval, val) if t_minval is not None else val
        t_maxval = max(t_maxval, val) if t_maxval is not None else val
    return (t_minval, t_maxval, t_mindig, t_maxdig, t_maxprec)
