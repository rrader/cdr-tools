import csv
from io import StringIO
import numpy as np
from sklearn.cluster import MiniBatchKMeans, KMeans
from cdrgen.generate import CDRStream
from cdrgen.sources import UniformSource, UserProfileSource, UserProfile, UserProfileChangeBehaviorSource
from cdrgen.utils import asterisk_like, csv_to_cdr, time_of_day, day_of_week, window, grouper, RATES_1,\
    it_merge, RATES_2, poisson_interval, moving_average_exponential, RATES_1m
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

# values needed to recalculate in real time to
# minimize all values: alarms rate, history length ALPHA and ALARM_THRESHOLD
ALARM_THRESHOLD = 1.  # multiply limits
ALPHA_FREQ = 0.8  # mean multipler
ALPHA_WEEKS = 0.8
HISTORY = 2  # in weeks
CURRENT_WINDOW = 5 # to approximate current frequency
#=====
MIN_THRESHOLD = 9.e-6
APPROX_WINDOW = 1  # to approximate weekly frequency
TIME_DISCRETIZATION = 60*60

alarms = 0

class Pattern(object):
    def __init__(self, user):
        self.src = user
        self.data = np.zeros(shape=(HISTORY, 7, 24))  # patterns 24x7 (history and one current)
        self.current = np.zeros(CURRENT_WINDOW)
        self.week_history = np.zeros(shape=(7, (24*60*60)//(TIME_DISCRETIZATION//APPROX_WINDOW)))
        self.last_day_of_week = 0
        self.weeks = 0
        self.class_num = None

    def extract_week_history(self):
        return self.week_history

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
        self.last_day_of_week = day

        self.current = np.roll(self.current, 1)  # for instantaneous frequency
        self.current[0] = cdr.start

        # new freq calc
        current = np.roll(self.current, 1)
        current[0] = cdr.start
        diffs = np.array([e[0]-e[1] for e in zip(current, current[1:])])
        current_freq = (60*60)/moving_average_exponential(diffs, ALPHA_FREQ)
        self.week_history[day, time] = max(self.week_history[day, time], current_freq)


    def is_conform(self, cdr):
        # FIXME: pattern should no check conforming, it's another task
        day = day_of_week(cdr.start)
        freq = self.get_pattern()[day][time_of_day(cdr.start)//60//60]

        current = np.roll(self.current, 1)
        current[0] = cdr.start
        diffs = np.array([e[0]-e[1] for e in zip(current, current[1:])])
        current_freq = (60*60)/moving_average_exponential(diffs, ALPHA_FREQ)

        limits = poisson_interval(freq, 1-0.997)  # float

        if not (current_freq <= max(1.0, limits[1]*ALARM_THRESHOLD)):
            print(freq, current_freq, max(1, limits[1]*ALARM_THRESHOLD), )
        return current_freq <= max(1.0, limits[1]*ALARM_THRESHOLD)

    def is_converged(self):
        return self.weeks >= HISTORY  # FIXME

    def alarm(self, cdr):
        global alarms
        alarms += 1
        print("ALARM: user {} behavior changed".format(cdr.src))

    def classify(self, class_num):
        self.class_num = class_num

    def get_pattern(self):
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
        print(alarms)
        plt.plot(list(range(24)), self.get_pattern()[0], 'yo-')
        plt.plot(np.asarray(np.matrix(RATES_1[0])[:,0]).reshape(-1)//60//60,
                 np.asarray(np.matrix(RATES_1[0])[:,1]).reshape(-1)*60*60, 'ro-')
        plt.show()


def process(source):
    """
    Simple processing
    """
    s = CDRStream(asterisk_like, source)
    s.start()
    for st in s:
        cdr = csv_to_cdr(list(csv.reader(StringIO(st), delimiter=','))[0])
        if not users.get(cdr.src):
            users[cdr.src] = Pattern(cdr.src)
        pattern = users[cdr.src]
        if pattern.is_converged() and not pattern.is_conform(cdr):
            pattern.alarm(cdr)
        pattern.maintain(cdr)


def recalculate(time):
    patterns = [p for p in users.values() if p.is_converged()]
    if len(patterns) < 10:
        return

    X = np.matrix([x.get_pattern().ravel() for x in patterns])
    km = KMeans(n_clusters=2, init='k-means++')
    km.fit(X)
    predicted = km.predict(X)
    print(predicted)
    for i,item in enumerate(predicted):
        patterns[i].classify(item)
    recalculate.km_time = time


def process_2(source):
    s = CDRStream(asterisk_like, source)
    s.start()
    recalculate.km_time = 0
    for st in s:
        cdr = csv_to_cdr(list(csv.reader(StringIO(st), delimiter=','))[0])
        if not users.get(cdr.src):
            users[cdr.src] = Pattern(cdr.src)
        pattern = users[cdr.src]
        if pattern.is_converged() and not pattern.is_conform(cdr):
            pattern.alarm(cdr)
        pattern.maintain(cdr)
        if cdr.start - recalculate.km_time >= 24*60*60*7:
            # Once a week recalculate clusters
            recalculate(cdr.start)
    recalculate(cdr.start)


def test_uniform():
    test(UniformSource(0, 24*60*60, rate=0.1))


def test_daily():
    # Авторегрессионное интегрированное скользящее среднее
    # https://docs.google.com/viewer?url=http%3A%2F%2Fjmlda.org%2Fpapers%2Fdoc%2F2011%2Fno1%2FFadeevEtAl2011Autoreg.pdf
    TIME = 24*60*60*7*4*2
    p1 = [UserProfileSource(0, TIME, profile=UserProfile(RATES_1, 10, 0.1)) for x in range(10)]
    p2 = [UserProfileSource(0, TIME, profile=UserProfile(RATES_2, 10, 0.1)) for x in range(5)]
    profiles = p1 + p2
    process_2(it_merge(*profiles, sort=lambda x: x[2]))

def test_one(rates):
    TIME = 24*60*60*7*4*2
    process_2(UserProfileSource(0, TIME, profile=UserProfile(rates, 10, 0.1)))
    list(users.values())[0].plot()

def test_change(rates, rates2):
    TIME = 24*60*60*7*4*2
    process_2(UserProfileChangeBehaviorSource(0, TIME, profile=UserProfile(rates, 10, 0.1),
                                              profile2=UserProfile(rates2, 10, 0.1),
                                              when_to_change=TIME//2))

def test_change_group(rates, rates2, rates3, rates4):
    TIME = 24*60*60*7*4*2
    p1 = [UserProfileChangeBehaviorSource(0, TIME, profile=UserProfile(rates, 10, 0.1),
                                              profile2=UserProfile(rates2, 10, 0.1),
                                              when_to_change=TIME//2) for x in range(10)]
    p2 = [UserProfileChangeBehaviorSource(0, TIME, profile=UserProfile(rates3, 10, 0.1),
                                              profile2=UserProfile(rates4, 10, 0.1),
                                              when_to_change=TIME//2) for x in range(5)]
    profiles = p1 + p2
    process_2(it_merge(*profiles, sort=lambda x: x[2]))
    print(alarms)

if __name__ == "__main__":
    test_one(RATES_1m)
    #test_change(RATES_1, RATES_1m)
    #test_daily()
    #test_change_group(RATES_1, RATES_1m, RATES_2, RATES_2)