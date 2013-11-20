import csv
from io import StringIO
from queue import Queue
import threading
from cdrgen.sources import UniformSource
from cdrgen.utils import asterisk_like


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
    hours = [0 for x in range(24)]
    file = StringIO()
    for x in s:
        file.write(x)

    file.seek(0)
    reader = csv.reader(file, delimiter=',')
    for line in reader:
        print(line)