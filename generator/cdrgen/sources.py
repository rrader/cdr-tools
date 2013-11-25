from itertools import dropwhile
import random

import numpy as np

from cdrgen.utils import phonebook_item_generator, time_of_day, day_of_week


POOL_NUMBER = 100
_gen = phonebook_item_generator()
PHONE_BOOK = [next(_gen ) for _ in range(POOL_NUMBER)]

def new_number():
    num = next(_gen)
    PHONE_BOOK.append(num)
    return num

class UniformSource(object):
    """
    Poisson stream of calls, uniform duration distribution
    """
    def __init__(self, start_time, duration, rate):
        self.time = start_time
        self.end_time = start_time + duration
        self.rate = rate
        self.phone_book = PHONE_BOOK

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
        return src, dst, start, answer, end


class UserProfile(object):
    """
    rates is list of 7 vectors of tuples (from-time in seconds, from 0am of day, rate) (from monday to sunday)
    working_set is count of phone numbers user usual calls
    with probability of socialization user can call any call from global phone_book
    """
    def __init__(self, rates, working_set, socialization):
        self.rates = rates
        self.working_set = working_set
        self.socialization = socialization


class UserProfileSource(object):
    """
    Poisson stream of calls from ONE user
    Lambda changes in respect of current time and user profile
    """
    def __init__(self, start_time, duration, profile):
        self.time = start_time  # time in UTC
        self.end_time = start_time + duration
        self.rates = profile.rates
        self.socialization = profile.socialization
        self.phone_book = random.sample(PHONE_BOOK, profile.working_set)
        self.my_phone = new_number()

    def __iter__(self):
        return self

    def rate(self):
        day_time = time_of_day(self.time)
        week_day = day_of_week(self.time)
        return np.interp(day_time, [x[0] for x in self.rates[week_day]], [x[1] for x in self.rates[week_day]])
        #return list(takewhile(lambda m: m[0] <= day_time, self.rates[week_day]))[-1][1]

    def random_threshold(self):
        day_time = time_of_day(self.time)
        week_day = day_of_week(self.time)
        next = list(dropwhile(lambda m: m[0] <= day_time, self.rates[week_day]))
        if len(next) == 0:
            next_time = 24*60*60
        else:
            next_time = next[0][0]
        return next_time - day_time

    def step(self):
        while True:
            delta = random.expovariate(self.rate())
            if delta > self.random_threshold() and self.time < self.end_time:
                self.time += self.random_threshold()
            else:
                self.time += delta
                break

    def __next__(self):
        self.step()
        if self.time >= self.end_time:
            raise StopIteration
        start = int(self.time)
        answer = start + random.randint(0,15)
        end = answer + random.randint(0,300)
        if random.random() > self.socialization:
            dst = random.choice(self.phone_book)
        else:
            dst = random.choice(PHONE_BOOK)
        return self.my_phone, dst, start, answer, end


class UserProfileChangeBehaviorSource(UserProfileSource):
    def __init__(self, start_time, duration, profile, profile2, when_to_change):
        self.profile2 = profile2
        self.when_to_change = when_to_change
        super().__init__(start_time, duration, profile)

    def step(self):
        super().step()
        if self.time >= self.when_to_change:
            self.rates = self.profile2.rates

