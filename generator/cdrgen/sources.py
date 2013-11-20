from itertools import takewhile
import random
from cdrgen.utils import phonebook_item_generator

POOL_NUMBER = 100


class UniformSource(object):
    """
    Poisson stream of calls, uniform duration distribution
    """
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


class TimeDependSource(object):
    """
    Poisson stream of calls.
    Lambda depends on time: rates is vector of tuples (from-time in seconds, from 0am of day, rate)
    """
    def __init__(self, start_time, duration, rates):
        self.time = start_time  # time in UTC
        self.end_time = start_time + duration
        self.rates = rates
        gen = phonebook_item_generator()
        self.phone_book = [next(gen) for _ in range(POOL_NUMBER)]

    def __iter__(self):
        return self

    def rate(self):
        day_time = self.time - int(self.time/60/60/24)*60*60*24
        return list(takewhile(lambda m: m[0] < day_time, self.rates))[-1][1]

    def __next__(self):
        self.time += random.expovariate(self.rate())
        if self.time > self.end_time:
            raise StopIteration
        start = int(self.time)
        answer = start + random.randint(0,15)
        end = answer + random.randint(0,300)
        src, dst = random.sample(self.phone_book, 2)
        return src, dst, self.time, answer, end
