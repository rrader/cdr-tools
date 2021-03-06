from collections import namedtuple
from datetime import datetime
from itertools import islice, zip_longest
import random
import itertools
import numpy as np

COUNTRIES = {"UA": "380"}
CODES = ["000"]
PHONE_LENGTH = 12
NAMES = ["Jayne", "Cobb", "Kaylee", "Frye", "Hoban", "Wash", "Washburne", "Zoe", "Washburne", "Derrial", "Book",
         "River", "Tam", "Simon", "Tam", "Malcolm", "Reynolds", "Inara", "Serra"]

phonebook_entry = namedtuple("PhonebookEntry", ["name", "number"])
cdr = namedtuple("CDR", ["src", "dst", "start", "answer", "end"])

_h = lambda x: x * 60 * 60  # hour
_r = lambda x, dur=1: float(x) / (60 * 60 * dur)  # count per hour within dur hours

RATES_1 = [[(_h(0.0), _r(1 / 30., 9.5)), # once per month
            (_h(6.5), _r(1 / 5.)), # once per 5 days
            (_h(7.5), _r(1)), # once per hour
            (_h(8.5), _r(6)), # 12 times per hour
            (_h(10.5), _r(12)), # 12 times per hour
            (_h(15.0), _r(12)), # 12 times per hour
            (_h(18.0), _r(1., 3.0)), # 1./(3*60*60) once per hour
            (_h(21.0), _r(1 / 30., 9.5)),
            (_h(24.0), 0),
           ]
          ] * 5 + \
          [[(_h(0.0), _r(1 / 30., 11.5)),
            (_h(8.0), _r(1 / 30., 11.5)),
            (_h(8.5), _r(2)),
            (_h(18.0), _r(2)),
            (_h(18.5), _r(1 / 30., 11.5)),
            (_h(24.0), 0),
           ]
          ] * 2

RATES_1m = [[(_h(0.0), _r(1 / 30., 9.5)), # once per month
            (_h(6.5), _r(1 / 5.)), # once per 5 days
            (_h(7.5), _r(1)), # once per hour
            (_h(8.5), _r(6)), # 12 times per hour
            (_h(10.5), _r(12)), # 12 times per hour
            (_h(15.0), _r(12)), # 12 times per hour
            (_h(18.0), _r(1., 3.0)), # 1./(3*60*60) once per hour
            (_h(21.0), _r(1 / 30., 9.5)),
            (_h(24.0), 0),
           ]
          ] * 5 + \
          [[(_h(0.0), _r(1 / 30., 11.5)),
            (_h(8.0), _r(1 / 30., 11.5)),
            (_h(8.5), _r(50)),
            (_h(18.0), _r(2)),
            (_h(18.5), _r(1 / 30., 11.5)),
            (_h(24.0), 0),
           ]
          ] * 2

RATES_2 = [[(_h(0.0), _r(1 / 30., 11.5)), # (1/(9.5*60*60))/30, once per month (10.5 is period within day)
            (_h(6.5), _r(1 / 5.)), # 1./(60*60)/5 once per 5 hours
            (_h(7.5), _r(2.)), # 1./(60*60) once per hour
            (_h(8.5), _r(1 / 20., 10)), # once per 20 days
            (_h(17.0), _r(1 / 20., 10)), # once per 20 days
            (_h(17.5), _r(1 / 5., 10)), # once per 20 days
            (_h(18.5), _r(2.)), # 1./(3*60*60) once per hour
            (_h(19.5), _r(1 / 30., 11.5)),
            (_h(24.0), 0.),
           ]
          ] * 5 + \
          [[(_h(0.0), _r(1, 9.5)),
            (_h(8.0), _r(1, 9.5)),
            (_h(8.5), _r(1)),
            (_h(18.), _r(1)),
            (_h(18.5), _r(1 / 30., 9.5)),
            (_h(24.0), 0.),
           ]
          ] * 2


def rate_variate(rates):
    def randomize_day(day):
        d = []
        for y in day:
            if 0 < y[0] < 24 * 60 * 60:
                d.append(
                    (y[0] + random.random() * 0.8 * 60 * 60 - 0.4 * 60 * 60, y[1] + random.random() / 1.e4 - 0.5e-4))
            else:
                d.append((y[0], y[1] + random.random() / 1.e4 - 0.5e-4))
        return d

    return [randomize_day(x) for x in rates]


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
    return time - (time // 60 // 60 // 24) * 60 * 60 * 24


def day_of_week(time):
    return datetime.fromtimestamp(time).weekday()


def window(seq, n=3):
    "Returns a sliding window (of width n) over data from the iterable"
    it = iter(seq)
    result = tuple(islice(it, (n + 1) // 2))
    if len(result) > 0:
        yield result
    for elem in it:
        result = result[1 if len(result) == n else 0:] + (elem,)
        yield result
    result = result[1:]
    while len(result) >= (n + 1) // 2:
        yield result
        result = result[1:]


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def it_merge(*iterators, sort):
    vector = [(k, next(it)) for k, it in enumerate(iterators)]
    while vector:
        k, val = sorted(vector, key=lambda x: sort(x[1]))[0]
        yield val
        try:
            vector[k] = (k, next(iterators[k]))
        except StopIteration:
            for v in (x for x in vector if x[0] > k):
                vector[v[0]] = (v[0] - 1, v[1])
            del vector[k]


def poisson_interval(k, alpha=0.05):
    """
    uses chisquared info to get the poisson interval. Uses scipy.stats
    (imports in function).
    """
    from scipy.stats import chi2

    a = alpha
    low, high = (chi2.ppf(a / 2, 2 * k) / 2, chi2.ppf(1 - a / 2, 2 * k + 2) / 2)
    if k == 0:
        low = 0.0
    return low, high


def moving_average_exponential(values, alpha, epsilon=0):
    if not 0 < alpha < 1:
        raise ValueError("out of range, alpha='%s'" % alpha)

    if not 0 <= epsilon < alpha:
        raise ValueError("out of range, epsilon='%s'" % epsilon)

    result = [None] * len(values)

    for i in range(len(result)):
        currentWeight = 1.0

        numerator = np.zeros(shape=values.shape[1:])
        denominator = 0
        for value in values[i::-1]:
            numerator += value * currentWeight
            denominator += currentWeight

            currentWeight *= alpha
            if currentWeight < epsilon:
                break

        #print(numerator, denominator)
        result[i] = numerator / denominator

    return result[-1]

#print(moving_average_exponential(np.array([[[1,2],[2,3]], [[2,3],[3,4]], [[3,4],[4,5]], [[4,5],[5,6]], [[5,6],[6,7]]]), 0.5))
