"""
nilutility/string_helper.py
$Id: string_helper.py 2454 2020-04-24 20:22:51Z pe $

Module for string helper functions.
This module is just a helper for dealing with common string manipulation tasks.
"""

import re
import csv
import six

class ListSplitterNewlineError(Exception):
    """
    Exception class for string parsing errors (list_splitter).
    """
    pass

class ListSplitterNullbyteError(Exception):
    """
    Exception class for string parsing errors (list_splitter).
    """
    pass

def _py2_unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    """
    The python2 csv module doesn't do Unicode; encode temporarily as UTF-8 and
    afterwards back to unicode.
    Parameters:
        unicode_csv_data   opened file or list of str
        dialect            csv dialect (see csv module)
        **kwargs           delimiter, skipinitialspace, ...
                           (see csv module)
    Returns:
        generator of lists (each list representing one line of csv)
    """
    csv_reader = csv.reader(_utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [cell.decode('utf-8') for cell in row]

def _utf_8_encoder(unicode_csv_data):
    """
    Helper for encoding unicode data to utf8.
    Parameters:
        unicode_csv_data    opened file or list of unicode strings
    Returns:
        utf-8 encoded text
    """
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def list_splitter(string, delimiter=' ', skipinitialspace=True):
    """
    Splits a string. Double quoted parts are untouched.
    Parameters:
        string        string to be splitted
        delimiter     splitting character
        skipinitialspace
                      spaces after delimiter are ignored
    Returns:
        [part,...] splitted parts as list
    Raises:
        ListSplitterNewlineError
            if newline inside string
        csv.Error
            all other (unexpected/unknown error conditions)
    Synopsis: see test cases
    """
    try:
        if six.PY2:
            return next(_py2_unicode_csv_reader(
                [string], delimiter=delimiter,
                skipinitialspace=skipinitialspace))
        else:
            csv_reader = csv.reader(
                [string], dialect=csv.excel, delimiter=delimiter,
                skipinitialspace=skipinitialspace)
            for row in csv_reader:
                return [cell for cell in row]
    except csv.Error as expt:
        # seems to be an old issue: "newline inside string" seems to be
        # not thrown anymore in recent versions of the csv module.
        # however on ratatoskr this is currently a problem 
        # (status 2016-12-06, ubuntu 12.04, python 2.7.3)
        # this is an issue, we catch the _csv.Error exception here,
        # throw a ListSplitterNewlineError which is cought in the ebas.io parser.
        # TODO: may be deleted in th future
        # e.g. ubuntu 16.04, python 2.7.11, this is not an issue
        #      MacOS, python.org 2.7.10 also no issue
        if str(expt) == 'newline inside string':
            raise ListSplitterNewlineError(str(expt))
        if str(expt) == 'line contains NULL byte':
            raise ListSplitterNullbyteError(str(expt))
        raise expt

def list_joiner(lst, delimiter=' ', insert_space=False):
    """
    Joins a list to a string. If the delimiter occurs in an element of the
    list or any element has leading or trailing whitespaces, this element
    is escaped (double quoted).
    Parameters:
        lst       list to be joined
        delimiter delimiter character
    Returns:
        string
    Synopsis: see test cases
    """
    # make a copy of the list and
    # - substitute list elements None by empty string
    # - wrap elements containing a comma in double quotes
    lst = ['' if elem is None
           else '"' + re.sub('"', '""', elem) +'"' \
               if re.search(delimiter, elem) or re.search('"', elem)
           else elem
           for elem in lst]
    if insert_space:
        delimiter += ' '
    return delimiter.join(lst)

