import csv
from io import StringIO
import numpy as np
from cdrgen.generate import CDRStream
from cdrgen.sources import UniformSource, UserProfileSource, UserProfile
from cdrgen.utils import asterisk_like, csv_to_cdr, time_of_day, day_of_week
import matplotlib.pyplot as plt

def test(source):
    s = CDRStream(asterisk_like, source)
    s.start()
    hours = np.zeros(24)
    l = []
    days = 1
    prev = 0
    pattern = None
    for st in s:
        cdr = csv_to_cdr(list(csv.reader(StringIO(st), delimiter=','))[0])
        if time_of_day(cdr.start) < prev:
            days += 1
            if days > 14 and pattern is None:
                pattern = hours/days
                hours = np.zeros(24)
            if days > 14 and days%7 == 0:
                print(np.linalg.norm(hours/(days-14) - pattern))
        h = time_of_day(cdr.start)//60//60
        hours[h] += 1
        prev = time_of_day(cdr.start)
        #l.append(h)
    fingerprint = hours/days
    print(fingerprint)


users = {}
ALARM_THRESHOLD = 0.5
HISTORY = 4  # in weeks
# (MIN_THRESHOLD - 1/(HISTORY+1))/MIN_THRESHOLD < ALARM_THRESHOLD
MIN_THRESHOLD = 1/(1+HISTORY-ALARM_THRESHOLD-ALARM_THRESHOLD*HISTORY)

class Pattern(object):
    # TODO: replace history with one pattern (and maintain with data + (old-new)/history)
    def __init__(self, user):
        self.src = user
        self.data = np.zeros(shape=(HISTORY + 1, 7, 24))  # patterns 24x7 (history and one current)
        self.last_day_of_week = 0
        self.weeks = 0

    def maintain(self, cdr):
        hour = time_of_day(cdr.start)//60//60
        day = day_of_week(cdr.start)
        if self.last_day_of_week != day and day == 0:  # week switched
            self.data = np.roll(self.data, 1, axis=0)
            self.data[0] = np.ones(shape=(7, 24))*MIN_THRESHOLD
            #self.data[0] = np.ones(shape=(7, 24)) * 0.001
            self.weeks += 1
        self.data[0, day, hour] += 1
        self.last_day_of_week = day

    def is_conform(self, cdr):
        hour = time_of_day(cdr.start)//60//60
        day = day_of_week(cdr.start)
        test = self.data.copy()
        test[0, day, hour] += 1
        freq = self.get_pattern()[day, hour]
        current_freq = (sum(test)/(HISTORY+1))[day, hour]
        #if abs(freq - MIN_THRESHOLD) < 0.01:
        #print(freq, current_freq)
        diff = (current_freq - freq) / freq

        return diff <= ALARM_THRESHOLD

    def is_converged(self, cdr):
        return self.weeks >= HISTORY  # FIXME

    def alarm(self, cdr):
        print("ALARM: user {} behaviour changed".format(cdr.src))

    def get_pattern(self):
        return sum(self.data[1:])/HISTORY

def pattern(source):
    s = CDRStream(asterisk_like, source)
    s.start()
    for st in s:
        cdr = csv_to_cdr(list(csv.reader(StringIO(st), delimiter=','))[0])
        if not users.get(cdr.src):
            users[cdr.src] = Pattern(cdr.src)
        pattern = users[cdr.src]
        if pattern.is_converged(cdr) and not pattern.is_conform(cdr):
            pattern.alarm(cdr)
        pattern.maintain(cdr)
    print(users)


def test_uniform():
    test(UniformSource(0, 24*60*60, rate=0.1))


def test_daily():
    h = lambda x: x*60*60  # hour
    rates = [[(h(0.0),  9.74e-7),   # (1/(9.5*60*60))/30, once per month (10.5 is period within day)
              (h(6.5),  5.5e-5),  # 1./(60*60)/5 once per 5 hours
              (h(7.5),  2.7e-4),  # 1./(60*60) once per hour
              (h(8.5),  1.1e-3),  # 4/(60*60) 4 times per hour
              (h(18.0), 9.25e-5), # 1./(3*60*60) once per hour
              (h(21.0), 9.74e-7),
              (h(24.0),  0)]
            ]*7
    p = UserProfile(rates, 10, 0.1)
    pattern(UserProfileSource(0, 24*60*60*7*4*3, profile=p))

if __name__ == "__main__":
    test_daily()
