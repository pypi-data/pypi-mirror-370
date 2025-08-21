"""
ebas/time_period.py
$Id: time_period.py 2794 2022-04-06 14:41:36Z pe $

functions for time intervals period/resolution code

History:
V.1.0.0  2013-05-30  pe  initial version

"""

import re
import dateutil.relativedelta
import datetime
from nilutility.statistics import modified_median
from nilutility.datetime_helper import DatetimeISO8601Duration

GREGORIAN_DAYS = 365.+(1./4)-(1./100)+(1./400)

PERIOD_CODE_FACTORS = {
                     'ms':  0.001,
                     's':  1,
                     'mn': 60,
                     'h':  60*60,
                     'd':  60*60*24,
                     'w':  60*60*24*7,
                     'mo': 60*60*24*(GREGORIAN_DAYS)/12.,
                     'y': 60*60*24*(GREGORIAN_DAYS)
    # month:    ...*(days_per_year)/12
    #  average days per year according to gregorian calendar,
    #  ignoring leap seconds
                     }

def parse_period_code(rescode):
    """
    Parse the period code string.
    Parameters:
        rescode    period code string
    Returns:
        tupel (value, unit) where value is the integer number and unit is the
        time unit
    Raises:
        ValueError where the string can not be parsed
    """
    match = re.match(r'^(\d+)(ms|s|mn|h|d|w|mo|y)$', rescode)
    if not match:
        raise ValueError("illegal period code {0}".format(rescode))
    return (int(match.group(1)), match.group(2))

def period_code_seconds(rescode):
    """
    Returns the given periode in converted to seconds.
    This is an estimate for month ('mo' periode codes), else it should be
    exact.
    e.g. '2w'  --> 2*7*24*60*60 = 1209600.0
         '6mo' --> 6*30.4*24*60*60 = 15759360.0
         '5mn' --> 5*60 = 300.0
         '400ms' --> 0.4
    Parameters:
        rescode    resolution code string, number+time unit
                   (time units: s, mn, h, d, w, mo)
    Returns:
        rescode converted to seconds
    Raises:
        ValueError
            when period code not known
    """
    (value, unit) = parse_period_code(rescode)
    return value * PERIOD_CODE_FACTORS[unit]

def period_code_iso8601_duration(rescode):
    """
    Returns the given periode as a DatetimeISO8601Duration object.
    
    e.g. '2w'  --> P14d or P0000-0014T00:00:00
         '6mo' --> P6M or P0000-06-00T00:00:00
         '5mn' --> PT5M or P0000-00-00T00:05:00
         '400ms' --> PT0.4S or P0000-00-00T00:00:00.400000
    Parameters:
        rescode    resolution code string, number+time unit
                   (time units: s, mn, h, d, w, mo)
    Returns:
        DatetimeISO8601Duration object
    """
    dur = DatetimeISO8601Duration()
    (value, unit) = parse_period_code(rescode)
    if value == 0:
        # 0 whatever unit is quite undefined... return empty duration
        return dur
    if unit == 'y':
        dur.year = value
    if unit == 'mo':
        dur.month = value
    if unit == 'w':
        dur.day = value * 7
    if unit == 'd':
        dur.day = value
    if unit == 'h':
        dur.hour = value
    if unit == 'mi':
        dur.minute = value
    if unit == 's':
        dur.second = value
    if unit == 'ms':
        dur.microsecond = value * 1000
    return dur

