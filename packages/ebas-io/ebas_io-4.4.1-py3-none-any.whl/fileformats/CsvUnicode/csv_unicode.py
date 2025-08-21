"""
Csv Unicode file format module
$Id: csv_unicode.py 2715 2021-10-13 14:25:10Z pe $
"""
import csv, codecs
from six import PY2, StringIO

class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    ONLY used for PY2
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def __next__(self):
        return self.reader.next().encode("utf-8")

    def next(self):
        """
        For python2
        """
        return self.__next__()

class CsvUnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        if PY2:
            f = UTF8Recoder(f, encoding)
            self.reader = csv.reader(f, dialect=dialect, **kwds)
        else:
            self.reader = csv.reader(codecs.getreader(encoding)(f),
                                     dialect=dialect, **kwds)

    def __next__(self):
        row = next(self.reader)
        if PY2:
            return [unicode(s, "utf-8") for s in row]
        return row

    def next(self):
        """
        For python2
        """
        return self.__next__()

    def __iter__(self):
        return self

class CsvUnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    For PY2, all output streams were raw, so we had to encode all streams the
    same way.
    For PY3, the file object might encode already, and csv.writer may be called
    with a PY3 str (which is unicode). Nevertheless, in PY 3 one can also open
    a file in "wb" mode, which requires the same treatment as in PY2. In this
    case, use rawfile=False!
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", rawfile=True,
                 **kwds):
        """
        Set up the object
        """
        self.rawfile = rawfile
        # Redirect output to a queue
        self.queue = StringIO()
        if rawfile:
            self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        else:
            self.writer = csv.writer(f, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        if self.rawfile:
            if PY2:
                self.writer.writerow([unicode(s).encode("utf-8") for s in row])
                # Fetch UTF-8 output from the queue ...
                data = self.queue.getvalue()
                data = data.decode("utf-8")
            else:
                self.writer.writerow([str(s) for s in row])
                # Fetch UTF-8 output from the queue ...
                data = self.queue.getvalue()
            # ... and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the target stream
            self.stream.write(data)
            # empty queue
            self.queue.truncate(0)
        else:
            self.writer.writerow([s if isinstance(s, str) else str(s) for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
