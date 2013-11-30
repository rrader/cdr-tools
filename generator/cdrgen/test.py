import csv
import datetime
from io import StringIO
from itertools import takewhile
from matplotlib.ticker import FuncFormatter
import numpy as np
import scipy
from cdrgen.generate import CDRStream
from cdrgen.sources import UniformSource, UserProfileSource, UserProfile, UserProfileChangeBehaviorSource
from cdrgen.utils import asterisk_like, csv_to_cdr, time_of_day, day_of_week, window, grouper, RATES_1, it_merge, RATES_2, poisson_interval, moving_average_exponential
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor

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

# values needed to recalculate in real time to
# minimize all values: alarms rate, history length ALPHA and ALARM_THRESHOLD
ALARM_THRESHOLD = 1.5  # multiply limits
ALPHA_FREQ = 0.8  # mean multipler
ALPHA_WEEKS = 0.8
HISTORY = 2  # in weeks
#=====
MIN_THRESHOLD = 9.e-6
CURRENT_WINDOW = 15 # to approximate current frequency
APPROX_WINDOW = 1  # to approximate weekly frequency
TIME_DISCRETIZATION = 60*60


class Pattern(object):
    # TODO: replace history with one pattern (and maintain with data + (old-new)/history)
    def __init__(self, user):
        self.src = user
        self.alarms = 0
        self.data = np.zeros(shape=(HISTORY, 7, 24))  # patterns 24x7 (history and one current)
        self.current = np.zeros(CURRENT_WINDOW)
        self.week_history = np.zeros(shape=(7, (24*60*60)//(TIME_DISCRETIZATION//APPROX_WINDOW)))
        self.last_day_of_week = 0
        self.weeks = 0

    def extract_week_history(self):
        ## smooth
        #for item in window(self.week_history, APPROX_WINDOW+1):
        #    pass
        week = np.ones(shape=(7, 24))*MIN_THRESHOLD
        for weekday in range(7):
            for i,item in enumerate(grouper(APPROX_WINDOW, self.week_history[weekday])):
                week[weekday, i] += sum(item)
        return week

    def maintain(self, cdr):
        """
        Maintaining should be continuous
        Calls have to be sorted by cdr.start time
        """
        time = time_of_day(cdr.start)//(TIME_DISCRETIZATION//APPROX_WINDOW)
        day = day_of_week(cdr.start)
        if self.last_day_of_week != day and day == 0:  # week switched
            self.data = np.roll(self.data, 1, axis=0)
            self.data[0] = self.extract_week_history()
            self.week_history = np.zeros(shape=(7, (24*60*60)//(TIME_DISCRETIZATION//APPROX_WINDOW)))
            self.weeks += 1
        self.week_history[day, time] += 1  # for average frequency
        self.last_day_of_week = day

        self.current = np.roll(self.current, 1)  # for instantaneous frequency
        self.current[0] = cdr.start

    def is_conform(self, cdr):
        # FIXME: pattern should no check conforming, it's another task
        day = day_of_week(cdr.start)
        # TODO: No interpolation! ?
        #freq = np.interp(time_of_day(cdr.start), [(x+0.5)*60*60 for x in range(24)],
        #                 self.get_pattern()[day])
        #freq = list(takewhile(lambda m: m[0] <= time_of_day(cdr.start), self.get_pattern()[day]))[-1][1]
        freq = self.get_pattern()[day][time_of_day(cdr.start)//60//60]

        current = np.roll(self.current, 1)
        current[0] = cdr.start
        diffs = np.array([e[0]-e[1] for e in zip(current, current[1:])])
        current_freq = np.interp(time_of_day(cdr.start), [(x+0.5)*60*60 for x in range(24)],
                                 self.week_history[day])
        current_freq = (60*60)/moving_average_exponential(diffs, ALPHA_FREQ)
        #print(current_freq)
        #print(cdr.start, current)
        #current_freq = self.week_history[day][time_of_day(cdr.start)//60//60]
        #limits = scipy.stats.poisson.interval(0.997, [freq])  # integer
        limits = poisson_interval(freq, 1-0.997)  # float

        if not (current_freq <= max(1.0, limits[1]*ALARM_THRESHOLD)):
            print(current.max() - current.min(), freq, max(1, limits[1]*ALARM_THRESHOLD), current_freq)
        return current_freq <= max(1.0, limits[1]*ALARM_THRESHOLD)

    def is_converged(self, cdr):
        return self.weeks >= HISTORY  # FIXME

    def alarm(self, cdr):
        self.alarms += 1
        print("ALARM: user {} behavior changed".format(cdr.src))

    def get_pattern(self):
        #print(moving_average_exponential(self.data, 0.75))
        #print(sum(self.data)/HISTORY)
        #return sum(self.data)/HISTORY
        return moving_average_exponential(self.data, ALPHA_WEEKS)

    def plot(self):
        row_labels = list('MTWTFSS')
        hours = list('0123456789AB')
        column_labels = ["{}am".format(x) for x in hours] + \
              ["{}pm".format(x) for x in hours]

        data = self.get_pattern()
        fig, ax = plt.subplots()
        ax.pcolor(data.transpose(), cmap=plt.cm.Blues)

        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(data.shape[0])+0.5, minor=False)
        ax.set_yticks(np.arange(data.shape[1])+0.5, minor=False)

        # want a more natural, table-like display
        ax.invert_yaxis()
        ax.xaxis.tick_top()

        ax.set_xticklabels(row_labels, minor=False)
        ax.set_yticklabels(column_labels, minor=False)
        plt.show()

    def plot_pattern(self):
        print(self.alarms)
        plt.plot(list(range(24)), self.get_pattern()[0], 'yo-')
        plt.plot(np.asarray(np.matrix(RATES_1[0])[:,0]).reshape(-1)//60//60,
                 np.asarray(np.matrix(RATES_1[0])[:,1]).reshape(-1)*60*60, 'ro-')
        plt.show()


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

    list(users.items())[0][1].plot_pattern()
    #list(users.items())[1][1].plot()


def test_uniform():
    test(UniformSource(0, 24*60*60, rate=0.1))

def test_daily():
    # Авторегрессионное интегрированное скользящее среднее
    # https://docs.google.com/viewer?url=http%3A%2F%2Fjmlda.org%2Fpapers%2Fdoc%2F2011%2Fno1%2FFadeevEtAl2011Autoreg.pdf
    TIME = 24*60*60*7*4*3
    p1 = [UserProfileSource(0, TIME, profile=UserProfile(RATES_1, 10, 0.1)) for x in range(1)]
    #p2 = [UserProfileSource(0, TIME, profile=UserProfile(RATES_2, 10, 0.1)) for x in range(1)]
    profiles = p1 #+ p2
    pattern(it_merge(*profiles, sort=lambda x: x[2]))
    #pattern(UserProfileChangeBehaviorSource(0, TIME, profile=UserProfile(RATES_1, 10, 0.1),
    #                                        profile2=UserProfile(RATES_2, 10, 0.1),
    #                                        when_to_change=24*60*60*7*4*1))
    #pattern(UserProfileSource(0, TIME, profile=UserProfile(RATES_1, 10, 0.1)))

if __name__ == "__main__":
    test_daily()
