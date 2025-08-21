"""
$Id: msg_condenser.py 2427 2020-03-19 23:09:09Z pe $

Message condenser, a way to deal with many repeating messages (e.g. logging).

= Synopsis:

from nilutility.msg_condenser import MessageCondenser

msgc = MessageCondenser(10)

def printit(*args):
    print args[0]

for i in range(1000000):
    msgc.add(printit, 1, 'message')
msgc.deliver()

==>

message
The previous message repeats 999999 times


Both classes will for real world scenarios be base classes for more specialized
derived classes. See fileformats/NasaAmes and ebas.io.file/basefile for
examples.

"""

from collections import defaultdict

class MessageRecord(tuple):
    """
    Message record class for MessageCondenser
    """

    KEYS = ['msgfunc', 'msg_id']
    DATA = ['message']

    def __getattr__(self, name):
        """
        Get key and data elements as attributes.
        Parameters:
            name    attribute name
        Returns:
            tuple value which corresponds to the respective key or data element.
        Raises:
            Attribute error if attribute name does not exists in key or data.
        """
        if name in self.__class__.KEYS:
            return self[self.__class__.KEYS.index(name)]
        if name in self.__class__.DATA:
            return self[len(self.__class__.KEYS) +
                        self.__class__.DATA.index(name)]
        raise AttributeError("'{}' object has no attribute '{}'".format(
            self.__class__.__name__, name))

    @property
    def key(self):
        """
        Get the key values of the record as tuple.
        Parameters:
            None
        Returns:
            Key values
        """
        return self[0:len(self.__class__.KEYS)]

class MessageCondenser(object):
    """
    Condense recurring messages.
    """

    def __init__(self, threshold=10, record_cls=MessageRecord):
        """
        Set up condenser object.
        Parameters:
            threshold   message threshold (from this number of occurrences the
                        messages will be condensed.
                        0 -> never condense
        Returns:
            None
        """
        self.threshold = threshold
        self.record_cls = record_cls
        self.list = []
        self.dict = defaultdict(list)

    def add(self, *args):
        """
        Add a message to the object.
        Parameter:
            *args: all keys and all data elements (additional elements included)
        Returns:
            None
        """
        record = self.record_cls(args)
        self.list.append(record)
        self.dict[record.key].append(record)

    def deliver(self):
        """
        Deliver the messages.
        """
        processed = []
        for msg in self.list:
            key = msg.key
            if key in processed:
                continue
            if self.threshold != 0 and len(self.dict[key]) >= self.threshold:
                # condense messages
                self.deliver_msg(msg, True)
                processed.append(key)
            else:
                # deliver a single message
                self.deliver_msg(msg, False)
        self.reset()

    def deliver_msg(self, record, condensed):  # pylint: disable=R0201
        # R0201: Method could be a  function
        # --> this is usually overridden with a real method...
        """
        Deliver a single message.
        Parameters:
            record
        Returns:
            None
        """
        record.msgfunc(record.message)
        if condensed:
            record.msgfunc(
                "The previous message repeats {} times".format(
                    len(self.dict[record.key])-1))

    def reset(self):
        """
        Reset the object to a freshly initialized state.
        """
        self.list = []
        self.dict = defaultdict(list)

    def is_reset(self):
        """
        Check status if object is reset.
        Parameters:
            None
        Returns:
            True if reset, else False
        """
        if self.list or self.dict:
            return False
        return True
