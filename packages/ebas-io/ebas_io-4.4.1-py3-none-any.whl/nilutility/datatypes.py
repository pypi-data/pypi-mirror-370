"""
nilu/datatypes.py
$Id: datatypes.py 2613 2021-02-18 10:58:49Z pe $

Module for generic datatypes.

History:
V.1.0.0  2012-10-05  pe  initial version

"""

import datetime
import six

class DataObject(dict):
    """
    Basic Object used for data dictionaries.
    This can be used as dictionary or in class attribute notation:

    # CREATION:
    dat=DataDictObj(bla=2, wtf=3)
    # same as:
    dat=DataDictObj({'bla'=2, 'wtf': 3})
    # same as:
    dat = DataDictObj([('bla', 2), ('wtf', 3)])

    # USAGE:
    dat.bla
    # same as:
    dat['bla']

    # SETTING:
    dat.bla = 2
    # same as:
    dat['bla'] = 2

    # EXCEPTIONS:
    dat.x
     --> AttributeError
    dat['x']
     --> KeyError
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as expt:
            raise AttributeError(str(expt))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError as expt:
            raise AttributeError(expt)

    def copy(self):
        return DataObject(self)

def recursive_data_object(*args, **kwargs):
    """
    Factory for buildinfg a recursive DataObject instance.
    Every "child" which is a dict will become a DataObject (subclass of dict).
    Parameters:
        passed on to the dict instanciation
    Returns:
        DataObject
    """
    def _recurse(elem):
        """
        Recurse into other structures (dict, list, set, tuple)
        """
        if type(elem) == dict:
            # use type: we only convert "plain" dicts, not subclasses!
            return recursive_data_object(elem)
        elif isinstance(elem, dict):
            for key in elem.keys():
                elem[key] = _recurse(elem[key])
        if isinstance(elem, list):
            for i in range(len(elem)):
                elem[i] = _recurse(elem[i])
            return elem
        if isinstance(elem, set):
            ret = type(elem)()
            for member in elem:
                ret.add(_recurse(member))
            if ret == elem:
                return(elem)
            return(ret)
        if isinstance(elem, tuple):
            ret = []
            for member in elem:
                ret.append(_recurse(member))
            ret = type(elem)(ret)
            if ret == elem:
                return(elem)
            return(ret)
        return(elem)

    ret = DataObject(*args, **kwargs)
    for key in ret.keys():
        ret[key] = _recurse(ret[key])
    return ret

class Histogram(dict):
    """
    Class for creating histograms, based on dict.
    SYNOPSIS:
        # generate
        hist = Histogram()
        # collect:
        hist.increment('a')
        hist.increment('b')
        hist.increment('c')
        hist.increment('b')
        hist.increment('b')
        # results:
        res = hist.get_max()
        # res == (3, ['b'])
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.unhashables = []

    def increment(self, value, inc=1):
        """
        Increments the histogram value.
        Parameters:
            value    histogram value
            inc      increment by (number)
        Returns:
            None
        """
        try:
            if not value in list(self.keys()):
                self[value] = inc
            else:
                self[value] += inc
        except TypeError:
            # if value is unhashable, use workaround
            for k in self.unhashables:
                if k[0] == value:
                    k[1] += 1
                    break
            else:
                self.unhashables.append([value, 1])

    def get_max(self):
        """
        Finds the maximum occorence.
        Parameters:
            None
        Returns:
            (maxocc, [keys])
        """
        if len(self) + len(self.unhashables) == 0:
            return (0, [])
        maxocc = max([self[x] for x in list(self.keys())] +\
                     [k[1] for k in self.unhashables])
        return (maxocc, [k for k in list(self.keys()) if self[k] == maxocc] +\
                        [k[0] for k in self.unhashables if k[1] == maxocc])


# Class HexInt

def returnthisclassfrom(methods, otype):
    """
    Decorator function for making certain methods of a class return an instance
    of the class itself instead of another type (all methods in list returning
    otype will return class instances).
    This works only if class can be instancianated from otype.
    """
    def gen_wrapper(cls, method):
        """
        Generate the customized wrapper function according to desired return
        type and method to be called.
        """
        def wrapper(*args, **kwargs):
            """
            Customized wrapper function for the original method.
            Will be created according to cls and method parameters of
            gen_wrapper.
            """
            res = method(*args, **kwargs)
            if isinstance(res, otype):
                return cls(res)
            return res
        return wrapper
    def wrap_methods(cls):
        """
        Wrap all relevant methods in the customized wrapper function.
        """
        for met in methods:
            method = getattr(cls, met)
            setattr(cls, met, gen_wrapper(cls, method))
        return cls
    return wrap_methods

# Compatibility issues python 2 and 3:
# __div__ is only implemented in python2. The python3 __truediff__ should
# of course _not_ be in the list.
if six.PY2:
    return_this_class_methods = (
        '__abs__', '__add__', '__and__', '__div__', '__floordiv__',
        '__invert__', '__lshift__', '__mod__', '__mul__', '__neg__', '__or__',
        '__pow__', '__rshift__', '__sub__', '__trunc__', '__xor__')
