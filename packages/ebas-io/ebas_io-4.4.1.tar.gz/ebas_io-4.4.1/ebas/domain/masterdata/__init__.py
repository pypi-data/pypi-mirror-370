"""
Masterdata caches (submodule masterdata):

A module to cache all important masterdata in EBAS. Those masterdata are mainly
lists of controlled vocabulary (e.g. parameters, instrument types, ...).

Those parts of the code which do not have direct access to the database
(e.g. ebas-io module running on a user's machine) use this caches. Parts of
code which have database access, update those caches right after connecting.

The storage technology is simple python pickle files.
"""
import logging
from .am import EbasMasterAM
from .ac import EbasMasterAC
from .ax import EbasMasterAX
from .ay import EbasMasterAY
from .bc import EbasMasterBC
from .ca import EbasMasterCA
from .cc import EbasMasterCC
from .co import EbasMasterCO
from .cy import EbasMasterCY
from .dc import DCBase
from .dl import EbasMasterDL
from .fl import EbasMasterFL
from .fm import EbasMasterFM
from .ft import EbasMasterFT
from .ht import EbasMasterHT
from .im import EbasMasterIM
from .ip import EbasMasterIP
from .it import EbasMasterIT
from .ma import EbasMasterMA
from .md import EbasMasterMD
from .oc import EbasMasterOC
from .org import EbasMasterOR
from .pg_pl import EbasMasterPG, EbasMasterPL
from .pm import EbasMasterPM
from .pr import EbasMasterPR
from .ps import EbasMasterPS
from .qm_qv import EbasMasterQM, EbasMasterQV
from .re import EbasMasterRE
from .sc import EbasMasterSC
from .se import EbasMasterSE
from .sm import EbasMasterSM
from .sp import EbasMasterSP
from .st import EbasMasterST
from .sw import EbasMasterSW
from .sx import EbasMasterSX
from .sz import EbasMasterSZ
from .vp import EbasMasterVP
from .vt import EbasMasterVT
from .wc import EbasMasterWC
from .zn import EbasMasterZN
from .zt import EbasMasterZT


def read_all_caches_from_db(dbh):
    """
    Reads all chache masterdata from db. This can be called by programs that
    have db access and want to make sure all called modules work with current
    master data from the database.
    Parameters:
        dbh    database handle
    Returns:
        None
    """
    EbasMasterAC(dbh)
    EbasMasterAM(dbh)
    EbasMasterAX(dbh)
    EbasMasterAY(dbh)
    EbasMasterBC(dbh)
    EbasMasterCA(dbh)
    EbasMasterCC(dbh)
    EbasMasterCO(dbh)
    EbasMasterCY(dbh)
    DCBase(dbh)
    EbasMasterDL(dbh)
    EbasMasterFL(dbh)
    EbasMasterFM(dbh)
    EbasMasterFT(dbh)
    EbasMasterHT(dbh)
    EbasMasterIM(dbh)
    EbasMasterIP(dbh)
    EbasMasterIT(dbh)
    EbasMasterMA(dbh)
    EbasMasterMD(dbh)
    EbasMasterOC(dbh)
    EbasMasterOR(dbh)
    EbasMasterPG(dbh)
    EbasMasterPL(dbh)
    EbasMasterPM(dbh)
    EbasMasterPR(dbh)
    EbasMasterPS(dbh)
    EbasMasterQM(dbh)
    EbasMasterQV(dbh)
    EbasMasterRE(dbh)
    EbasMasterSC(dbh)
    EbasMasterSE(dbh)
    EbasMasterSM(dbh)
    EbasMasterSP(dbh)
    EbasMasterST(dbh)
    EbasMasterSW(dbh)
    EbasMasterSX(dbh)
    EbasMasterSZ(dbh)
    EbasMasterVP(dbh)
    EbasMasterVT(dbh)
    EbasMasterWC(dbh)
    EbasMasterZN(dbh)
    EbasMasterZT(dbh)
