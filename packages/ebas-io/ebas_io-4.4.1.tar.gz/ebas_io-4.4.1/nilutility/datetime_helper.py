"""
nilu/datetime_helper.py
$Id: datetime_helper.py 2686 2021-08-18 11:24:59Z pe $

Module for helper functions for date/time handling.
Provides classes for DateTime intervals and sets of intervals.

History:
V.1.0.0  2012-10-05  pe  initial version
V.2.0.0  2016-12-08  pe  rewritten, created classes

"""

import datetime
import re
import math
from dateutil.relativedelta import relativedelta

class DatetimeInterval(list):
    """
    Time interval class.

    Description of time intervals:
     - Generally, an interval has a start and an end time.
     - Start or End can be None which means + and - infinity, e.g.
       [None, 2014-01-01] is all times before and including
       2014-01-01T00:00:00.000.
     - None is interpreted as empty interval []
     - intervals must be positive (start<end for () and [) intervals,
       start<=end for [] intervals)
    """

    def __init__(self, start, end, empty=False, bounds='[)'):
        """
        Initialize a time interval
        """
        self.bounds = bounds
        if empty:
            # initialize the list:
            super(DatetimeInterval, self).__init__([])
            self.bounds = ''
            return
        # initialize the list:
        super(DatetimeInterval, self).__init__((start, end))
        # ignore and hard reset open bounds for infinity:
        if start is None:
            self.bounds = '(' + self.bounds[1]
        if end is None:
            self.bounds = self.bounds[0] + ')'
        self.check()

    def __str__(self):
        """
        Create a pretty string.
        """
        if self.is_empty():
            return self.bounds
        ret = ['-Inf', 'Inf']
        if self[0]:
            ret[0] = datetime_string(self[0])
        if self[1]:
            ret[1] = datetime_string(self[1])
        return "{}{}, {}{}".format(self.bounds[0], ret[0], ret[1], self.bounds[1])

    def __repr__(self):
        """
        Use the same es str?
        """
        return str(self)

    def __eq__(self, other):
        """
        Check for equality.
        """
        return self.cmp(other) == 0
        
    def __ne__(self, other):
        """
        Check for inequality.
        """
        return self.cmp(other) != 0
        
    def __lt__(self, other):
        """
        Check if less than.
        """
        return self.cmp(other) < 0
        
    def __le__(self, other):
        """
        Check if less or equal.
        """
        return self.cmp(other) <= 0
        
    def __gt__(self, other):
        """
        Check if greater than.
        """
        return self.cmp(other) > 0
        
    def __ge__(self, other):
        """
        Check if greater or equal.
        """
        return self.cmp(other) >= 0

    def __hash__(self):
        """
        Hash value for object
        """
        return hash(tuple(self) + (self.bounds,))

    def cmp(self, other):
        """
        Compare two objects
        """
        if self.is_empty() and other.is_empty():
            return 0
        if self.is_empty():
            return -1
        if other.is_empty():
            return 1

        if (self[0] is None and other[0] is not None) or \
                (self[0] is not None and other[0] is not None and \
                 self[0] < other[0]):
            return -1
        if (other[0] is None and self[0] is not None) or \
                (self[0] is not None and other[0] is not None and \
                 self[0] > other[0]):
            return 1
        # here the start values are equal (either both None or both the same date)
        if self.bounds[0] == '[' and other.bounds[0] == '(':
            return -1
        if self.bounds[0] == '(' and other.bounds[0] == ']':
            return 1
        # here they have equal start (also bound)
        if (self[1] is None and other[1] is not None) or \
                (self[1] is not None and other[1] is not None and \
                 self[1] > other[1]):
            return 1
        if (other[1] is None and self[1] is not None) or \
                (self[1] is not None and other[1] is not None and \
                 self[1] < other[1]):
            return -1
        # end values are also equal
        if self.bounds[1] == ')' and other.bounds[1] == ']':
            return -1
        if self.bounds[1] == ']' and other.bounds[1] == ')':
            return 1
        return 0

    @classmethod
    def empty(cls):
        """
        Create an empty interval.
        """
        return DatetimeInterval(None, None, empty=True)

    def is_empty(self):
        """
        An empty interval is one with zero length!
        """
        return not bool(self)

    def is_unbound(self):
        """
        Is unbound at both ends.
        """
        if not self:
            return False
        if self[0] is None and self[1] is None:
            return True
        return False

    def clone(self):
        """
        Clones the interval. Factory of DatetimeInterval.
        Parameters:
            None
        Returns:
            copy of self
        """
        if self.is_empty():
            return self.empty()
        return DatetimeInterval(*self, bounds=self.bounds)

    def check(self):
        """
        Check an interval.
        Parameters:
            interval    time interval to be checked
        Returns:
            None
        Raises:
            TypeError, ValueError
        """
        if self.is_empty():
            return
        if self.bounds not in ('[]', '[)', '(]', '()'):
            raise ValueError('illegal interval bounds {}'.format(self.bounds))
        intv = list(self)  # raises TypeError if it cannot be converted
        if len(intv) != 2:
            raise ValueError('illegal time interval')
        for tim in intv:
            if tim is not None and not isinstance(tim, datetime.datetime):
                raise TypeError('time interval limits must be None or '
                                'datetime.datetime')
        if intv[0] is not None and intv[1] is not None:
            if (self.bounds[0] == '(' or self.bounds[1] == ')') and \
                    intv[0] >= intv[1]:
                raise ValueError(
                    'time interval start must be earlier then time interval '
                    'end for open and half-open intervals')
            elif intv[0] > intv[1]:
                raise ValueError(
                    'time interval start must be earlier or equal time '
                    'interval end for closed intervals')

    def overlap(self, interval2):
        """
        Checks intervals for overlap.
        Returns overlaping time interval (intersection).

        Parameters:
            interval2   interval to overlap self wdith
        Returns:
            DatetimeInterval (overlapping interval)
            None if no overlap
        """
        if self.is_empty() or interval2.is_empty():
            # empty intervals cannot overlap with anything
            return DatetimeInterval.empty()
        if (not self[0] or not interval2[1] or \
            (self.bounds[0] == '[' and interval2.bounds[1] == ']' and \
             self[0] <= interval2[1]) or \
            self[0] < interval2[1]) and \
           (not self[1] or not interval2[0] or \
            (self.bounds[1] == ']' and interval2.bounds[0] == '[' and \
             self[1] >= interval2[0]) or \
            self[1] > interval2[0]):
            if self[0] is None:
                if interval2[0] is None:
                    low = None
                    lowbnd = '('
                else:
                    low = interval2[0]
                    lowbnd = interval2.bounds[0]
            elif interval2[0] is None:
                low = self[0]
                lowbnd = self.bounds[0]
            elif self[0] > interval2[0]:
                low = self[0]
                lowbnd = self.bounds[0]
            elif self[0] < interval2[0]:
                low = interval2[0]
                lowbnd = interval2.bounds[0]
            else:
                # equal
                low = self[0]
                lowbnd = self.bounds[0] if interval2.bounds[0] == '[' else '('

            if self[1] is None:
                if interval2[1] is None:
                    upp = None
                    uppbnd = ')'
                else:
                    upp = interval2[1]
                    uppbnd = interval2.bounds[1]
            elif interval2[1] is None:
                upp = self[1]
                uppbnd = self.bounds[1]
            elif self[1] < interval2[1]:
                upp = self[1]
                uppbnd = self.bounds[1]
            elif self[1] > interval2[1]:
                upp = interval2[1]
                uppbnd = interval2.bounds[1]
            else:
                # equal
                upp = interval2[1]
                uppbnd = self.bounds[1] if interval2.bounds == ']' else ')'
            return DatetimeInterval(low, upp, bounds=lowbnd+uppbnd)
        else:
            return DatetimeInterval.empty()

    def contains_timestamp(self, dtime):
        """
        Checks if timestamp is contained in interval.
        Parameters:
            dtime    datetime.datetime (contained in me?)
                     if None we assume unlimited end of interval.
        Returns:
            bool
        """
        if self.is_empty():
            return False
        if ((dtime is None and self[1] is None) or
            (dtime is not None and
             (self[0] is None or self[0] <= dtime) and
             (self[1] is None or self[1] > dtime))):
            return True
        return False

    def contains(self, other):
        """
        Checks if other interval is contained in interval.
        (Fully contained, otherwise it would be an overlap).
        Parameters:
            other    other interval (contained in me?)
        Returns:
            bool
        """
        if self.is_empty() or other.is_empty():
            # empty intervals cannot contain or be contained
            return False
        # check lower limit: if...
        #  both are numbers and other not fully in self OR
        #  both are numbers and equal and
        #      self is open and other is closed OR
        #  other[0] is infinite and self[0] is not infinite OR
        #  other[0] is infinite and self[0] is infinite and
        #      self is open and other is closed
        if self[0] and other[0] and self[0] > other[0] or \
           self[0] and other[0] and self[0] == other[0] and \
               self.bounds[0] == '(' and other.bounds == '[' or \
           not other[0] and self[0] or \
           not other[0] and not self[0] and \
               self.bounds[0] == '(' and other.bounds == '[':
            return False
        # check upper limit: if...
        #  both are numbers and other not fully in self OR
        #  both are numbers and equal and
        #      self is open and other is closed OR
        #  other[1] is infinite and self[1] is not infinite OR
        #  other[1] is infinite and self[1] is infinite and
        #      self is open and other is closed
        if self[1] and other[1] and self[1] < other[1] or \
           self[1] and other[1] and self[1] == other[1] and \
               self.bounds[1] == ')' and other.bounds == ']' or \
           not other[1] and self[1] or \
           not other[1] and not self[1] and \
               self.bounds[1] == ')' and other.bounds == ']':
            return False
        # else, other is contained in self
        return True

    def distance(self, interval2):
        """
        Calculates the distance (in seconds).
        0.0 is either overlap (contains) or adjoins.
        """
        if self.overlap(interval2) or self.adjoins(interval2):
            return 0.0
        if self[0] is not None and interval2[1] is not None and (self[0]-interval2[1]).total_seconds() > 0.0:
            return (self[0]-interval2[1]).total_seconds()
        if self[1] is not None and interval2[0] is not None and (interval2[0]-self[1]).total_seconds() > 0.0:
            return (interval2[0]-self[1]).total_seconds()

    def subtract(self, interval2):
        # pylint: disable=R0912, W1401
        #  R0912: Too many branches
        """
        Subtracts interval2 from self.
        (in set theory: relative complement of interval2 in self:
        self \\ interval2)

        Parameters:
            interval2   interval to subtract from self
        Returns:
            DatetimeIntervalSet   resulting interval(s) (can be empty)
        """
        # pylint: enable=W1401
        ret = DatetimeIntervalSet()
        if self.is_empty():
            # nothing to subtract from
            return ret
        if not self.overlap(interval2):
            # nothing to subtract
            ret.add(self.clone())
            return ret
        if (self[0] is None and (interval2[0] is not None or
                                 (self.bounds[0] == '[' and
                                  interval2.bounds[0] == '('))) or \
           (self[0] is not None and interval2[0] is not None and
            (self[0] < interval2[0] or (self[0] == interval2[0] and
                                        self.bounds[0] == '[' and
                                        interval2.bounds[0] == '('))):
            # There is a part extending at the beginning of self
            ret.add(DatetimeInterval(
                self[0], interval2[0],
                bounds=self.bounds[0] + (']' if interval2.bounds[0] == '('
                                         else ')')))

        if (self[1] is None and (interval2[1] is not None or
                                 (self.bounds[1] == ']' and 
                                  interval2.bounds[1] == ')'))) or \
           (self[1] is not None and interval2[1] is not None and
            (self[1] > interval2[1] or (self[1] == interval2[1] and
                                        self.bounds[1] == ']' and
                                        interval2.bounds[1] == ')'))):
            # There is something extending at the end of self
            ret.add(DatetimeInterval(
                interval2[1], self[1],
                bounds=('[' if interval2.bounds[1] == ')' else '(') + \
                    self.bounds[1]))        
        return ret

    def adjoins_right(self, interval2):
        """
        Checks if interval2 adjoins self to the right.
        Parameters:
            interval2   second interval
        Returns:
            True / False
        """
        if self.is_empty() or interval2 is None or interval2.is_empty():
            return False  # empty intervals can not adjoin to anything
        return bool(self[1] == interval2[0] and
                    ((self.bounds[1] == ')' and interval2.bounds[0] == '[') or
                     (self.bounds[1] == ']' and interval2.bounds[0] == '(')))

    def adjoins_left(self, interval2):
        """
        Checks if interval2 adjoins self to the left.
        Parameters:
            interval2   second interval
        Returns:
            True / False
        """
        if self.is_empty() or interval2 is None or interval2.is_empty():
            return False  # empty intervals can not adjoin to anything
        return bool(self[0] == interval2[1] and
                    ((self.bounds[0] == '[' and interval2.bounds[1] == ')') or
                     (self.bounds[0] == '(' and interval2.bounds[1] == ']')))

    def adjoins(self, interval2):
        """
        Checks if interval2 adjoins self to the left or right.
        Parameters:
            interval2   second interval
        Returns:
            True / False
        """
        return self.adjoins_left(interval2) or self.adjoins_right(interval2)

