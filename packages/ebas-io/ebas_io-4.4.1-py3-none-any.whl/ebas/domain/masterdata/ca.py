"""
$Id: ca.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for calibration scales

This module implements the class EbasMasterCA.
"""

from .offline_masterdata import CAOfflineMasterData
from .base import EbasMasterBase
from .co import PTR_MS_COMP

class EbasMasterCA(EbasMasterBase, CAOfflineMasterData):
    """
    Domain Class for calibration scale masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling sensor types and checking them against master data.
    Sensor type master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for SE (sensor types)
    # Those are fallback values, will be read from database as soon as possible.
    CAOfflineMasterData.read_pickle_file()

    # some hardcoded exceptional components (see method exceptional):            
    CA_EXCEPTIONAL = {
        '0': {}
    }
    # PTR-MS lev0:
    for comp in PTR_MS_COMP:
        CA_EXCEPTIONAL['0'][(comp, 'NPL')] = {
            'CO_COMP_NAME': comp,
            'CA_CALIBRATION_SCALE': 'NPL',
            'CA_DESC': None,
            'CA_COMMENT': None,
        }


    def __init__(self, dbh=None):
        """
        Read se masterdata if dbh is provided.
        """
        CAOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def __getitem__(self, key):
        """
        Allows dictionary like access to metadata.
        Exception for CA:
            - exceptional metadata lookup (non DB, data level dependent)
        Parameters:
            key    tuple (comp_name, calibration_scale, data_level)
                   Only the first 2 aer used for regulat lookup!
                   data_level is optional and is used for finding exceptional
                   data level dependent masterdata
        """
        # first try: use regular masterdata, ignore data level
        try:
            return self.__class__.META[key[:2]]
        except KeyError:
            # don't exist: try exceptional masterdata (needs data level)
            # Those masterdata are NOT defined in the database, but might be
            # used e.g. in lev 0 files.
            # Thus they are accepted when reading the file, but the domain
            # layer will issue an error message.
            if len(key) != 3:
                raise
            data_level = key[2]
            if data_level in ('0a', '0b'):
                data_level = '0'
            return self.__class__.CA_EXCEPTIONAL[data_level][key[:2]]

    @classmethod
    def exist_calibrationscale(cls, cal_scale):
        """
        Check if the sensor type exists (regardless of FT and CO).
        Parameters:
            cal_scale    sensor type code to be checked
        Returns:
            True/False
        """
        if any([key[1] == cal_scale for key in list(cls.META.keys())]):
            return True
        if any([key[1] == cal_scale
                for dl_ in cls.CA_EXCEPTIONAL.keys()
                for key in list(cls.CA_EXCEPTIONAL[dl_].keys())]):
            return True
        return False
