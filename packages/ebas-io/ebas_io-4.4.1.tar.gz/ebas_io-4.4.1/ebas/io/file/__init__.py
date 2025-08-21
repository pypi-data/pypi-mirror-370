"""
EBAS I/O file module
"""
from six import string_types
from collections import OrderedDict
from .base import FLAGS_ONE_OR_ALL, FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE, \
    FLAGS_AS_IS, \
    EBAS_IOFORMAT_NASA_AMES, EBAS_IOFORMAT_CSV, EBAS_IOFORMAT_XML, \
    EBAS_IOFORMAT_NETCDF1, EBAS_IOFORMAT_NETCDF, EBAS_IOFORMAT_OPENDAP, \
    EBAS_IOSTYLE_SINGLECOLUMN, EBAS_IOSTYLE_MULTICOLUMN, \
    EBAS_IOSTYLE_MULTICOLUMN_PRECIP, EBAS_IOSTYLE_KEEP, \
    EBAS_IOMETADATA_OPTION_SETKEY, EBAS_IOMETADATA_OPTION_ALL, \
    SUPPRESS_SORT_VARIABLES, SUPPRESS_METADATA_OCCURRENCE

class BaseEbasIOOption(int):
    """
    Base class for options (commandline):
    """
    options = None
    roptions = None

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], string_types):
            try:
                obj = int.__new__(cls, cls.options[args[0]])
            except KeyError:
                raise ValueError("invalid literal for {}: '{}'".format(
                    cls.__name__, args[0]))
        else:
            obj = int.__new__(cls, *args)
        return obj
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.__class__.roptions[self])
    def __str__(self):
        return '{}'.format(self.__class__.roptions[self])

    @classmethod
    def legal_options(cls):
        """
        Returns a list of option names.
        """
        return [cls(x) for x in cls.options.keys()]


class EbasIOFlagOption(BaseEbasIOOption):
    """
    Flag options for NILU Nasa Ames files:
    """
    options = OrderedDict([
        ('one-or-all', FLAGS_ONE_OR_ALL),
        ('compress', FLAGS_COMPRESS),
        ('all', FLAGS_ALL),
        ('none', FLAGS_NONE),
    ])
    roptions = OrderedDict([(x[1], x[0]) for x in options.items()])

class EbasIOFormatOption(BaseEbasIOOption):
    """
    Format options for EBAS files:
    """
    options = OrderedDict([
        ('NasaAmes', EBAS_IOFORMAT_NASA_AMES),
        ('CSV', EBAS_IOFORMAT_CSV),
        ('XML', EBAS_IOFORMAT_XML),
        ('NetCDF1', EBAS_IOFORMAT_NETCDF1),
        ('NetCDF', EBAS_IOFORMAT_NETCDF),
        ('OPeNDAP', EBAS_IOFORMAT_OPENDAP),
    ])
    roptions = OrderedDict([(x[1], x[0]) for x in options.items()])
