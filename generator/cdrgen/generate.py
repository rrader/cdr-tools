from collections import namedtuple
import csv
from io import StringIO
from queue import Queue
import random
import threading
from cdrgen.sources import UniformSource


def asterisk_like(src, dst, start, answer, end):
    """Returns asterisk-like fields of CDR"""
    account_code = ""
    dcontext = "dcont"
    channel = dst_channel = "SIP/????"
    last_app = "Dial"
    last_data = "SIP/?????,??,??"
    amaflags = "DOCUMENTATION"
    user_field = "????"
    unique_id = ""
    while True:
        clid = '{} <{}>'.format(src.name, src.number)
        duration = end - start
        bill_sec = end - answer
        disposition = "ANSWERED" if random.random() > 0.9 else "BUSY"
        return (account_code, src.number, dst.number, dcontext, clid, channel, dst_channel, last_app, last_data, start,
               answer, end, duration, bill_sec, disposition, amaflags, user_field, unique_id)


class CDRStream(threading.Thread):
    def __init__(self, formatter, source):
        self.formatter = formatter
        self.output = StringIO()
        self.writer = csv.writer(self.output, delimiter=",", quoting=csv.QUOTE_ALL)
        self.source = source
        self.queue = Queue()
        super(CDRStream, self).__init__()

    def run(self):
        for cdr in self.source:
            self.queue.put(cdr)

    def __iter__(self):
        return self

    def __next__(self):
        cdr = self.queue.get()
        self.writer.writerow(self.formatter(*cdr))
        val = self.output.getvalue().strip()
        self.output.truncate(0)
        self.output.seek(0)
        return val


if __name__ == "__main__":
    s = CDRStream(asterisk_like, UniformSource(0, 24*60*60, rate=0.005))
    s.start()
    for x in s:
        print(x)
