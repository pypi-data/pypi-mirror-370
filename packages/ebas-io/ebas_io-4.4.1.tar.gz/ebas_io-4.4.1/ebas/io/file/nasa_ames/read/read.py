"""
ebas/nasa_ames/read
$Id: read.py 2097 2018-07-10 10:49:34Z pe $

File input functionality for EBAS NASA Ames module

! Attention !
Basic Nasa Ames 1001 functionality is implemented in the NasaAmes1001 class.
The ebas/nasa_ames (this) module is about EBAS extentions!

History:
V.1.0.0  2013-03-05  pe  initial version

"""

from .parse import NasaAmesPartialReadParser
from ..base import EbasNasaAmesReadError
from fileformats.NasaAmes1001 import NasaAmes1001, NasaAmes1001Error

class NasaAmesPartialRead(NasaAmesPartialReadParser):  # pylint: disable=R0901
    # R0901: Too many ancestors
    # This is a quite big class, therefore we ignore this warning
    """
    Nasa Ames I/O object.
    This is one part of the partial class NasaAmes (input functionality).
    """

    def _read(self, filename,  # pylint: disable=R0913, W0221
              ignore_rescode=False, ignore_revdate=False,  # @UnusedVariable
              ignore_parameter=False, ignore_sampleduration=False,
              skip_data=False,  # @UnusedVariable
              skip_unitconvert=False, skip_variables=None,  # @UnusedVariable
              encoding=None, ignore_numformat=False, ignore_dx0=False):
        # # @UnusedVariable
        # R0913 Too many arguments
        # W0221 _read:Arguments number differs from overridden '_read' method
        """
        Reads a NASA Ames files to NasaAmes object.
        Parameters:
            filename          path and filename
            ignore_rescode    ignore rescde errors (downgraded to warning)
            ignore revdate    ignore revdate errors (downgrade to warning)
            ignore_parameters ignore errors related to paramters and units
                              this is needed when a file with non standard
                              vnames should be processed without importing it
                              into the ebas.domain.
            skip_data         skip reading of data (speedup, if data are not
                              needed at application level). First and last line
                              are read. (Tjis is just passed to NasaAmes1001)
            skip_unitconvert  skips the automatic unit conversion on input
                              this is needed when a file with non standard units
                              should be processed without importing it into the
                              ebas.domain.
            skip_variables    list of variable numbers to be skipped (variabzle
                              numbers start with 1 for the first variable after
                              end_time)

            Specific for EbasNasaAmes._read:
            encoding          encoding of the file (passed through to
                              NasaAmes1001)
                              default: None (NasaAmes1001 tries to find a codec)
            ignore_numformat  ignore number format errors
            ignore_dx0        ignore error when DX=0 with regular data

        Returns:
            None
        Raises:
            IOError (from builtin, file open)
            EbasNasaAmesReadError
        """
        strictness = 0
        if not ignore_numformat:
            strictness |= NasaAmes1001.STRICT_NUMFORMAT
        if not ignore_dx0:
            strictness |= NasaAmes1001.STRICT_DX
        self.nasa1001 = NasaAmes1001(strictness=strictness)
        try:
            self.nasa1001.read(filename, encoding, skip_data=skip_data,
                               condense_messages=self.msg_condenser.threshold)
        except NasaAmes1001Error:
            pass
        self.errors += self.nasa1001.errors
        self.warnings += self.nasa1001.warnings
        if self.errors:
            self.logger.info("Exiting because of previous errors")
            raise EbasNasaAmesReadError(
                "{} Errors, {} Warnings".format(self.nasa1001.errors,
                                                self.nasa1001.warnings))

        self.parse_nasa_ames_1001(skip_variables=skip_variables,
                                  ignore_parameter=ignore_parameter)

    def msgref_vnum_lnum(self, vnum):
        """
        Get info on variable number and line number for error messages.
        Overrides the EbasFileBase method.
        If the file has been read from an input file, the the variable number
        and line numbers are adjusted to the actual file.
        Parameters:
            vnum    variable index in the file object
        Returns:
            (file_vnum, file_num) where:
                file_vnum: the real variable number in the physical file
                           (if there was a physical file read)
                           Variable 1 is the first variable after end_time
                file_lnum: the line number offset for the first data line in
                           the physical file (if there was a physical file read)
                file_metalnum: the line number reference that should be used for
                               metadata releted messages
        """
        file_vnum, file_lnum, file_metalnum = \
            super(NasaAmesPartialRead, self).msgref_vnum_lnum(vnum)
        # if read from file, get real variable number and line number in file:
        # (ibeacuse flag columns, possible skipped columns in between...)
        if self.internal.read_tmp and 'var_num' in self.internal.read_tmp \
           and self.internal.read_tmp.var_num:
            file_vnum = self.internal.read_tmp.var_num[vnum]
            file_metalnum = 13 + file_vnum
        if self.nasa1001:
            file_lnum = 13 + self.nasa1001.data.NV + 1 + \
                len(self.nasa1001.data.SCOML) + 1 + \
                len(self.nasa1001.data.NCOML)

        return (file_vnum, file_lnum, file_metalnum)