class DatetimeIntervalSet(list):
    """
    Set of DateTime Intervals.
    """

    def __init__(self, initintv=None):
        """
        Initialize a time interval
        Parameters:
            initintv   initial interval to be added righrt away
        """
        # initialize the list:
        super(DatetimeIntervalSet, self).__init__([])
        if initintv:
            self.add(initintv)

    def clone(self):
        """
        Clones the interval set.
        Parameters:
            None
        Returns:
            cloned object
        """
        ret =DatetimeIntervalSet()
        for intv in self:
            ret.add(intv.clone())
        return ret

    def union(self, interval):
        """
        Calculate the union of interval set with an interval or another interval
        set.
        Like add, but returns the union instead of changing the object.

        Parameters:
            interval    DatetimeInterval or DatetimeIntervalSet to be unioned
        Returns:
            union (DatetimeIntervalSet)
        """
        ret = self.clone()
        ret.add(interval)
        return ret
        
    def add(self, interval):
        # pylint: disable=R0912
        #  R0912: Too many branches
        """
        Adds interval or interval set to the interval set.
        Like union, but changes the object instead of returning the result.

        Parameters:
            interval    DatetimeInterval or DatetimeIntervalSet to be added
        Returns:
            None
        """
        if isinstance(interval, DatetimeInterval):
            self._add_interval(interval)
        else:
            for intv in interval:
                self._add_interval(intv)

    def _add_interval(self, interval):
        # pylint: disable=R0912
        #  R0912: Too many branches
        """
        Adds interval2 to the interval set.

        Parameters:
            interval    DatetimeInterval to be added
        Returns:
            None
        """
        if not interval:
            return  # empty interval, nothing to add
        added = False
        i = 0
        while i < len(self):
            # check overlap/adjoin with interval
            if (self[i][0] is None or interval[1] is None or \
                self[i][0] <= interval[1]) and \
               (self[i][1] is None or interval[0] is None or \
                self[i][1] >= interval[0]):
                # element i overlaps with or adjoins interval: merge them:
                if self[i][0] is None or interval[0] is None:
                    self[i][0] = None
                else:
                    self[i][0] = min(self[i][0], interval[0])
                if self[i][1] is None or interval[1] is None:
                    self[i][1] = None
                else:
                    self[i][1] = max(self[i][1], interval[1])
                added = True
            # check overlap/adjoin with any other list element:
            j = i + 1
            while j < len(self):
                if (self[i][0] is None or self[j][1] is None or \
                    self[i][0] <= self[j][1]) and \
                   (self[i][1] is None or self[j][0] is None or \
                    self[i][1] >= self[j][0]):
                    # element i overlaps or adjoins element j:
                    # merge them and del j
                    if self[i][0] is None or self[j][0] is None:
                        self[i][0] = None
                    else:
                        self[i][0] = min(self[i][0], self[j][0])
                    if self[i][1] is None or self[j][1] is None:
                        self[i][1] = None
                    else:
                        self[i][1] = max(self[i][1], self[j][1])
                    del self[j]
                    # do not increment
                else:
                    j += 1
            i += 1
        if not added:
            self.append(interval.clone())
        self.sort(
            key=lambda x: [datetime.datetime.min if x[0] is None else x[0],
                           0 if x.bounds[0] == '[' else 1,
                           datetime.datetime.max if x[1] is None else x[1],
                           0 if x.bounds[0] == ')' else 1])

    def difference(self, interval):
        """
        Calculates the (set) difference of an interval set and an interval or
        another interval set.
        Like subtract, but returns the difference instead of changing the
        object.

        Parameters:
            interval  DatetimeInterval or DatetimeIntervalSet to be differenced
        Returns:
            None
        """
        if isinstance(interval, DatetimeInterval):
            return self._difference_interval(interval)
        else:
            ret = None
            for intv in interval:
                if not ret:
                    ret = self._difference_interval(intv)
                else:
                    ret = ret._difference_interval(intv)
                if not ret:
                    return ret

    def _difference_interval(self, interval):
        """
        Calculates the (set) difference of an interval set and an interval.

        Parameters:
            interval    DatetimeInterval to be differenced
        Returns:
            difference (DattimeIntervalSet)
        """
        ret= DatetimeIntervalSet()
        for intv in self:
            remain = intv.subtract(interval)
            if remain:
                ret.extend(remain)
        ret.sort()
        return ret

    def subtract(self, interval):
        """
        Subtracts an interval from the interval set.
        Like difference, but changes the object instead of returning the result.

        Parameters:
            interval    DatetimeInterval or DatetimeIntervalSet to be subtracted
        Returns:
            None
        """
        new = self.difference(interval)
        del self[:]
        self.extend(new)

    def intersection(self, interval):
        """
        Calculates the intersection of an interval set and and interval or
        another interval set.

        Parameters:
            interval   DatetimeInterval or DatetimeIntervalSet to be intersected
        Returns:
            None
        """
        ret = DatetimeIntervalSet()
        if isinstance(interval, DatetimeInterval):
            interval = [interval]
        for int1 in interval:
            for int2 in self:
                overlap = int1.overlap(int2)
                if overlap:
                    ret.add(overlap)
        return ret

    def overlap(self, interval):
        """
        Overlaps the interval set with an interval or another interval set.
        Like intersection, but changes the object instead of returning the
        result.

        Parameters:
            interval    DatetimeInterval or DatetimeIntervalSet to be overlapped
        Returns:
            None
        """
        new = self.intersection(interval)
        del self[:]
        self.extend(new)

