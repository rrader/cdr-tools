import csv
from io import StringIO
from cdrgen.generate import CDRStream
from cdrgen.sources import UniformSource, UserProfileSource, UserProfile
from cdrgen.utils import asterisk_like, csv_to_cdr, time_of_day

def test(source):
    s = CDRStream(asterisk_like, source)
    s.start()
    hours = [0 for x in range(24)]
    for st in s:
        cdr = csv_to_cdr(list(csv.reader(StringIO(st), delimiter=','))[0])
        hours[time_of_day(cdr.start)//60//60] += 1
        print(hours)


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
              (h(24.0),  0),]
            ]*7
    p = UserProfile(rates, 10, 0.1)
    test(UserProfileSource(0, 24*60*60*7*365, profile=p))

if __name__ == "__main__":
    test_daily()
