"""
$Id: offline_masterdata.py 2743 2021-11-23 15:48:15Z pe $

EBAS Offline Masterdata classes
"""

import os
from ebas.domain.masterdata.offline_masterdata.base import OfflineMasterDataBase


class ACOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for AC
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'AC.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ac()
        cls.INIT = True

class AMOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for AM
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'AM.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_am()
        cls.INIT = True

class AXOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for AX
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'AX.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ax()
        cls.INIT = True


class AYOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for AY
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'AY.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ay()
        cls.INIT = True


class BCOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for BC and BA
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'BC.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_bc()
        # set all characteristics to []:
        for bc_id in cls.META:
            cls.META[bc_id]['characteristics'] = {}
        for ba_ in dbh.getcache_ba():
            if ba_['CT_DATATYPE'] == 'CHR':
                val = ba_['BA_VAL_CHR']
            elif ba_['CT_DATATYPE'] == 'INT':
                val = ba_['BA_VAL_INT']
            else:
                val = ba_['BA_VAL_DBL']
            cls.META[ba_['BC_ID']]['characteristics'][ba_['CT_TYPE']] = val
        cls.INIT = True


class CAOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for CA
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'CA.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ca()
        cls.INIT = True


class CCOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for CC
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'CC.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_cc()
        cls.INIT = True


class COOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for CO
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'CO.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_co()
        cls.INIT = True


class CXOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for CX
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'CX.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_cx()
        cls.INIT = True


class CYOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for CY
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'CY.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_cy()
        cls.INIT = True


class CTOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for CT and CV
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'CT_CV.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handke
        Returns:
            None
        """
        cls.META['SORTORDER'] = list(dbh.get_ct_order())
        cls.META['CHARACTERISTICS'] = {}
        for ct_ in cls.META['SORTORDER']:
            cls.META['CHARACTERISTICS'][ct_] = dbh.select_ct(ct_)
        cls.META['VALIDITY'] = list(dbh.selectlist_cv())
        cls.INIT = True


class DLOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for DL
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'DL.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_dl()
        cls.INIT = True


class FLOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for FL
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'FL.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_fl()
        cls.INIT = True


class FMOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for FM
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'FM.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_fm()
        cls.INIT = True


class FPOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for FP
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'FP.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_fp()
        cls.INIT = True

class FTOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for FT
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'FT.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ft()
        cls.INIT = True

class IMOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for IM
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'IM.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_im()
        cls.INIT = True


class HTOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for HT
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'HT.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ht()
        cls.INIT = True


class IPOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for IP.
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'IP.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ip()
        cls.INIT = True


class ITOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for IT.
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'IT.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_it()
        cls.INIT = True


class MAOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for MA
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'MA.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ma()
        cls.INIT = True


class MDOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for MD
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'MD.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_md()
        cls.INIT = True


class OCOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for OC
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'OC.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_oc()
        cls.INIT = True


class OROfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for OR
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'OR.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_or()
        cls.INIT = True


class PMOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for PM.
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'PM.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_pm()
        cls.INIT = True


class PGOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for PG.
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'PG.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_pg()
        cls.INIT = True


class PLOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for PL.
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'PL.pkl')
    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_pl()
        cls.INIT = True


class PROfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for PR
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'PR.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_pr()
        cls.INIT = True


class PSOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for PS
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'PS.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_ps()
        cls.INIT = True


class QMOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for QM
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'QM.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_qm()
        cls.INIT = True


class QOOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for QO
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'QO.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_qo()
        cls.INIT = True


class QVOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for QV
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'QV.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_qv()
        cls.INIT = True


class REOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for RE
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'RE.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_re()
        cls.INIT = True


class SCOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SC
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SC.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_sc()
        cls.INIT = True


class SEOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SE
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SE.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_se()
        cls.INIT = True


class SMOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SM
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SM.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_sm()
        cls.INIT = True


class SPOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SP
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SP.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_sp()
        cls.INIT = True


class STOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for ST
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'ST.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_st()
        cls.INIT = True


class SXOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SX
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SX.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_sx()
        cls.INIT = True


class SZOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SZ
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SZ.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_sz()
        cls.INIT = True


class SWOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for SW
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'SW.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_sw()
        cls.INIT = True


class VPOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for VP
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'VP.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_vp()
        cls.INIT = True


class VTOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for VT
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'VT.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_vt()
        cls.INIT = True


class WCOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for WC
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'WC.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_wc()
        cls.INIT = True


class ZNOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for ZN
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'ZN.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_zn()
        cls.INIT = True


class ZTOfflineMasterData(OfflineMasterDataBase):
    """
    Base class for handling Offline Masterdata for ZT
    """
    # file name
    META_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'ZT.pkl')

    @classmethod
    def from_db(cls, dbh):
        """
        Update the cache from the database.
        Parameters:
            dbh     database handle
        Returns:
            None
        """
        cls.META = dbh.getcache_zt()
        cls.INIT = True
