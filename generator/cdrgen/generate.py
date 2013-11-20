import csv
from io import StringIO
import queue
import threading
from cdrgen.sources import UniformSource
from cdrgen.utils import asterisk_like, csv_to_cdr, time_of_day


class CDRStream(threading.Thread):
    def __init__(self, formatter, source):
        self.formatter = formatter
        self.output = StringIO()
        self.writer = csv.writer(self.output, delimiter=",", quoting=csv.QUOTE_ALL)
        self.source = source
        self.queue = queue.Queue()
        super(CDRStream, self).__init__()

    def run(self):
        for cdr in self.source:
            self.queue.put(cdr)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            cdr = self.queue.get(timeout=1)
        except queue.Empty:
            raise StopIteration
        self.writer.writerow(self.formatter(*cdr))
        val = self.output.getvalue().strip()
        self.output.truncate(0)
        self.output.seek(0)
        return val