else:
    return_this_class_methods = (
        '__abs__', '__add__', '__and__', '__floordiv__',
        '__invert__', '__lshift__', '__mod__', '__mul__', '__neg__', '__or__',
        '__pow__', '__rshift__', '__sub__', '__trunc__', '__xor__')
@returnthisclassfrom(return_this_class_methods, int)
class HexInt(int):
    """
    Class for representing a hex integer value.
    Modifications from int:
        - interpret  initialization string as hex if it is a string
        - modify most special methods to return HexInt objects instead of int
        - repr and str return hex strings
    Synopsis:
        Initialization:
            HexInt(0xa), HexInt('a'), HexInt('0xa'), HexInt(10), HexInt(012)
            all do the same thing:
            (HexInt(0xa), HexInt(0xa), HexInt(0xa), HexInt(0xa), HexInt(0xa))

        repr(HexInt(0xa)) => 'HexInt(0xa)'

        str(HexInt(0xa)) => '0xa'

        HexInt(0xf) + 2 => HexInt(0x11) but 2 + HexInt(0xf) => 17 and
            HexInt(0xf) + 2.1 => 17.1

        HexInt(0xf) / 2 => HexInt(0x7) but 15 / HexInt(2) => 7 and
            HexInt(0xf) / 2.1 => 7.142857142857142

        HexInt(0xf) % 2 => HexInt(0x1) but 15 % HexInt(2) => 1 and
            HexInt(0xf) % 2.0 => 1.0

        divmod(HexInt(0xf),2) =>(HexInt(0x7), HexInt(0x1)) but
            divmod(15, HexInt(2)) => (7, 1) and
            divmod(HexInt(0xf), 2.0) => (7.0, 1.0)
    """
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], six.string_types):
            obj = int.__new__(cls, args[0], 16)
        else:
            obj = int.__new__(cls, *args)
        return obj
    def __repr__(self):
        return 'HexInt({:#x})'.format(self)
    def __str__(self):
        return '{:#x}'.format(self)
    def __divmod__(self, other):
        return tuple(HexInt(x) if isinstance(x, int) else x
                     for x in divmod(int(self), other))

class datetimeprec(datetime.datetime): # pylint: disable=C0103
    # C0103: Invalid name (should match [A-Z_][a-zA-Z0-9]
    #   -> The original class was called datetime. A similar name is wanted.
    """
    Enhanced dateime.datetime class.
    + Adds one attribute for defining a precision with which the object was
    created. This attribute can either be specified explicitly on creation as
    a keyword argument, or will be set implicitly according to other parameters
    passed.
    + Allows creation of datetime object with year only or year and month only.
    """
    def __new__(cls, *args, **kwargs):
        """
        datetiome.datetime is immutable, so we must override __new__()
        """
        prec = None
        if 'prec' in kwargs:
            prec = kwargs['prec']
            cls.checkprec(prec)
            del kwargs['prec']
        if prec is None:
            if len(args) >= 7 or 'microsecond' in kwargs:
                prec = 'f'
            elif len(args) == 6 or 'second' in kwargs:
                prec = 'S'
            elif len(args) == 5 or 'minute' in kwargs:
                prec = 'M'
            elif len(args) == 4 or 'hour' in kwargs:
                prec = 'H'
            elif len(args) == 3 or 'day' in kwargs:
                prec = 'd'
            elif len(args) == 2 or 'month' in kwargs:
                prec = 'm'
            else:
                prec = 'Y'
        if len(args) < 2 and \
           [tag for tag in ['microsecond', 'second', 'minute', 'hour',
                            'day', 'month'] if tag in kwargs] == []:
            kwargs['month'] = 1
        if len(args) < 3 and \
           [tag for tag in ['microsecond', 'second', 'minute', 'hour',
                            'day'] if tag in kwargs] == []:
            kwargs['day'] = 1
        ret = datetime.datetime.__new__(cls, *args, **kwargs)
        ret.prec = prec
        return ret

    def __repr__(self):
        """
        Representation of a datetimeprec object.
        Parameters:
            None
        Returns:
            repr string
        """
        return "datetimeprec: " + self.strftime("%Y-%m-%dT%H:%M:%S.%f") + \
               ", prec=" + self.prec

    @staticmethod
    def checkprec(prec):
        """
        Checks the precision string for validity
        Parameters:
            prec   precision string
        """
        if not isinstance(prec, six.string_types):
            raise TypeError(
                "prec: string expected, not {}".format(prec.__class__.__name__))
        if prec not in ('Y', 'm', 'd', 'H', 'M', 'S', 'f'):
            raise ValueError("illigal precission string '{}'".format(prec))

    @classmethod
    def fromdatetime(cls, dto, prec):
        """
        Creates a datetimeprec object from a datetime.datetime object.
        Precision must be set, the original precision cannot be guessed from
        the datetime object.
        Parameters:
            dto     datetime.datetime object
            prec    precision
        """
        kwargs = {}
        cls.checkprec(prec)
        if prec in ('Y', 'm', 'd', 'H', 'M', 'S', 'f'):
            kwargs['year'] = dto.year
        if prec in ('m', 'd', 'H', 'M', 'S', 'f'):
            kwargs['month'] = dto.month
        if prec in ('d', 'H', 'M', 'S', 'f'):
            kwargs['day'] = dto.day
        if prec in ('H', 'M', 'S', 'f'):
            kwargs['hour'] = dto.hour
        if prec in ('M', 'S', 'f'):
            kwargs['minute'] = dto.minute
        if prec in ('S', 'f'):
            kwargs['second'] = dto.second
        if prec in ('f',):
            kwargs['microsecond'] = dto.microsecond
        kwargs['tzinfo'] = dto.tzinfo
        kwargs['prec'] = prec
        return cls.__new__(cls, **kwargs)

    def todatetime(self):
        """
        Converts into a normat datetime.
        Returns:
            datetime
        """
        return datetime.datetime(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second, self.microsecond,
            tzinfo=self.tzinfo)

