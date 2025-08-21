"""
ebas/domain/base.py
$Id: base.py 2561 2020-12-07 23:09:30Z pe $

Base Classes for EBAS domain layer (entity objects)

History:
V.1.0.0  2012-10-14  pe  initial version

"""

from nilutility.datatypes import DataObject
from nilutility.datetime_helper import DatetimeInterval

# exceptions used in the domain module
class EbasDomainError(Exception):
    """
    Base class for exceptions.
    """
    pass


class EbasDomainObjCache(DataObject):
    """
    Object cache for domain objects (SU and DS).
    This mechanism is needed to avoid recursion in HDI objects.
    """
    def __init__(self):
        DataObject.__init__(self)

    def clear(self):
        """
        Clear all caches.
        Parameters:
            None
        Returns:
            None
        """
        for ele in list(self.keys()):
            self[ele] = []
            del self[ele]


class EbasDomainDbContext(DataObject):
    """
    Database Context for Ebas Domain Objects.
    """

    def __init__(self, dbh=None, time=DatetimeInterval(None, None), us_id=None,
                 export_filter=0,
                 state=None, diff=None, diff_ctx=None, cache=None):
        # pylint: disable-msg=R0913
        # R0913: Too many arguments
        """
        Initialize DB Context.
        Parameters:
            dbh     database handle (ebas.db layer)
            time    time interval for the context (only work on metadata and
                    date within this interval)
                    tuple (start, end), both datetime.datetime or None (+- inf)
            us_id   user id for access (access restrictions)
            export_filter
                    filter option for export of data from db to domain
                    bitfield:
                    EXPORT_FILTER_INCLUDE_900, EXPORT_FILTER_INCLUDE_INVALID
                    defined in ebas.doain.__init__
            state   the DB state for the context (only work on metadata and
                    data which are valid in this DB state)
                    datetime.datetime, None=current
            diff    only work on metadata and data that differ between state
                    and diff.
                    datetime.datetime, None=on all valid data
            diff_ctx
                    the EbasDomainDbContext object used for handling the object
                    layer for objects in "reversed" diff/state.
                    (should only be used by EbasDomainDbContext.__init__)
                    None=create new context if needed.
            cache   cache object to be used (None=create new cache)
        """
        DataObject.__init__(self)
        self.dbh = dbh
        self.time = time
        self.state = state
        self.diff = diff
        self.us_id = us_id
        self._dbwrite_obj = set()  # all objects which need to be written
        self._dbwrite_first = None  # object should be written first (useful?)
        self.export_filter = export_filter
        if cache:
            self.cache = cache
        elif dbh:
            self.cache = EbasDomainObjCache()
        if self.dbh:
            self.dbh.US_ID = us_id
        if self.diff:
            if not self.dbh:
                raise EbasDomainError("diff without dbh")
            if not self.state:
                self.state = self.dbh.safe_ts
            if diff_ctx:
                if diff_ctx.diff != self.state or \
                   diff_ctx.state != self.diff or diff_ctx.time != self.time:
                    raise EbasDomainError("diff_ctx: state/diff/time invalid")
                self.diff_ctx = diff_ctx
            else:
                # Create a "reversed" DbContext: stat/diff is reversed,
                # diff_ctx=self, and force a enew cache:
                self.diff_ctx = EbasDomainDbContext(
                    dbh=self.dbh, time=self.time, us_id=self.us_id,
                    export_filter=self.export_filter,
                    state=self.diff, diff=self.state, diff_ctx=self, cache=None)
        elif diff_ctx:
            raise EbasDomainError("diff_ctx without diff timestamp")

    def add_dbwrite_obj(self, obj):
        """
        Add object to the set of objects to be written on write_db.
        Parameters:
            obj    object to be added
        Returns:
            None
        """
        if not self._dbwrite_obj:
            self._dbwrite_first = obj
        if obj not in self._dbwrite_obj:
            self._dbwrite_obj.add(obj)

    def write_db(self):
        """
        Write all objects toi the DB.
        Parameters:
            None
        Returns:
            None
        """
        if self._dbwrite_first:
            self._dbwrite_first.write_db()
        for obj in self._dbwrite_obj:
            if obj != self._dbwrite_first:
                obj.write_db()
        self._dbwrite_obj = set()
        self._dbwrite_first = None