def normalize_period_code(rescode):
    """
    Returns the given periode in ebas standard period code.
    (which is the shortest possible integer number)
    e.g.:
         '300s'    --> '5mn'
         '60mn'    --> '1h'
         '3600s'   --> '1h'
         '48h'     --> '2d'
         '7d'      --> '1w'
         '604800s' --> '1w'
    Month and year codes will not be generated (both are variable length).
    
    Parameters:
        rescode    resolution code string, number+time unit
                   (time units: s, mn, h, d, w, mo)
    Returns:
        rescode converted to standard
    Raises:
        ValueError
            when period code not known
    """
    (value, unit) = parse_period_code(rescode)
    if value == 0:
        # 0 whatever unit is quite undefined... return original unit
        return rescode
    if unit == 'ms' and value >= 1000:
        value /= 1000
        unit = 's'
    if unit == 's' and value % 60 == 0:
        value /= 60
        unit = 'mn'
    if unit == 'mn' and value % 60 == 0:
        value /= 60
        unit = 'h'
    if unit == 'h' and value % 24 == 0:
        value /= 24
        unit = 'd'
    if unit == 'd' and value % 7 == 0:
        value /= 7
        unit = 'w'
    return str(int(value))+unit

def estimate_period_code(start, end):
    # pylint: disable-msg=R0911, R0912
    # R0912: Too many branches
    # R0911: Too many return statements 
    """
    Returns the closest approximation of a periode code.
    e.g.:
    
    Parameters:
        start    datetime start of interval
        end      datetime end of interval
    Returns:
        rescode
        None if difference is < 0.0005 sec
    """
    tot_sec = (end - start).total_seconds()
    
    y_real = tot_sec / (GREGORIAN_DAYS*24*60*60.0)
    y_est = int(round(y_real))
    # if exact y --> return y
    if y_est and \
       abs((end-(start+dateutil.relativedelta.relativedelta(years=y_est)))\
       .total_seconds()) < 1.0:
        return '{}y'.format(y_est)
    # if > 3y --> return rounded y
    if y_est >= 3:
        return '{}y'.format(y_est)
    
    # if exact month --> return mo
    mo_est = int(round(tot_sec / (GREGORIAN_DAYS*24*60*60.0/12.0)))
    if mo_est and \
       abs((end-(start+dateutil.relativedelta.relativedelta(months=mo_est)))\
           .total_seconds()) < 1.0:
        return '{}mo'.format(mo_est)
    
    # if exact week --> return w
    w_real = tot_sec / (7*24*60*60.0)
    w_est = int(round(w_real)) 
    if w_est and abs(tot_sec - w_est * 7*24*60*60.0) < 1.0:
        return '{}w'.format(w_est)
    
    # 2 y +- 3w -> rounded y
    if y_est == 2 and \
       abs((end-(start+dateutil.relativedelta.relativedelta(years=y_est)))\
           .total_seconds()) < (3*7*24*60*60.0):
        return '{}y'.format(y_est)
    # 1 y +- 1w -> rounded y
    if y_est == 1 and \
       abs((end-(start+dateutil.relativedelta.relativedelta(years=y_est)))\
           .total_seconds()) < (7*24*60*60.0):
        return '{}y'.format(y_est)
    
    # if >= 2y --> round mo
    if y_est >= 2:
        return '{}mo'.format(mo_est)

    # mo +-0.5d --> round mo
    if mo_est and \
       abs((end-(start+dateutil.relativedelta.relativedelta(months=mo_est)))\
           .total_seconds()) <= (12*60*60.0):
        return '{}mo'.format(mo_est)

    # w +-0.5d --> round w
    if w_est and abs(tot_sec - w_est * 7*24*60*60) <= (12*60*60.0):
        return '{}w'.format(w_est)

    # mo >= 3 and +-1d --> round mo
    if mo_est >= 3 and \
       abs((end-(start+dateutil.relativedelta.relativedelta(months=mo_est)))\
           .total_seconds()) <= (24*60*60.0):
        return '{}mo'.format(mo_est)

    # w >= 12 and +-1d --> round w
    if w_est >= 12 and abs(tot_sec - w_est * 7*24*60*60) < (24*60*60.0):
        return '{}w'.format(w_est)
    
    # mo >= 3 --> round mo
    if mo_est >= 3:
        return '{}mo'.format(mo_est)
        
    d_real = tot_sec / (24*60*60.0)
    d_est = int(round(d_real))
    # exact d --> return d
    if d_est and abs(tot_sec - d_est * 24*60*60.0) < 1.0:
        return '{}d'.format(d_est)
    
    # w >= 3 and +-2d --> round w
    if w_est >= 3 and abs(tot_sec - w_est * (7*24*60*60.0)) < (2*24*60*60.0):
        return '{}w'.format(w_est)

    # d >= 4 --> return rounded d
    if d_real > 4.0:
        return '{}d'.format(d_est)

    h_real =  tot_sec / (60*60.0)
    h_est = int(round(h_real))
    # h >= 48 --> return rounded h or    
    # h >= 5 +-5mn --> return rounded h
    # h >= 1 +-30sec --> return rounded h
    if h_est >= 24 or \
       (h_est >= 5 and abs(tot_sec - (h_est * (60*60.0))) < 300.0) or \
       (h_est >= 1 and abs(tot_sec - (h_est * (60*60.0))) < 30):
        return '{}h'.format(h_est)

    mn_real =  tot_sec / (60.0)
    mn_est = int(round(mn_real))
    # exact mn --> return mn    
    if mn_est and abs(tot_sec - mn_est * 60.0) < 1.0:
        return '{}mn'.format(mn_est)
    
    # h >= 5 --> return rounded h    
    if h_est >= 5:
        return '{}h'.format(h_est)
    
    # mn +-5s and minute is n/4h --> return mn    
    if mn_est and abs(tot_sec - mn_est * 60) < 5.0 and mn_est % 15 == 0:
        return '{}mn'.format(mn_est)
    
    # h >= 1 --> return rounded h    
    if h_real >= 1.0:
        return '{}h'.format(h_est)
    
    # mn +-5s or minute > 15 -> return mn
    if mn_est and (abs(tot_sec - mn_est * 60) < 5.0 or mn_est > 15):
        return '{}mn'.format(mn_est)
    
    # if >= 0.5, use s
    if tot_sec >= 0.5:
        return "{}s".format(int(round(tot_sec)))

    # if between 0.5 ms and 500 ms: use ms
    if tot_sec >= 0.0005:
        return "{}ms".format(int(round(tot_sec*1000)))

    return None

