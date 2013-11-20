from collections import namedtuple
import csv
from io import StringIO
from queue import Queue
import random
import threading

COUNTRIES = {"UA" : "380"}
CODES = ["000"]
POOL_NUMBER = 100
PHONE_LENGTH = 12
NAMES = ["Jayne", "Cobb", "Kaylee", "Frye", "Hoban", "Wash", "Washburne", "Zoe", "Washburne", "Derrial", "Book",
         "River", "Tam", "Simon", "Tam", "Malcolm", "Reynolds", "Inara", "Serra"]

phonebook_entry = namedtuple("PhonebookEntry", ["name", "number"])

def generate_phone(country, code):
    prefix = "{}{}".format(COUNTRIES[country], code)
    phone = "".join([str(random.randint(0, 9)) for _ in range(PHONE_LENGTH - len(prefix))])
    return "{}{}".format(prefix, phone)


def phonebook_item_generator():
    """Generates unique phone number"""
    generated = []
    while True:
        number = generate_phone("UA", CODES[0])
        if number not in generated:
            generated.append(number)
            yield phonebook_entry(number=number, name="{} {}".format(random.choice(NAMES), random.choice(NAMES)))


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


class UniformSource(object):
    def __init__(self, start_time, duration, rate):
        self.time = start_time
        self.end_time = start_time + duration
        self.rate = rate
        gen = phonebook_item_generator()
        self.phone_book = [next(gen) for _ in range(POOL_NUMBER)]

    def __iter__(self):
        return self

    def __next__(self):
        self.time += random.expovariate(self.rate)
        if self.time > self.end_time:
            raise StopIteration
        start = int(self.time)
        answer = start + random.randint(0,15)
        end = answer + random.randint(0,300)
        src, dst = random.sample(self.phone_book, 2)
        return src, dst, self.time, answer, end


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
    s = CDRStream(asterisk_like, UniformSource(0, 100, rate=1.0))
    s.start()
    for x in s:
        print(x)
