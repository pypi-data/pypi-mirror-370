"""
$Id: ndecimal.py 2557 2020-12-02 23:54:45Z pe $

nilutility.ndecimal private decimal type with changed format behaviour

Adaptation of the python decimal.Decimal class:
Issue: exponet __format__ only produces minimum 1 digit exponents, not minimum
       2 digits like float does:
       e.g.: "{:8.2E}".format(1.2) --> "1.20E+00"
             "{:8.2E}".format(Decimal(1.2)) --> " 1.20E+0"

basically, this whole module has only one reason:
apply the following patch to the python standard library decimal:

+++ decimal.py
+++ decimal.py
@@ -6119,7 +6119,7 @@
-        fracpart += "{0}{1:+}".format(echar, exp)
+        fracpart += "{0}{1:+03d}".format(echar, exp)
"""

import six

# Compatibility issues python 2 and 3
# Decimal data type:
#    In python3 there seems to be 2 modules: _decimal and _pydecimal
#    _decimal is a c implementation (accelerator module) which seems to be not
#    available on all platforms. _pydecimal is a pure python implementation.
#    Therefor the decimal wrapper module (called decimal) in python3 tries to
#    import _decimal, but falls back to _pydecimal if _decimal is not available.
#
#    In python2 there is only the (python implementaed) decimal module.
#
#    As we inherit from the Decimal class and make use of some module private
#    methods (_parse_format_specifier, _format_sign, _format_align,
#    _dec_from_triple, _insert_thousands_sep), we need to use the _pydecimal
#    implementation in python 3.
if six.PY2:
    import decimal
    # pylint: disable=E0611
    # E0611: No name '_xxx' in module 'decimal' (no-name-in-module)
    # --> disable for python3
    from decimal import getcontext, _parse_format_specifier, _format_sign, \
        _format_align, _dec_from_triple, _insert_thousands_sep, InvalidOperation
else:
    # pylint: disable=E0401
    # E0401: Unable to import '_pydecimal' (import-error)
    # --> disable for python2
    # Meta: there is something weired going on with the pylint directives
    # do not work on block level...
    import _pydecimal as decimal # pylint: disable=E0401
    # pylint: disable=E0401
    from _pydecimal import getcontext, _parse_format_specifier, _format_sign, \
        _format_align, _dec_from_triple, _insert_thousands_sep, InvalidOperation


class Decimal(decimal.Decimal):  # pylint: disable=R0904
    # R0904: Too many public methods (53/20)
    # -> problem inherited from decimal.Decimal
    """Floating point class for decimal arithmetic."""

    # this is exactly the same as in the original decimal.Decimal, but
    # _format_number is a different implementation
    def __format__(self, specifier, context=None, _localeconv=None):
        # pylint: disable=R0912
        # R0912: Too many branches
        # -> problem inherited from decimal.Decimal.__format__
        """Format a Decimal instance according to the given specifier.

        The specifier should be a standard format specifier, with the
        form described in PEP 3101.  Formatting types 'e', 'E', 'f',
        'F', 'g', 'G', 'n' and '%' are supported.  If the formatting
        type is omitted it defaults to 'g' or 'G', depending on the
        value of context.capitals.
        """

        # Note: PEP 3101 says that if the type is not present then
        # there should be at least one digit after the decimal point.
        # We take the liberty of ignoring this requirement for
        # Decimal---it's presumably there to make sure that
        # format(float, '') behaves similarly to str(float).
        if context is None:
            context = getcontext()

        spec = _parse_format_specifier(specifier, _localeconv=_localeconv)

        # special values don't care about the type or precision
        if self._is_special:
            sign = _format_sign(self._sign, spec)
            body = str(self.copy_abs())
            return _format_align(sign, body, spec)

        # a type of None defaults to 'g' or 'G', depending on context
        if spec['type'] is None:
            spec['type'] = ['g', 'G'][context.capitals]

        # if type is '%', adjust exponent of self accordingly
        if spec['type'] == '%':
            self = _dec_from_triple(self._sign, self._int, self._exp+2)

        # round if necessary, taking rounding mode from the context
        rounding = context.rounding
        precision = spec['precision']
        if precision is not None:
            if spec['type'] in 'eE':
                self = self._round(precision+1, rounding)
            elif spec['type'] in 'fF%':
                self = self._rescale(-precision, rounding)
            elif spec['type'] in 'gG' and len(self._int) > precision:
                self = self._round(precision, rounding)
        # special case: zeros with a positive exponent can't be
        # represented in fixed point; rescale them to 0e0.
        if not self and self._exp > 0 and spec['type'] in 'fF%':
            self = self._rescale(0, rounding)

        # figure out placement of the decimal point
        leftdigits = self._exp + len(self._int)
        if spec['type'] in 'eE':
            if not self and precision is not None:
                dotplace = 1 - precision
            else:
                dotplace = 1
        elif spec['type'] in 'fF%':
            dotplace = leftdigits
        elif spec['type'] in 'gG':
            if self._exp <= 0 and leftdigits > -6:
                dotplace = leftdigits
            else:
                dotplace = 1

        # find digits before and after decimal point, and get exponent
        if dotplace < 0:
            intpart = '0'
            fracpart = '0'*(-dotplace) + self._int
        elif dotplace > len(self._int):
            intpart = self._int + '0'*(dotplace-len(self._int))
            fracpart = ''
        else:
            intpart = self._int[:dotplace] or '0'
            fracpart = self._int[dotplace:]
        exp = leftdigits-dotplace

        # done with the decimal-specific stuff;  hand over the rest
        # of the formatting to the _format_number function
        return _format_number(self._sign, intpart, fracpart, exp, spec)

# this is mainly the same as decimal.___format_number, except the line:
# - fracpart += "{0}{1:+}".format(echar, exp)
# + fracpart += "{0}{1:+03d}".format(echar, exp)
def _format_number(is_negative, intpart, fracpart, exp, spec):
    """Format a number, given the following data:

    is_negative: true if the number is negative, else false
    intpart: string of digits that must appear before the decimal point
    fracpart: string of digits that must come after the point
    exp: exponent, as an integer
    spec: dictionary resulting from parsing the format specifier

    This function uses the information in spec to:
      insert separators (decimal separator and thousands separators)
      format the sign
      format the exponent
      add trailing '%' for the '%' type
      zero-pad if necessary
      fill and align if necessary
    """

    sign = _format_sign(is_negative, spec)

    if fracpart:
        fracpart = spec['decimal_point'] + fracpart

    if exp != 0 or spec['type'] in 'eE':
        echar = {'E': 'E', 'e': 'e', 'G': 'E', 'g': 'e'}[spec['type']]
        fracpart += "{0}{1:+03d}".format(echar, exp)
    if spec['type'] == '%':
        fracpart += '%'

    if spec['zeropad']:
        min_width = spec['minimumwidth'] - len(fracpart) - len(sign)
    else:
        min_width = 0
    intpart = _insert_thousands_sep(intpart, spec, min_width)

    return _format_align(sign, intpart+fracpart, spec)