def estimate_resolution_code(sample_times):
    """
    Calculates a representative resolution code based on sample start/end times.
    The estimate is in most cases the median of all start time differences in
    data. See implementation of modified_median for details.
    Parameters:
        sample_times   list of tuples [(start, end),...]
    Returns:
        representative resolution code (e.g. 2h)
        None if undefined (e.g. only one sample or any sample time is None)
    """
    if len(sample_times) > 1:
        try:
            med_res = modified_median([diff[1][0] - diff[0][0] for diff in \
                        zip(sample_times[:-1], sample_times[1:])])
        except TypeError:
            # most likely one time is None...
            return None
        res_sec = med_res.total_seconds()
        res_cde = estimate_period_code(datetime.datetime(1900, 1, 1), \
            datetime.datetime(1900, 1, 1) + med_res)
        return res_cde
    return None

def estimate_sample_duration_code(sample_times):
    """
    Calculates a representative sample duration code based on sample start/end
    times.
    The estimate is in most cases the median duration in data. See
    implementation of modified_median for details.
    Parameters:
        sample_times   list of tuples [(start, end),...]
    Returns:
        representative sample duration code (e.g. 2h)
        None if undefined (e.g. only one sample or any sample time is None)
    """
    if len(sample_times) > 0:
        try:
            med_dur = modified_median([samp[1] - samp[0]
                              for samp in sample_times])
        except TypeError:
            # most likely one time is None...
            return None
        dur_sec = med_dur.total_seconds()
        return estimate_period_code(datetime.datetime(1900, 1, 1), \
            datetime.datetime(1900, 1, 1) + med_dur)
    return None
