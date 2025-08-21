"""
nilutility/statistics.py
$Id: statistics.py 2556 2020-12-02 20:12:20Z pe $

Basic statistics routines.
"""

import math
from nilutility.ndecimal import Decimal
from bisect import insort, bisect_left
from collections import deque, defaultdict

def median(lst, is_sorted=False, contains_none=True):
    """
    Calculates the median of a list of values.
    Parameters:
        lst         list of values
        is_sorted   bool, speed up the calculation if the list is already sorted
        contains_none
                    bool, speed up the calculation if the list does not contain
                    Nones
    Returns:
        median value
    """
    if contains_none:
        lst = [x for x in lst if x is not None]
    if not is_sorted:
        lst = sorted(lst)
    # do not check is_sorted or contains_none:
    #  this would be a performace killer (ca. factor 1000 for contains_None)
    #  is_sorted would be even more expansive to check
    return _median_fast(lst)

def _median_fast(lst):
    """
    A raw and fast version of calculating the median if one can guarantee that
    the list is sorted and there aer no None's in the list.
    !!! Fast version, list must be sorted and may not contain None values!
    For unsorted lists or lists containing None's use median()
    Parameters:
        lst   list of values
    Returns:
        median of values, None in case of empty list
    """
    len_ = len(lst)
    if len_ == 0:
        # empty list, no median
        return None
    if len_ % 2:
        return lst[len_//2]
    try:
        ret = (lst[len_//2-1] + lst[len_//2]) / 2.0
    except TypeError:
        # in case where /2.0 is not allowed (e.g. datetime.timedelta)
        ret = (lst[len_//2-1] + lst[len_//2]) / 2
    return ret

def modified_median(lst, **kwargs):
    """
    This is a modified median. If less then 75% of th evalues are the same
    but still the most abundant 2 different values make at least 90%:
    use the arithmetic mean of those two elements.
    In all other cases, the median is returned.
    
    Parameters:
        lst        list of values
        **kwargs   keyword arguments to be passed to the fallback median method

    Used to find a representative value for the time resolution of time series.
    Before, we used the median (if majority of the samples are 1h, use 1h even
    though there are some outliers...)
    This modified median tackles the followong edge case:
    Samples taken at 3+4 days interval. The median returns 3 if the series
    starts with 3d and ends with 3 h. It returns 4d if the sequence starts with
    4d and ends with 4d. And it resturn 3.5d (84h) if there is the same number
    of both.
    """
    if len(lst) > 3:
        histo = defaultdict(int)
        for elem in lst:
            histo[elem] += 1
        res = sorted(histo.items(), key=lambda x: x[1], reverse=True)
        # how many of the most abundant value?
        if res[0][1] >= len(lst)*0.75:
            # >= 75% og all values are the same
            return res[0][0]
        if res[0][1] + res[1][1] >= len(lst)*0.9:
            # >= 90% of all values are the most abundant 2)
            return (res[0][0] + res[1][0]) / 2
    # else return median
    return median(lst, **kwargs)

def running_median(lst, radius):
    """
    Running median. The running median for an element n is the median of element
    n and radius elements before and after (Window size = 2 * radius + 1).
    For the first (and last) n elements, the number of elements before (after)
    is iof course shorter then n.

    Parameters:
        lst    list of values
        radius the radius (how many elements left and right on an element n
               should be included).
    Returns:
        list with running medians.

    Highly performant implementation, especially with bigger window sizes about
    100-1000 times faster than more naive approaches.
    Makes use of the fact that only 2 elements are changed within the window for
    each iteration.

    Performance of different approches has been tested in a small test setup:
    https://git.nilu.no/ebas/scripts/test/blob/master/running_median_test.py
    The bigger the used window sizes, the clearer the advantages of this
    implementation is visible.

    A double-ended queue (deque; with fast append and pop on both sides) is used
    to keep track of the current window. In parallel a list of the window
    elements is always kept sorted, using the highly performant bisect methods
    (insort, bisect_left) to maintain the sorted list.
    """
    result = []
    # Initial window: n elements right of the value plus the value itself (=n+1
    # values).
    # We preload the window with n values. in the first iteration + 1 value
    # is added
    deq_win = deque(lst[0:radius])  # The window as double ended queue
    # The window as sorted list:
    srt_win = sorted([x for x in deq_win if x is not None])
    for item in lst[radius:]:
        # Iterate through elements from radius to the end
        # Item is the rightmost element to be appended to the window:
        deq_win.append(item)
        if item is not None:
            insort(srt_win, item)
        # Delete one element if the window size is exceeded:
        if len(deq_win) > 2 * radius + 1:
            tbd = deq_win.popleft()  # item to be deleted
            if tbd is not None:
                del srt_win[bisect_left(srt_win, tbd)]
        # Calculate and append the median value:
        # (we know the window is sorted and contains no None values, use
        # _median_fast directly)
        result.append(_median_fast(srt_win))
    # Process the final elements (no new values, but pop values from the
    # left of the window.
    # Usually this is radius iterations, but specail case when list size <
    # rarius.
    for i in range(len(lst) - len(result)):
        # with list much longer then radius, we would just unconditionally pop
        # one element per loop. But when list length < 2*r+1 (i.e. full window
        # size is never reached), we pop elements too early for the last r
        # elements. Thus we depend on i:.
        # Example: [1., 2., 3., 4.], radius = 2
        if len(deq_win) > 2 * radius - i:
            tbd = deq_win.popleft()  # item to be deleted
            if tbd is not None:
                del srt_win[bisect_left(srt_win, tbd)]
        # Calculate and append the median value:
        # (we know the window is sorted and contains no None values, use
        # _median_fast directly)
        result.append(_median_fast(srt_win))
    return result

def stddev(lst, contains_none=True):
    """
    Calculates the stddev of a list of values.
    stddev of a sample of a population (i.e. df = n-1).
    Parameters:
        lst         list of values
        contains_none
                    bool, speed up the calculation if the list does not contain
                    Nones
    Returns:
        stddev value
    """
    if contains_none:
        lst = [x for x in lst if x is not None]
    return _stddev_fast(lst)

def _stddev_fast(lst):
    """
    A raw and fast version of calculating the stddev of a list of values (stddev
    of a sample of a population (i.e. df = n-1)).
    !!! Fast version, list must not contain None values!
    For lists containing None's use stddev()
    Parameters:
        lst   list of values (may not contain None's)
    Returns:
        stddev value
    """
    if len(lst) < 2:
        return None
    mean = sum(lst)/float(len(lst))
    return math.sqrt(sum([(x-mean)**2 for x in lst])/float(len(lst)-1.0))

def running_stddev(lst, radius):
    """
    Running stddev. The running stddev for an element n is the stddev of element
    n and radius elements before and after (Window size = 2 * radius + 1).
    For the first (and last) n elements, the number of elements before (after)
    is of course shorter then n.

    Parameters:
        lst    list of values
        radius the radius (how many elements left and right on an element n
               should be included).
    Returns:
        list with running stddev.

    A double-ended queue (deque; with fast append and pop on both sides) is used
    to keep track of the current window.

    Welford's a algorithm (streaming calculation) is used to improve
    performance (see class StddevWeford).
    """
    result = []
    # Initial window: n elements right of the value plus the value itself (=n+1
    # values).
    # We preload the welford object with n values. in the first iteration + 1
    # value is added
    welford = StddevWelford()
    for item in lst[0:radius]:
        welford.push(item)

    for item in lst[radius:]:
        # Iterate through elements from radius to the end
        # Item is the rightmost element to be appended to the window:
        welford.push(item)
        # Delete one element if the window size is exceeded:
        if len(welford.data) > 2 * radius + 1:
            welford.pop()
        # Calculate and append the stddev value:
        # (we know the window contains no None values, use
        # _stddev_fast directly)
        result.append(welford.stddev)
    # Process the final elements (no new values, but pop values from the
    # left of the window.
    # Usually this is radius iterations, but specail case when list size <
    # rarius.
    for i in range(len(lst) - len(result)):
        # with list much longer then radius, we would just unconditionally pop
        # one element per loop. But when list length < 2*r+1 (i.e. full window
        # size is never reached), we pop elements too early for the last r
        # elements. Thus we depend on i:.
        # Example: [1., 2., 3., 4.], radius = 2
        if len(welford.data) > 2 * radius - i:
            welford.pop()
        # Calculate and append the stddev value:
        # (we know the window is sorted and contains no None values, use
        # _stddev_fast directly)
        result.append(welford.stddev)
    return result

class StddevWelford(object):
    """
    Implementation of Welford's algorithm for calculating the stddev.
    This is a numerically quite stable version according to
    https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm

    Added the pop method for removing elements: pop is implemented trivially
    as the opposite of push.

    The Welford algorithm is likely slower for calculating a single stddev.
    But it can calculate streaming data (no need to store all data at once), and
    it has a husge performance advantage for calculating a running stddev (see
    methon running_stddev above).
    """
    def __init__(self):
        """
        Set up the object.
        """
        # sum of the squares of the diffs from mean:
        self.sum_squ_diff_mean = 0.0
        self.data = deque([])
        self.count = 0
        self.mean = 0.0

    def push(self, value):
        """
        Append a value to the end of the list of data.
        """
        self.data.append(value)
        if value is not None:
            self.count += 1
            delta = value - self.mean
            self.mean += delta / self.count
            self.sum_squ_diff_mean += delta * (value - self.mean)

    def pop(self):
        """
        Pop one value from the beginning of the list of data.
        """
        if len(self.data) == 1:
            self.__init__()
        value = self.data.popleft()
        if value is not None:
            self.count -= 1
            delta = value - self.mean
            self.mean -= delta / self.count
            self.sum_squ_diff_mean -= delta * (value - self.mean)

    @property
    def stddev(self):
        """
        Get the resulting stddev.
        """
        if self.count < 2:
            return None
        return math.sqrt(self.sum_squ_diff_mean/float(self.count-1.0))


def percentile(lst, perc, is_sorted=False, contains_none=True):
    """
    A raw and fast version of calculating a percentile of a list of values.
    Parameters:
        lst         list of values. MUST BE already sorted.
                    either float or Decimal, but NOT MIXED!
        perc        percentile to be calculated float 0.0 - 100.0.
        is_sorted   bool, speed up the calculation if the list is already sorted
        contains_none
                    bool, speed up the calculation if the list does not contain
                    Nones
    Returns:
        the percentile of the values
    """
    if contains_none:
        lst = [x for x in lst if x is not None]
    if not is_sorted:
        lst = sorted(lst)
    return _percentile_fast(lst, perc)

def _percentile_fast(lst, perc):
    """
    A raw and fast version of calculating a percentile of a list of values.
    !!! Fast version, list must be sorted!
    For unsorted lists use stddev()
    Parameters:
        lst    list of values. MUST BE already sorted.
               either float or Decimal, but NOT MIXED!
        perc   percentile to be calculated float 0.0 - 100.0.
    Returns:
        the percentile of the values
    """
    if len(lst) == 0:  # pylint: disable=C1801
        # C1801: Do not use `len(SEQUENCE)` to determine if a sequence is  empty
        # --> want to raise TypeError on not sequence objects, e.g. False, None)
        return None

    # float index for the percentile value:
    index = (len(lst)-1) * perc / 100.0
    floor = math.floor(index)
    ceil = math.ceil(index)

    if floor == ceil:
        # index is integer
        return lst[int(index)]
    # else, return the weighed average of the two elements (weighed by distance)
    if isinstance(lst[0], Decimal):
        # special case for Decimal: can only be multiplied by a Decimal
        return lst[int(floor)] * Decimal(ceil-index) + \
               lst[int(ceil)] * Decimal(index-floor)
    return lst[int(floor)] * (ceil-index) + \
           lst[int(ceil)] * (index-floor)
