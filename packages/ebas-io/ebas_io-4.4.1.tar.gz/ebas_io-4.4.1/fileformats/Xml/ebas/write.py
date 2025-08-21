"""
/Xml/write.py
$Id: write.py 2466 2020-07-10 13:20:48Z pe $

Basic XML file writer class.
It adds functionality to generateDS.generatedsuper.GeneratedsSuper.
Handles low level file I/O.

History:
V.1.0.0  2014-08-05  toh  initial version

"""

# import time
# import datetime
# import decimal
# import re
import sys
import inspect
# from nilutility.datatypes import HexInt
from six import PY2, string_types
from .base import XmlError, XmlBase
from .generateDS_ebas import ebas, gml
# from .generateDS_ebas.generateDS_ebas import \
#     Result, ResultSetType, TimeDimensionType, DataSetType, DirectPositionType, PointType, PositionType, \
#     HeightAGLType, WavelengthType, ParticleDiameterType, MeasurementUncertaintyType

class XmlWrite(XmlBase):
    """
    Partial class Xml: Part for writing Xml files from object.
    """
    def write(self, filespec=None):
        """
        Writes the file.
        Parameters:
            filespec    file name (incl. path) or file like object (stream)
                        stdout if not passed
                        
        Returns:
            None
        Raises:
            IOError           file open error
            XmlError          on any unrecoverable write error
        """
        # reset the object state for writing
        self.init_state()
        self.finalize_data()
        
        # toh: initialise XML structures
        self._set_xml()
        
        if filespec is None:
            self.file = sys.stdout
        elif isinstance(filespec, string_types):
            filename = filespec
            self.logger.info("writing file {}".format(filename))
            if PY2:
                mod = "w"
            else:
                mod = "wb"
            with open(filename, mod) as self.file:
                self._write()
        else:
            filename = None
            self.logger.debug("writing to stream")
            self.file = filespec
            self._write()

    def finalize_data(self):
        """
        Calculate data attributes that are not setable by the caller (not in 
        SETABLE_DATA_ATTRIBS). These would be redundant if set by the caller.
        Set default values for unset attributes (initialized to None).
        Parameters:
            None
        Returns:
            None
        Raises:
            various builtin exceptions when data are not set correctly.
        """
        # first set DATA if not set
        if self.data.DATA is None:
            self.data.DATA = []
            
        # calculate unsetable attributes
        self.data.NV = max(len(self.data.DATA), 0)
                
        # set default values for the rest of unset attributes
        if self.data.COMP_NAME is None:
            self.data.COMP_NAME = ['' for _unused in range(self.data.NV)]
        self._checkdims()            

    def _checkdims(self):
        """
        Checks consistency of dimensions and extents in the data structure.
        Parameters:
            None
        Returns:
            None
        Raises:
            XmlError if inconsistent
        """
        # check dimension for COMP_NAME and DATA
        if len(self.data.COMP_NAME) != self.data.NV:
            raise XmlError(
                'COMP_NAME ({} values) inconsistent with NV ({})'.format(
                                    len(self.data.COMP_NAME), self.data.NV)) 
        if len(self.data.DATA) != self.data.NV and \
           (self.data.NV != 0 or len(self.data.DATA) != 0):
            # rais error if #vars - 1 (== # dependent vars) != NV
            # special case: NV=0 and #vars = 0 (=> # dependent vars is -1!) 
            raise XmlError(
                'DATA ({} dep. variables) inconsistent with NV ({})'.format(
                                    len(self.data.DATA) - 1 , self.data.NV))
        # check variable length
        for i in range(self.data.NV-1):
            if len(self.data.DATA[0]) != len(self.data.DATA[i+1]):
                raise XmlError(
                    'number of rows for variable[0] ({}) '.format(
                                                    len(self.data.DATA[0])) +\
                    'is different from variable[{}] ({})'.format(i+1,
                                                    len(self.data.DATA[i+1])))
                
        # check variable length against time
        for i in range(self.data.NV):
            if len(self.data.SAMPLE_TIMES) != len(self.data.DATA[i]):
                raise XmlError(
                    'number of rows for SAMPLE_TIMES ({}) '.format(
                                                    len(self.data.SAMPLE_TIMES)) +\
                    'is different from variable[{}] ({})'.format(i+1,
                                                    len(self.data.DATA[i+1]))) 

    def _set_xml(self):
        """
        Sets the XML structures according to generateDS.
        Parameters:
            None
        Returns:
            None
        Raises:
            XmlError     on any unrecoverable read error
        """
        # set result set
        self.xmlResultSet = ebas.ResultSetType()
        
        # set time variable
        self.xmlTime = ebas.TimeDimensionType()
        self._set_sample_times()
        self.xmlResultSet.set_TimeDimension(self.xmlTime)
        
        # each variable will be written in one result set
        for vnum in range(self.data.NV):
            self.xmlData = ebas.DataSetType()
            for self.state in range (len(self.__class__.SECTIONS)):
                statename = self.curr_state_name()
                try:
                    method = getattr(self, '_set_' + statename.lower())
                except AttributeError:
                    # If no dedicated _set_ method exists: pass
                    pass
                else:
                    # check if method requires vnum argument
                    if 'vnum' in inspect.getargspec(method).args:
                        method(vnum)
                    else:
                        method()
            self.xmlResultSet.add_DataSet(self.xmlData)
                       
    def _set_sample_times(self):
        """
        Set the SAMPLE_TIMES XML element.
        """
        self.xmlTime.set_StartTimes(zip(*self.data.SAMPLE_TIMES)[0])
        self.xmlTime.set_EndTimes  (zip(*self.data.SAMPLE_TIMES)[1])
        
    def _set_station_code(self, vnum):
        """
        Set the STATION_CODE XML element.
        """
        self.xmlData.set_StationCode(self.data.STATION_CODE[vnum])
        
    def _set_station_name(self, vnum):
        """
        Set the STATION_NAME XML element.
        """
        self.xmlData.set_StationName(self.data.STATION_NAME[vnum])
        
    def _set_inst_type(self, vnum):
        """
        Set the INST_TYPE XML element.
        """
        self.xmlData.set_InstrumentType(self.data.INST_TYPE[vnum])
        
    def _set_comp_name(self, vnum):
        """
        Set the COMP_NAME XML element.
        """
        self.xmlData.set_ComponentName(self.data.COMP_NAME[vnum])
        
    def _set_flag_name(self, vnum):
        """
        Set the FLAG_NAME XML element. toh: not required yet
        """
        self.xmlData.set_FlagName(self.data.FLAG_NAME[vnum])
        
    def _set_matrix_name(self, vnum):
        """
        Set the MATRIX_NAME XML element.
        """
        self.xmlData.set_Matrix(self.data.MATRIX_NAME[vnum])
        
    def _set_unit(self, vnum):
        """
        Set the UNIT XML element.
        """
        self.xmlData.set_Unit(self.data.UNIT[vnum])
        
    def _set_statistic_code(self, vnum):
        """
        Set the STATISTIC_CODE XML element.
        """
        self.xmlData.set_Statistics(self.data.STATISTIC_CODE[vnum])
        
    def _set_rescode(self, vnum):
        """
        Set the RESCODE XML element.
        """
        self.xmlData.set_ResolutionCode(self.data.RESCODE[vnum])
        
    def _set_data_level(self, vnum):
        """
        Set the DATA_LEVEL XML element.
        """
        if self.data.DATA_LEVEL[vnum]:
            self.xmlData.set_DataLevel(str(self.data.DATA_LEVEL[vnum]))
        
    def _set_uncertainty(self, vnum):
        """
        Set the UNCERTAINTY XML element.
        """
        if self.data.UNCERTAINTY[vnum]:
            self.xmlData.set_MeasurementUncertainty(
            ebas.MeasurementUncertainty(unit=self.data.UNCERTAINTY[vnum][1],
                                        valueOf_=self.data.UNCERTAINTY[vnum][0]))
        
    def _set_position(self, vnum):
        """
        Set the POSITION XML element.
        """
        self.xmlData.set_Position(ebas.Position(gml.PointType(
        id="pos"+str(self.resultset_id)+'_'+str(vnum),
        srsName="urn:ogc:def:crs:EPSG:6.6:4979",
        srsDimension=len(self.data.POSITION[vnum]),
        pos=gml.DirectPositionType(
        valueOf_=self.data.POSITION[vnum]))))
        
    def _set_height_agl(self, vnum):
        """
        Set the HEIGHT_AGL XML element.
        """
        if self.data.HEIGHT_AGL[vnum]:
            self.xmlData.set_HeightAGL(
            ebas.HeightAGL(unit='m', # toh: unit for measurment height is not given
                           valueOf_=self.data.HEIGHT_AGL[vnum]))
        
    def _set_characteristics(self, vnum):
        """
        Set the XML elements given in CHARACTERISTICS.
        """
        if self.data.CHARACTERISTICS[vnum] is None or \
           len(self.data.CHARACTERISTICS[vnum]) < 1:
            return
        attr = {'Location':   {'setter': self.xmlData.set_Location,
                               'type': None},
                'Wavelength': {'setter': self.xmlData.set_Wavelength,
                               'type': ebas.WavelengthType},
                'D':          {'setter': self.xmlData.set_D,
                               'type': ebas.ParticleDiameterType},
                'Dmin':       {'setter': self.xmlData.set_Dmin,
                               'type': ebas.ParticleDiameterType},
                'Dmax':       {'setter': self.xmlData.set_Dmax,
                               'type': ebas.ParticleDiameterType},
               }
               
        for char in self.data.CHARACTERISTICS[vnum].sorted():
            if char.CT_TYPE in attr:
                inf = attr[char.CT_TYPE]
                (_skip, value, unit) = char.tuple()
                if inf['type']:
                    if unit:
                        inf['setter'](inf['type'](valueOf_=value, unit=unit))
                    else:
                        inf['setter'](inf['type'](valueOf_=value))
                else:
                    inf['setter'](value)
        
        def _set_location(self, char):
            """
            Set the Location XML element.
            """
            self.xmlData.set_Location(str(char.tuple()[1]))
            
        def _set_wavelength(self, char):
            """
            Set the Wavelength XML element.
            """
            self.xmlData.set_Wavelength(ebas.WavelengthType(
            unit=char.tuple()[2],valueOf_=char.tuple()[1]))
            
        def _set_d(self, char):
            """
            Set the D XML element.
            """
            self.xmlData.set_D(ebas.ParticleDiameterType(
            unit=char.tuple()[2],valueOf_=char.tuple()[1]))
            
        def _set_dmin(self, char):
            """
            Set the Dmin XML element.
            """
            self.xmlData.set_Dmin(ebas.ParticleDiameterType(
            unit=char.tuple()[2],valueOf_=char.tuple()[1]))
            
        def _set_dmax(self, char):
            """
            Set the Dmax XML element.
            """
            self.xmlData.set_Dmin(ebas.ParticleDiameterType(
            unit=char.tuple()[2],valueOf_=char.tuple()[1]))
        
    def _set_data(self, vnum):
        """
        Set the DATA XML element.
        """
        if len(self.data.DATA[vnum]) == 0:
            return
        self.xmlData.set_Values(self.data.DATA[vnum])
        
    def _set_flags(self, vnum):
        """
        Set the FLAGS XML element.
        """
        # toh: flags are not required yet
        self.xmlData.set_Flags(self.data.FLAGS[vnum])
        
    def _set_setkey(self, vnum):
        """
        Set the SETKEY XML element.
        """
        self.xmlData.set_setkey(self.data.SETKEY[vnum])
                
    def _write(self):
        """
        Writes the file to opened file handle.
        This method is only needed to extract the write functionality in order
        to wrap the 'with open(filename)' around it in the read() method.
        Parameters:
            None
        Returns:
            None
        Raises:
            XmlError     on any unrecoverable read error
        """
        self.xmlResultSet.export(self.file, 1, name_='ResultSet')
        self.logger.debug(u"export XML object")
           
