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
    Lambda depends on time
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
