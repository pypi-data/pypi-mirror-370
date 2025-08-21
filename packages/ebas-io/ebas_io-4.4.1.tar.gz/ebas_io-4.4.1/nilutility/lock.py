"""
nilutility/lock.py
$Id: lock.py 1388 2016-09-15 09:05:32Z pe $

Simple lock file handling
"""

import os
import logging

class LockError(Exception):
    """
    Exception class, raised if something strange happened with locks.
    """
    pass

class Lock(object):
    """
    Implements a simple lock file mechanism.
    """

    def __init__(self, lockfile):
        """
        Initialize locking class
        """
        self.status = False
        self.lockfile = lockfile
        self.logger = logging.getLogger('lock')

    def lock(self):
        """
        Lock the lockfile.
        Parameters:
            None
        Retiurn:
            True when locked, False when locking could not be aquired.
        """
        if os.path.isfile(self.lockfile):
            self.logger.error('no lock aquired (lockfile exists: {})'
                .format(self.lockfile))
            return False
        open(self.lockfile, 'a').close()
        self.status = True
        self.logger.debug('lock aquired (lockfile created: {})'
            .format(self.lockfile))
        return True

    def release(self):
        if not self.status:
            self.logger.error('lock: called release without a lock')
            raise LockError("Release without a lock")
        if not os.path.isfile(self.lockfile):
            self.logger.error('lock file vanished: {}'
                .format(self.lockfile))
            raise LockError("Lockfile vanished")
        os.remove(self.lockfile)
        self.logger.debug('lock released (lockfile deletd: {})'
            .format(self.lockfile))
        self.status = False
