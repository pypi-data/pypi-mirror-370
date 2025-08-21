"""
nilutility/timer.py
$Id: timer.py 1374 2016-09-07 08:58:19Z pe $

Timer class (measure elapsed walltime)
"""

import time

class Timer(object):
    """
    Wall clock timer class.
    """
    def __init__(self):
        """
        Object initialization. Starts timer automatically.
        However, the timer can be started explicitely later by calling start().
        """
        self.starttime = None
        self.stoptime = None
        self.start()

    def start(self):
        """
        Start the timer.
        Parameters:
            None
        Returns:
            None
        """
        self.starttime = time.time()

    def stop(self):
        """
        Stop the timer.
        Parameters:
            None
        Returns:
            None
        """
        self.stoptime = time.time()
    
    def elapsed(self):
        """
        Get timer wall clock time elapsed.
        Parameters:
            None
        Returns:
            time elapsed in seconds (float)
        """
        return self.stoptime - self.starttime
