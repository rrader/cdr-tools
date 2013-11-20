from collections import namedtuple
from datetime import datetime
import random

COUNTRIES = {"UA" : "380"}
CODES = ["000"]
PHONE_LENGTH = 12
NAMES = ["Jayne", "Cobb", "Kaylee", "Frye", "Hoban", "Wash", "Washburne", "Zoe", "Washburne", "Derrial", "Book",
         "River", "Tam", "Simon", "Tam", "Malcolm", "Reynolds", "Inara", "Serra"]

phonebook_entry = namedtuple("PhonebookEntry", ["name", "number"])
cdr = namedtuple("CDR", ["src", "dst", "start", "answer", "end"])


def phonebook_item_generator():
    """Generates unique phone number"""
    generated = []
    while True:
        number = generate_phone("UA", CODES[0])
        if number not in generated:
            generated.append(number)
            yield phonebook_entry(number=number, name="{} {}".format(random.choice(NAMES), random.choice(NAMES)))


def generate_phone(country, code):
    prefix = "{}{}".format(COUNTRIES[country], code)
    phone = "".join([str(random.randint(0, 9)) for _ in range(PHONE_LENGTH - len(prefix))])
    return "{}{}".format(prefix, phone)


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


def csv_to_cdr(csv):
    return cdr(src=csv[1], dst=csv[2], start=int(csv[9]), answer=int(csv[10]), end=int(csv[11]))


def time_of_day(time):
    return time - (time//60//60//24)*60*60*24


def day_of_week(time):
    return datetime.fromtimestamp(time).weekday()
