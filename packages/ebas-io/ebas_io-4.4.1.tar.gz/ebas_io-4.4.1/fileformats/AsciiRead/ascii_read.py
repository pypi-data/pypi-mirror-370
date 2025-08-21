"""
Basic file IO for ASCII datafiles. Mainly encoding and special character issues.
"""

import logging
import os
from six import string_types, PY2
from nilutility.file_helper import tail


class AsciiReadError(Exception):
    """
    Error class for NasaAmes 1001.
    """
    pass

class BackposError(Exception):
    """
    Exception class when backwards positioning in file was not allowed.
    """
    pass

class AsciiRead(object):
    # pylint: disable=R0902
    # R0902: Too many instance attributes
    """
    Basic file IO for ASCII datafiles. Mainly encoding and special character
    issues.
    The instances of this class are a context managers, so they can be used in
    a "with" block.
    """

    def __init__(
            self, filespec,
            encodings=('ascii', 'utf-8', 'utf-16', 'utf-32'),
            fallback_encoding='iso8859-15', strict_enc=True,
            ignore_bom=1, cvt_nbsp=False, strip=False, tabsize=None,
            error_callback=None, warning_callback=None):
        # pylint: disable=R0913
        # R0913: Too many arguments
        """
        Set up IO object.
        Opens the underlying file right away, this way callers can easier catch
        an IOError if a "with" block schould be used.
        Example:
        try:
           fil = AsciiRead(filename)
        except IOEror:
           ...
        with fil:
           ...

        Parameters:
            filespec    either a path and filename or a stream like object
            encodings   list of non-ambiguous encodings to try
            fallback_encoding
                        a fallback 8 bit encoding, this is ambiguous and
                        might be correct or not
            strict_enc  be strict about encodings (do not allow changes through
                        the file)
            ignore_bom  ignore (take out) BOM character in utf- encoded files
                        possible values:
                        1   take out as first character in file
                        2   take out as any character in file
            cvt_nbsp    convert non breaking space characters to normal space
                        1 convert, but raise warning only first time
                        2 convert, warn each time
                        3 convert, no warning
            strip       strip leading and trailing white spaces (and \n)
            tabsize     convert tab to newlines, use tabsize
                        None = no tab conversion
                        If tabsize is negative use fixed number of blanks for
                        each tab instead og expandtabs.
            error_callback
                        Callback method in case of error. See method error.
            warning_callback
                        Callback method in case of warning. See method warning.
            None
        Returns:
            None
        Raises:
            None
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.filespec = filespec
        self.filename = None
        self.file = None
        self.lnum = 0
        self.encodings = encodings
        self.fallback_encoding = fallback_encoding
        self.encoding = None
        self.enc_line = None
        self.strict_enc = strict_enc
        self.ignore_bom = ignore_bom
        self.cvt_nbsp = cvt_nbsp
        self.strip = strip
        self.tabsize = tabsize
        self.error_callback = error_callback
        self.warning_callback = warning_callback
        # Open the file right away. See docstring for explanation
        self.open()

    def __enter__(self):
        """
        Context manager enter method.
        Parameters:
            None
        Returns:
            self as context manager object
        """
        return self

    def __exit__(self,
                 exception_type, exception_value, traceback): # @UnusedVariable
        """
        Context manager exit method.
        Parameters:
            exception_type, exception_value, traceback
                exception details (if an exception is raised in the with block)
        Returns:
            None (= False, True would suppress the exception)
        """
        self.close()

    def open(self):
        """
        Opens the file.
        Parameters:
        Returns:
            None
        """
        if PY2:
            try:
                import pathlib
            except ImportError:
                accepted = string_types
            else:
                accepted = (string_types, pathlib.PurePath)
        else:
            accepted = (string_types, os.PathLike)
        if isinstance(self.filespec, accepted):
            self.filename = self.filespec
            if PY2:
                self.file = open(self.filename, "Urb")
            else:
                self.file = open(self.filename, "r")
            self.logger.info("reading file %s", self.filename)
        else:
            self.filename = None
            self.file = self.filespec
            self.logger.info("reading from stream")

    def close(self):
        """
        Closes the file.
        Parameters:
            None
        Returns:
            None
        """
        if self.filename:
            # only close file if we opened it in open()
            self.file.close()

    def readline(self):
        """
        Read one line of data. Get the net content (no line breaks).

        Parameters:
        """
        self.lnum += 1
        rawline = self.file.readline()
        if rawline == "":
            self.logger.debug(u"read line %d: EOF", self.lnum)
            raise EOFError()
        self.logger.debug(u"read raw line %d: %s", self.lnum, repr(rawline))
        if PY2:
            line = self.decode(rawline)
        else:
            line = rawline
        if self.cvt_nbsp and u'\u00a0' in line:
            if self.cvt_nbsp == 1:
                self.warning('File contains NO-BREAK SPACE characters, will be '
                             'substituted with normal blanks')
                line = line.replace(u'\u00a0', ' ')
                self.cvt_nbsp = 3
            elif self.cvt_nbsp == 2:
                while u'\u00a0' in line:
                    pos = line.index(u'\u00a0') + 1
                    self.warning('Pos {}: NO-BREAK SPACE character, will be '
                                 'substituted with normal blank'.format(pos))
                    line = line.replace(u'\u00a0', ' ', 1)
            else:
                line = line.replace(u'\u00a0', ' ')
        if self.lnum == 1 and self.ignore_bom and line.startswith(u'\ufeff'):
            if self.encoding == 'utf-8':
                self.warning(
                    "File starts with unicode Bit Order Marker (BOM) "
                    "character. "
                    "This is neither needed nor recommended in utf-8 encoding. "
                    "BOM will be ignored.")
            line = line.replace(u"\ufeff", "", 1)
        while self.ignore_bom == 2 and u'\ufeff' in line and \
                (self.lnum > 1 or not line.startswith(u'\ufeff')):
            pos = line.index(u'\ufeff') + 1
            self.warning(
                "Pos {}: Unicode Bit Order Marker (BOM) character at unusual "
                "position (not the start of the file). "
                "BOM will be ignored.".format(pos))
            line = line.replace(u"\ufeff", "", 1)
        if self.strip:
            # strip leading and trailing whitespaces, \n
            line = line.strip()
        if self.tabsize is not None and self.tabsize >= 0:
            # if tabsize is 0 or positive, use expandtabs
            line = line.expandtabs(self.tabsize)
        elif self.tabsize:
            # if tabsize is negative, use fixed number of blanks for each tab
            line = line.replace(u"\t", " " * (-1 * self.tabsize))
        self.logger.debug(u"encoded line %d: %s", self.lnum, repr(line))
        return line

    def decode(self, line):
        """
        Decode a single line of input.
        Parameters:
            line     line of input from the file
        Retruns:
            decoded line (unicode)
        """
        # Try first 7 bit ascii, then the preselected encodings (self.encoding)
        # if set.
        # If strict_enc is not set, select a different encoding if the
        # preselected does not work.

        # If no encoding is preselected (self.encoding is None), then the
        # selection of a suitable codecs will be started.
        # As long as only 7 bit ascii characters are used (codec 'ascii'), there
        # is no change (self.encoding is still None, which means 'whatever may
        # come later').
        # As soon as a UnicodeDecodeError is raised, the diffeent encodings are
        # tried in order.
        # When one of those is selected, self.encoding is fixed, from now on
        # this codec is used for reading the file. If self.strict_enc is set,
        # This encoding must be used for the rest of the file (no change).
        #
        # The different encodings will raise NO warning, because they are
        # officially supported and unambiguous character sets. Fallback to]
        # fallback_encoding will raise a warning (ambiguous encoding).
        #
        # There can be only ONE eight bit encoding (fallback_encoding), because
        # single byte encodings will always succeed (although maybe producing
        # nonsense)
        #
        # utf-8 and single byte encodings:
        # The large number of invalid byte sequences [in utf-8] provides the
        # advantage of making it easy to have a program accept both UTF-8 and
        # legacy encodings such as ISO-8859-1. Thus, the software can check for
        # UTF-8 correctness, and if that fails assume the input to be in the\
        # legacy encoding. It is technically true that this may detect an
        # ISO-8859-1 string as UTF-8, but this is very unlikely if it contains
        # any 8-bit bytes as they all have to be in unusual patterns of two or
        # more in a row, such as ...
        # http://en.wikipedia.org/wiki/UTF-8#Invalid_byte_sequences

        if self.encoding:
            try:
                return line.decode(self.encoding)
            except UnicodeDecodeError:
                if not self.strict_enc:
                    self.encoding = None
                    return self.decode(line)
                if self.enc_line != None:
                    self.error(
                        'character set decode error: line {} suggested codec '
                        "'{}', but it failed in line {}"
                        .format(self.enc_line, self.encoding, self.lnum))
                else:
                    self.error(
                        "character set decode error: codec '{}' failed in line "
                        '{}'.format(self.encoding, line))
        else:
            try:
                return line.decode('ascii')
            except UnicodeDecodeError:
                for enc in range(len(self.encodings)):
                    try:
                        line = line.decode(self.encodings[enc])
                        self.encoding = self.encodings[enc]
                        self.enc_line = self.lnum
                        return line
                    except UnicodeDecodeError:
                        pass
                if self.fallback_encoding:
                    try:
                        line = line.decode(self.fallback_encoding)
                    except UnicodeDecodeError:
                        self.error(
                            "unsupported character encoding; tried: {}".format(
                                ('ascii',) +
                                self.encodings +
                                (self.fallback_encoding,)
                                if self.fallback_encoding
                                else tuple()))
                    self.encoding = self.fallback_encoding
                    self.enc_line = self.lnum
                    self.warning(
                        "character set encoding: fallback to codec '{}'"
                        ' but this might be wrong'
                        .format(self.fallback_encoding))
                    return line

    def goto_line(self, lnum, allow_backpos=True):
        """
        Position the file pointer to specified line number.
        Parameters:
            lnum   line number (positive=from start, negative=from end)
                   0 = before reading the first line
                   -2 = before reading the last line
        Returns:
            None
        Raises:
            EOFError when reaching or exceeding end of file
            BackposError when allow_backpos was False and backwards positioning
            occurred
        """
        oldpos = self.file.tell()
        oldlnum = self.lnum
        if lnum >= 0:
            if self.lnum > lnum:
                # if we are already past, start from the start
                self.file.seek(0, os.SEEK_SET)
                self.lnum = 0
            while self.lnum < lnum:
                self.readline()
        else:
            lines = tail(self.file, (-1) * lnum - 1)
            # seek to length of last n lines
            self.file.seek(0, os.SEEK_END)
            self.file.seek(self.file.tell() - sum([len(l) for l in lines]),
                           os.SEEK_SET)
        if self.file.tell() < oldpos:
            self.file.seek(oldpos, os.SEEK_SET)
            self.lnum = oldlnum
            if not allow_backpos:
                raise BackposError()

    def error(self, msg):
        """
        Error handling for file read.

        Error callback method (self.error_callback):
        If the error callback method is set (self.error_callback), it is called.
        The error callback method must accept following parameters:
            msg
        If the error callback returns True, the error is logged and the
        exception raised if needed.
        If the error callback returns False, everything will be handled by the
        callback method and the local error method will cease action.

        Parameters:
            msg         error message
        Returns:
            None
        Raises:
            NasaAmesError when parameter exception is True
        """
        if not self.error_callback or \
                self.error_callback(msg):
            msg = "line {}: {}".format(self.lnum, msg)
            self.logger.error(msg)
            raise AsciiReadError(msg)

    def warning(self, msg):
        """
        Warning message for file read.

        Warning callback method (self.error_callback):
        If the warning callback method is set (self.warning_callback), it is
        called.
        The warning callback method must accept following parameters:
            msg
        If the warning callback returns True, the warning is logged and the
        exception raised if needed.
        If the warning callback returns False, everything will be handled by the
        callback method and the local warning method will cease action.

        Parameters:
            msg         warning message
        Returns:
            None
        """
        if not self.warning_callback or \
                self.warning_callback(msg):
            msg = "line {}: {}".format(self.lnum, msg)
            self.logger.warning(msg)
