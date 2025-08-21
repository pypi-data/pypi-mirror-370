"""
$Id: file_helper.py 2614 2021-02-18 10:59:10Z pe $

Module for file io helper functions.
This module is just a helper for dealing with common file  i/o needs.
"""

import os
import re
import hashlib
import six

def tail(file_, nlines, expected_linelength=300):
    """
    Returns the last nline lines from a file.
    Parameters:
        file    opened file handle or file name including path
        nlines  number of lines that should be returned
        expected_linelength
                average expected length of lines for the last n lines
                with files that have very long lines (veeery long, say > 1000),
                this will help to speed up the reading
    Returns:
        The last nlines lines of the file (list of strings).
        Less then n lines, if there is not more in the file.
        The strings are raw data from the file, no decoding, no substitution
        of line end characters!
        AsciiRead.goto_line relies on this!
    Raises:
        IOError:  on various io problems
            file name does not exist, no access, ...)
    """
    if isinstance(file_, six.string_types):
        with open(file_, 'r') as file_:
            return tail(file_, nlines, expected_linelength=expected_linelength)
    if nlines < 0:
        raise ValueError('tail negative line numbers')
    if nlines == 0:
        return []
    # get the file size:
    file_.seek(0, os.SEEK_END)
    filesize = file_.tell()
    chunksize = min(expected_linelength * nlines, filesize)
    lastlines_pattern = r'[^\n\r]*\r?\n?'
    if not six.PY2:
        from io import BytesIO
        is_bin = False
        if isinstance(file_, BytesIO):
            is_bin = True
        else:
            try:
                is_bin = 'b' in file_.mode
            except AttributeError:
                pass
        if is_bin:
            lastlines_pattern = lastlines_pattern.encode('utf-8')
    while True:
        file_.seek(0, os.SEEK_END)
        file_.seek(file_.tell()-chunksize, os.SEEK_SET)
        buf = file_.read()
        lines = re.findall(lastlines_pattern, buf)[0:-1]  # last elem. '', skip
        # NO decoding, NO substitution of line ends: see docstring!
        if len(lines) > nlines:
            # we need nlines+1 to make sure the first line is complete
            # generate result:
            return lines[-nlines:]
        if chunksize == filesize:
            # fine, if we read already the whole file, return what's there
            return lines[-nlines:]
        else:
            # estimate a new buffer size
            if len(lines) <= 1:
                # not even one full line read: double the chunk
                chunksize *= 2
            else:
                # estiomate new size according to the fraction read already
                factor = float(nlines) / float(len(lines)-1)
                chunksize = int(chunksize * factor)
            if chunksize > filesize:
                chunksize = filesize

def md5(file_, chunksize=65536):
    """
    Generates and returns an md5 hash for a file.
    Parameters:
        file_       file object or file path
        chunksize   chunk size for file reading
    Returns:
        md5 hash of the file
    Raises:
       IOError
    """
    def _md5():
        """
        Generate the hash for a file object (opened file)
        Parameters:
            None
        Returns:
            md5 hash
        """
        md5_hash = hashlib.md5()
        for chunk in iter(lambda: file_.read(chunksize), b""):
            md5_hash.update(chunk)
        return md5_hash.hexdigest()

    if isinstance(file_, six.string_types):
        with open(file_, "rb") as file_:
            return _md5()
    else:
        return _md5()

def hardlinktree(src, dst):
    """
    Makes a copy of a directory tree, but hard links the files instead of
    copying.
    Similar to shutil.copytree, but hard links (in python3, there is a
    copy_function parameter, so this function mimics:
       shutil.copytree(src, dst, copy_function=os.link)
    in python3.
    """
    dst = os.path.abspath(dst)
    os.mkdir(dst)
    for root, dirs, files in os.walk(src, topdown=True):
        root = os.path.relpath(root, start=src)
        if root == '.':
            root = ''
        curdst = os.path.join(dst, root)
        for dir_ in dirs:
            os.mkdir(os.path.join(curdst, dir_))
        for file_ in files:
            fromfile = os.path.join(src, root, file_)
            tofile = os.path.join(curdst, file_)
            os.link(fromfile, tofile)

def get_main_path():
    """
    Get the path name of the main script running.
    """
    return os.path.abspath(__main__.__file__)