class ControlledDictList(list):
    """
    A versatile list of controlled dictionaries.
    Each element is a dict. The allowed keys of the dictionaries as well as the
    values for certain keys can be limited. elements can be added either as dict
    or as tuple/list.
    """
    def __init__(self, *args, **kwargs):
        """
        Set up the list. The allowed keys for the dictionaries is limited, the
        allowed values for each key can be limited.
        Parameters:
            keys       key names used for the elements of each dict (mandatory)
            <key-name> list of allowed values for the key
        Returns:
            none
        """
        self.allowed = {}
        if 'keys' in kwargs:
            self.keys = kwargs['keys']
            del kwargs['keys']
        else:
            raise ValueError('no keys defined')
        for key in self.keys:
            if key in kwargs:
                # allowed values for key:
                self.allowed[key] = kwargs[key]
                del kwargs[key]
        if kwargs:
            raise ValueError('unexpected keys: {}'.format(
                ', '.join(list(kwargs.keys()))))
        super(ControlledDictList, self).__init__(*args, **kwargs)

    def add(self, *args, **kwargs):
        """
        Adds one element (dict) to the list.
        Parameters:
            all keys defined by __init__
            or a list/tuple containing as many elements as self.keys
        """
        if args and kwargs:
            raise RuntimeError('either args or kwargs allowed, no mix')
        if args:
            if len(args) != len(self.keys):
                raise RuntimeError('number of args does not match number of '
                                   'keys')
            self.append({key: args[i] for i, key in enumerate(self.keys)})
        else:
            self.append(kwargs)

    def append(self, element):
        """
        Override append method. Additionally check for ControlledDictList logic.
        Parameters:
            element    element to append
        """
        # must be dict
        if not isinstance(element, dict):
            raise TypeError('only dict allowed')

        # only keys defined in self.keys are valid; all are mandatory
        err = [x for x in self.keys if x not in element]
        if err:
            raise RuntimeError("Missing keys: {}".format(', '.join(err)))
        err = [x for x in list(element.keys()) if x not in self.keys]
        if err:
            raise RuntimeError("Extra keys: {}".format(', '.join(err)))

        # check allowed values for certain keys
        for key in self.allowed:
            if element[key] not in self.allowed[key]:
                raise ValueError("'{}' is not allowed for key '{}'".format(
                    element[key], key))
        super(ControlledDictList, self).append(element)

    def insert(self, pos, element):
        """
        Override insert method. Additionally check for ControlledDictList logic.
        Parameters:
            pos        position to insert at
            element    element to insert
        """
        # must be dict
        if not isinstance(element, dict):
            raise TypeError('only dict allowed')

        # only keys defined in self.keys are valid; all are mandatory
        err = [x for x in self.keys if x not in element]
        if err:
            raise RuntimeError("Missing keys: {}".format(', '.join(err)))
        err = [x for x in list(element.keys()) if x not in self.keys]
        if err:
            raise RuntimeError("Extra keys: {}".format(', '.join(err)))

        # check allowed values for certain keys
        for key in self.allowed:
            if element[key] not in self.allowed[key]:
                raise ValueError("'{}' is not allowed for key '{}'".format(
                    element[key], key))
        super(ControlledDictList, self).insert(pos, element)

    def _check_compatibility(self, other):
        """
        Check compatibility of lists in order to add to one another.
        """
        if type(self) != type(other):  # pylint: disable=C0123
            # C0123: Using type() instead of isinstance() for a typecheck.
            # --> this type comparison cannot be substituted by isinstance
            raise TypeError(
                "Only a list of the same type can be added to a {}, not {}"
                .format(self.__class__.__name__, other.__class__.__name__))
        if self.keys != other.keys or self.allowed != other.allowed:
            raise TypeError("{} to add must have the same "
                            "configuration".format(self.__class__.__name__))

    def __add__(self, other):
        """
        Overrides the __add__ method. Check configuration and return a
        EbasDomainIssueList.
        Parameters:
            other    the other list to add
        """
        self._check_compatibility(other)
        return type(self)(list.__add__(self, other))

    def __iadd__(self, other):
        """
        Override the __iadd__ method. Check configuration.
        Parameters:
            other    the other list to iadd
        """
        self._check_compatibility(other)
        super(ControlledDictList, self).__iadd__(other)
        return self