def datetime_string(dtt):
    """
    Convert datetime object to a pretty string. Use precision according to
    content.
    Parameters:
        dtt    datetime object
    Returns:
        stting ipretty formatted datetime or "None"
    """
    if not dtt:
        return "None"
    fmt = '%Y-%m-%d'
    if dtt.microsecond:
        fmt += 'T%H:%M:%S.%f'
    elif dtt.second:
        fmt += 'T%H:%M:%S'
    elif dtt.minute or dtt.hour:
        fmt += 'T%H:%M'
    return dtt.strftime(fmt)

def datetime_round(datetime_, sec_digits):
    """
    Rounds a datatime.datetime object.
    Parameters:
        datetime_    datetime.datetime object
        sec_digits   digits of a second:
                       e.g.: 3: round to milliseconds
                       e.g.: 0: round to seconds
    Returns:
        datetime.datetime (must return new value, datetime is immutable)
    """
    seconds = datetime_.second + datetime_.microsecond / 1000000.0
    rounded = round(seconds, sec_digits)
    return datetime_ + datetime.timedelta(seconds=rounded-seconds)

def datetime_parse_iso8601(string):
    """
    Parses a single time string and returns a datetime.datetime object.

    Parameters:
        string    time string
    Returns:
        datetime
    Raises:
        ValueError in case of parsing errors

    TODO: support for optional timezones, week number syntax, ordinal day syntax
    """
    # check base ISO format syntax
    if not re.match('[0-9][0-9][0-9][0-9](-[0-9][0-9](-[0-9][0-9]' + \
       r'(T[0-9][0-9](:[0-9][0-9](:[0-9][0-9](\.[0-9]+)?)?)?)?)?)?$', string):
        raise ValueError('illegal ISO8601 time: ' + string)

    if len(string) > 20:
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
    elif len(string) < 4:
        fmt = '%Y'
    else:
        fmt = "%Y-%m-%dT%H:%M:%S."[0:len(string)-2]
    try:
        return datetime.datetime.strptime(string, fmt)
    except ValueError:
        raise ValueError('illegal ISO8601 time: ' + string)

