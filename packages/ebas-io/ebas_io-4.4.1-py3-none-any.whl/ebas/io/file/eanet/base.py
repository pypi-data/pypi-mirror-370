"""
$Id: base.py 2759 2021-11-30 11:41:16Z pe $
EANET base class
"""

from ..basefile.file import EbasFile
from ...base import EbasIOError
from ebas.domain.masterdata.org import EbasMasterOR
from ebas.domain.masterdata.st import EbasMasterST

class EbasEanetReadError(EbasIOError):
    """
    Exception class for EANET read errors.
    """
    pass



class EbasEanetBase(EbasFile):  # pylint: disable=W0223
    # W0223: Method ... is abstract in base class but is not overridden
    # This is also an abstract class, just does not raise NotImplementedError
    """
    Base class.
    """

    def _set_method(self, metadata):
        """
        Set the method from analytical lab code and method name
        """
        if 'method' not in metadata or not metadata.method:
            metadata.method = ''
            if '#ana_lab_code' in metadata and metadata['#ana_lab_code']:
                metadata.method += metadata['#ana_lab_code']
            elif 'lab_code' in metadata and metadata['lab_code']:
                self.warning(
                    "#ana_lab_code not set, using lab_code for method")
                metadata.method += metadata['lab_code']
            else:
                self.error(
                    "#ana_lab_code and lab_code not set")
            if '#method_name' in metadata and metadata['#method_name']:
                metadata.method += '_' + metadata['#method_name']
            else:
                self.error(
                    "#method_name not set")
        if '#ana_lab_code' in metadata:
            del metadata['#ana_lab_code']
        if '#method_name' in metadata:
            del metadata['#method_name']

    def _set_station(self, metadata):
        """
        Set all station metadata:
            - by station code from config from ebas masterdata
            - then override from config
        """
        
        if 'station_code' in metadata and metadata.station_code:
            try:
                master_st = EbasMasterST()[metadata.station_code]
            except KeyError:
                self.warning(
                    "Station '{}' not found in EBAS "
                    "masterdata.".format(metadata.station_code))
            else:
                # station_code already set, no need to copy
                # platform code is special, needs to be mapped manually:
                if 'platform_code' not in metadata:
                    metadata.platform_code = \
                        master_st.ST_STATION_CODE[:-1] + \
                        master_st.PF_PLATFORM
                # generic mapping:
                maps = [
                    ('station_name', 'ST_NAME'),
                    ('station_wdca_id', 'ST_WDCA_ID'),
                    ('station_gaw_id', 'ST_GAW_ID'),
                    ('station_gaw_name', 'ST_GAW_NAME'),
                    ('station_airs_id', 'ST_AIRS_ID'),
                    ('station_other_ids', 'ST_OTHER_ID'),
                    ('station_state_code', 'ST_STATE_CODE'),
                    ('station_landuse', 'SL_STATION_LANDUSE'),
                    ('station_setting', 'SS_STATION_SETTING'),
                    ('station_gaw_type', 'SG_STATION_GAW_TYPE'),
                    ('station_wmo_region', 'SW_STATION_WMO_REGION'),
                    ('station_latitude', 'ST_LATITUDE'),
                    ('station_longitude', 'ST_LONGITUDE'),
                    ('station_altitude', 'ST_ALTITUDE_ASL'),
                ]
                for keys in maps:
                    if keys[0] not in metadata:
                        metadata[keys[0]] = master_st[keys[1]]

    def _set_org(self, metadata):
        """
        Map the organisation code.
        """
        org = {
            # Empty org dict, just to make sure all keys exist.
            'OR_CODE': None,
            'OR_NAME': None,
            'OR_ACRONYM':  None,
            'OR_UNIT':  None,
            'OR_ADDR_LINE1':  None,
            'OR_ADDR_LINE2':  None,
            'OR_ADDR_ZIP':  None,
            'OR_ADDR_CITY':  None,
            'OR_ADDR_COUNTRY':  None,
        }
        if 'org' in metadata and metadata.org:
            if 'OR_CODE' in metadata.org and metadata.org.OR_CODE:
                try:
                    org.update(EbasMasterOR()[metadata.org['OR_CODE']])
                except KeyError:
                    self.warning(
                        "Organisation '{}' not found in EBAS "
                        "masterdata.".format(metadata.org['OR_CODE']))
        elif 'lab_code' in metadata and metadata.lab_code:
            self.warning(
                "No organisation defined in masterdata. Using lab code")
            try:
                org.update(EbasMasterOR()[metadata.lab_code])
            except KeyError:
                self.warning(
                    "Organisation '{}' not found in EBAS masterdata.".format(
                    metadata.lab_code))
        org.update(metadata.org)
        metadata.org = org


class EbasEanetFilterBase(EbasEanetBase):  # pylint: disable=W0223
    # W0223: Method ... is abstract in base class but is not overridden
    # This is also an abstract class, just does not raise NotImplementedError
    """
    Base class.
    """
    # set exception for generic read method
    READ_EXCEPTION = EbasEanetReadError

    def __init__(self, *args, **kwargs):
        """
        Class initioalization.
        """
        EbasEanetBase.__init__(self, *args, **kwargs)
        # add one additional attribute:
        self.sourcefile = None
        self.setup_non_domain()


class EbasEanetPrecipBase(EbasEanetBase):  # pylint: disable=W0223
    # W0223: Method ... is abstract in base class but is not overridden
    # This is also an abstract class, just does not raise NotImplementedError
    """
    Base class.
    """
    # set exception for generic read method
    READ_EXCEPTION = EbasEanetReadError

    def __init__(self, *args, **kwargs):
        """
        Class initioalization.
        """
        EbasEanetBase.__init__(self, *args, **kwargs)
        # add one additional attribute:
        self.sourcefile = None
        self.setup_non_domain()
        self._prec_values = None
