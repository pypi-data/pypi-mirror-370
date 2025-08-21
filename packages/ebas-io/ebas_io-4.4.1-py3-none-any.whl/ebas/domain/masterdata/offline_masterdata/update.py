#!/usr/bin/env python
"""
update.py
$Id: update.py 2743 2021-11-23 15:48:15Z pe $

Update offline masterdata from database.

History:
V.0.1.0  2014-02-28  pe  initial version

"""
__version__ = '0.1.0-devel $Rev: 2743 $'


import logging

# if __name__ == '__main__':
#     if __package__ is None:
import sys
from os import path
#         sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.join(path.dirname(path.abspath(__file__)),
                          '..', '..', '..', '..'))
#         import offline_masterdata
#     else:
#         from . import offline_masterdata
# # need some path tweaking, add ../.. (= ebas lib) to python path

import offline_masterdata
from ebas.commandline import EbasCommandline

def update_masterdata(cmdline):
    """
    Main program for update
    Created for lexical scoping.

    Parameters:
        none
    Returns:
        none
    """
    logger = logging.getLogger('update')

    dbh = cmdline.dbh
    # don't register user with db layer, not necessary for update masterdata

    logger.info(' AC')
    offline_masterdata.ACOfflineMasterData.write_pickle_file(dbh)
    logger.info(' AX')
    offline_masterdata.AXOfflineMasterData.write_pickle_file(dbh)
    logger.info(' AM')
    offline_masterdata.AMOfflineMasterData.write_pickle_file(dbh)
    logger.info(' AY')
    offline_masterdata.AYOfflineMasterData.write_pickle_file(dbh)
    logger.info(' BC')
    offline_masterdata.BCOfflineMasterData.write_pickle_file(dbh)
    logger.info(' CA')
    offline_masterdata.CAOfflineMasterData.write_pickle_file(dbh)
    logger.info(' CC')
    offline_masterdata.CCOfflineMasterData.write_pickle_file(dbh)
    logger.info(' CO')
    offline_masterdata.COOfflineMasterData.write_pickle_file(dbh)
    logger.info(' CT and CV')
    offline_masterdata.CTOfflineMasterData.write_pickle_file(dbh)
    logger.info(' CY')
    offline_masterdata.CYOfflineMasterData.write_pickle_file(dbh)
    logger.info(' DL')
    offline_masterdata.DLOfflineMasterData.write_pickle_file(dbh)
    logger.info(' FL')
    offline_masterdata.FLOfflineMasterData.write_pickle_file(dbh)
    logger.info(' FM')
    offline_masterdata.FMOfflineMasterData.write_pickle_file(dbh)
    logger.info(' FT')
    offline_masterdata.FTOfflineMasterData.write_pickle_file(dbh)
    logger.info(' FP')
    offline_masterdata.FPOfflineMasterData.write_pickle_file(dbh)
    logger.info(' HT')
    offline_masterdata.HTOfflineMasterData.write_pickle_file(dbh)
    logger.info(' IM')
    offline_masterdata.IMOfflineMasterData.write_pickle_file(dbh)
    logger.info(' IP')
    offline_masterdata.IPOfflineMasterData.write_pickle_file(dbh)
    logger.info(' IT')
    offline_masterdata.ITOfflineMasterData.write_pickle_file(dbh)
    logger.info(' MA')
    offline_masterdata.MAOfflineMasterData.write_pickle_file(dbh)
    logger.info(' MD')
    offline_masterdata.MDOfflineMasterData.write_pickle_file(dbh)
    logger.info(' OC')
    offline_masterdata.OCOfflineMasterData.write_pickle_file(dbh)
    logger.info(' OR')
    offline_masterdata.OROfflineMasterData.write_pickle_file(dbh)
    logger.info(' PM')
    offline_masterdata.PMOfflineMasterData.write_pickle_file(dbh)
    logger.info(' PG')
    offline_masterdata.PGOfflineMasterData.write_pickle_file(dbh)
    logger.info(' PL')
    offline_masterdata.PLOfflineMasterData.write_pickle_file(dbh)
    logger.info(' PR')
    offline_masterdata.PROfflineMasterData.write_pickle_file(dbh)
    logger.info(' PS')
    offline_masterdata.PSOfflineMasterData.write_pickle_file(dbh)
    logger.info(' QM')
    offline_masterdata.QMOfflineMasterData.write_pickle_file(dbh)
    logger.info(' QO')
    offline_masterdata.QOOfflineMasterData.write_pickle_file(dbh)
    logger.info(' QV')
    offline_masterdata.QVOfflineMasterData.write_pickle_file(dbh)
    logger.info(' RE')
    offline_masterdata.REOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SE')
    offline_masterdata.SEOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SM')
    offline_masterdata.SMOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SC')
    offline_masterdata.SCOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SP')
    offline_masterdata.SPOfflineMasterData.write_pickle_file(dbh)
    logger.info(' ST')
    offline_masterdata.STOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SX')
    offline_masterdata.SXOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SZ')
    offline_masterdata.SZOfflineMasterData.write_pickle_file(dbh)
    logger.info(' SW')
    offline_masterdata.SWOfflineMasterData.write_pickle_file(dbh)
    logger.info(' VP')
    offline_masterdata.VPOfflineMasterData.write_pickle_file(dbh)
    logger.info(' VT')
    offline_masterdata.VTOfflineMasterData.write_pickle_file(dbh)
    logger.info(' WC')
    offline_masterdata.WCOfflineMasterData.write_pickle_file(dbh)
    logger.info(' ZN')
    offline_masterdata.ZNOfflineMasterData.write_pickle_file(dbh)
    logger.info(' ZT')
    offline_masterdata.ZTOfflineMasterData.write_pickle_file(dbh)
    logger.info('all masterdata caches updated')


EbasCommandline(update_masterdata, custom_args=['LOGGING', 'DB', 'CONFIG'],
                help_description='%(prog)s update masterdata caches.',
                version=__version__, read_masterdata=False).run()