class DatetimeISO8601Duration(object):
    """
    Class for handling durations in all units (i.e. years, months, ...).
    In contrast, the datetime.timedelta only handles days, seconds and
    milliseconds. Which means the duration has always a definded extent in
    seconds.

    Here the arithmetic is completely different: A duration of a year can
    be 365 days, 366 days, even with 2 leap seconds included... Depends on the
    reference date the duration is applied.
    """

    def __init__(self):
        """
        Set up object object.
        """
        self.positive = True
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.microsecond = 0

    def diff(self, time1, time2):
        """
        Calculates the ISO 8601 duration from the difference of two timestamps.
        Parameters:
            time1   timestam 1 (earlier)
            time2   timestamp 2 (later)
        Returns:
            None
        """
        if time2 < time1:
            self.positive = False
            hlp = time1
            time1 = time2
            time2 = hlp

        # Years
        offset = 0
        if time2.year > time1.year:
            for offset in (time2.year-time1.year, time2.year-time1.year-1):
                test = time1 + relativedelta(years=offset)
                # use relativedelta (replace year crashes on leap days!)
                if test <= time2:
                    time1 = test
                    break
        self.year = offset

        # Months
        offset = 0
        max_ = int(math.ceil((time2-time1).total_seconds()/60.0/60.0/24.0/28.0))
        min_ = math.trunc((time2-time1).total_seconds()/60.0/60.0/24.0/31.0)
        # min and max will always be different, except time1==time2
        for offset in reversed(list(range(min_, max_ + 1))):
            test = time1 + relativedelta(months=offset)
                # use relativedelta (replace year crashes on leap days!)
            if test <= time2:
                time1 = test
                break
        self.month = offset

        # Days
        offset = (time2-time1).days
        time1 = time1 + datetime.timedelta(days=offset)
        self.day = offset

        # Hours
        totalsec = (time2-time1).total_seconds()
        offset, totalsec = divmod(totalsec, 3600)
        self.hour = int(offset)
        # Minutes
        offset, totalsec = divmod(totalsec, 60)
        self.minute = int(offset)
        # Seconds
        offset, totalsec = divmod(totalsec, 1)
        self.second = int(offset)
        # Microseconds
        if totalsec != 0.0:
            self.microsecond = int(totalsec * 1000000 + 0.5)

    def format(self, fmt=1):
        """
        Return the formated output for the object.
        Parameters:
            fmt      format specification according to ISO8601:
                      1: standard format, e.g. P3Y6M4DT12H30M5S
                      2: alternative extended format, e.g. P0003-06-04T12:30:05
                      3: alternative shortened format, e.g. P00030604123005
        Returns:
            formatted string
        """
        if fmt == 1:
            #standard format:
            res = "P"
            if not self.positive:
                res += "-"
            if self.year:
                res += "{}Y".format(self.year)
            if self.month:
                res += "{}M".format(self.month)
            if self.day:
                res += "{}D".format(self.day)
            if self.hour or self.minute or self.second or self.microsecond:
                res += "T"
            if self.hour:
                res += "{}H".format(self.hour)
            if self.minute:
                res += "{}M".format(self.minute)
            if self.microsecond:
                res += "{}S".format(self.second+self.microsecond/1000000.0)
            elif self.second:
                res += "{}s".format(self.second)
            if res == "P":
                # nothing set yet
                res += "T0S"
            return res
        if fmt == 2:
            # alternative extended format (with -, T and :)
            res = "P{}{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
                "" if self.positive else "-", self.year, self.month, self.day,
                self.hour, self.minute, self.second)
            if self.microsecond:
                res += ".{:06d}".format(self.microsecond)
            return res
        if fmt == 3:
            # alternative shortened format (without -, T and :)
            res = "P{}{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(
                "" if self.positive else "-", self.year, self.month, self.day,
                self.hour, self.minute, self.second)
            if self.microsecond:
                res += ".{:6d}".format(self.microsecond)
            return res
