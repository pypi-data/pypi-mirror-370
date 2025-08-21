"""
$Id: se.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for sensor types

This module implements the class EbasMasterSE.
"""

from .offline_masterdata import SEOfflineMasterData
from .base import EbasMasterBase

class EbasMasterSE(EbasMasterBase, SEOfflineMasterData):
    """
    Domain Class for sensor type masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling sensor types and checking them against master data.
    Sensor type master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for SE (sensor types)
    # Those are fallback values, will be read from database as soon as possible.
    SEOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read se masterdata if dbh is provided.
        """
        SEOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def exist_sensortype(cls, sensor_type):
        """
        Check if the sensor type exists (regardless of FT and CO).
        Parameters:
            sensor_type    sensor type code to be checked
        Returns:
            True/False
        """
        if any([key[2] == sensor_type for key in list(cls.META.keys())]):
            return True
        return False
