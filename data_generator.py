#!/usr/bin/env python
from blog.models import *
from django.utils import timezone

from datetime import datetime
from datetime import timedelta
import random


class DataGenerator:
    def __init__(self, user, start_datetime=None, stop_datetime=None, steps_factor=25, pulse_factor=0.5, alco_factor=2.0, time_shift=timedelta(hours=0)):
        self.user = user
        self.start_datetime = start_datetime
        self.stop_datetime = stop_datetime
        self.steps_factor = steps_factor
        self.pulse_factor = pulse_factor
        self.alco_factor = alco_factor
        self.time_shift = time_shift

    def rand_datetime(self, start=None, stop=None):
        if start is None:
            start=self.start_datetime
        if stop is None:
            stop = self.stop_datetime
        delta = stop - start
        delta_seconds = delta.total_seconds()
        rand_seconds = timedelta(seconds=random.randrange(0, delta_seconds))
        rand_date = start + rand_seconds
        return rand_date

    def rand_alco(self, weekday, hour):
        alco = self.alco_factor
        if (weekday <= 4) and (1 <= hour <= 6):
            return None
        if 6 <= hour <= 16:
            alco /= 4
        if weekday >= 5:
            alco *= 2
        return random.random() * alco

    def rand_steps(self, weekday, hour, rand_alco=None):
        steps = self.steps_factor
        if (weekday <= 4) and (1 <= hour <= 6):
            return 0
        if 10 <= hour <= 17:
            steps /= 2
        if weekday == 6:
            steps *= 2
        if rand_alco is not None:
            steps *= 1 + rand_alco / self.alco_factor
        return int(random.random() * steps)

    def rand_pulse(self, weekday, hour, rand_steps, rand_alco=None):
        pulse = 85.0
        if 1 <= hour <= 6:
            pulse *= 0.8
        if rand_alco is not None:
            pulse += 1 + rand_alco / self.alco_factor
        pulse += rand_steps * self.pulse_factor
        pulse += random.random()
        return pulse

    def rand_single_data(self):
        measure_time = self.rand_datetime()
        weekday = measure_time.weekday()
        hour = measure_time.hour
        alco = self.rand_alco(weekday, hour)
        steps = self.rand_steps(weekday, hour, alco)
        pulse = self.rand_pulse(weekday, hour, steps, alco)
        activity = Activity(user=self.user, timestamp=measure_time, steps=steps, pulse=pulse)
        drinking = Drinking(user=self.user, timestamp=measure_time, alcohol=alco)
        return activity, drinking

    def rand_multiple_data(self, data_length):
        act_list = []
        drink_list = []
        for _ in range(data_length):
            act, drink = self.rand_single_data()
            act_list.append(act)
            if drink.alcohol is not None:
                drink_list.append(drink)
        return act_list, drink_list


class DataContainer:
    def __init__(self, user, days):
        self.user = user
        self.stop_datetime = timezone.now()
        self.start_datetime = self.stop_datetime - timedelta(days=days)

        self.act_list = None
        self.drink_list = None
        self.min_step = 0
        self.max_step = 0
        self.min_pulse = 0
        self.max_pulse = 0
        self.min_alco = 0
        self.max_alco = 0

    def rand(self, length):
        gen = DataGenerator(self.user, self.start_datetime, self.stop_datetime)
        self.act_list, self.drink_list = gen.rand_multiple_data(length)
        self.min_step = min([x.steps for x in self.act_list])
        self.max_step = max([x.steps for x in self.act_list])
        self.min_pulse = min([x.pulse for x in self.act_list])
        self.max_pulse = max([x.pulse for x in self.act_list])
        self.min_alco = min([x.alcohol for x in self.drink_list])
        self.max_alco = max([x.alcohol for x in self.drink_list])

    def save(self):
        for a in self.act_list:
            print(a)
            a.save(using='new_smartband_db')
        for d in self.drink_list:
            print(d)
            d.save(using='new_smartband_db')

    @staticmethod
    def clear_database():
        for a in Activity.objects.using('new_smartband_db').all():
            print(a)
            a.delete()
        for d in Drinking.objects.using('new_smartband_db').all():
            print(d)
            d.delete()
            

def generate(user, days, numbers=1000):
    cont = DataContainer(user, days)
    cont.rand(numbers)
    cont.save()


if __name__ == "__main__":
    time1 = datetime(year=2018, month=10, day=1)
    time2 = datetime(year=2018, month=11, day=1)
    gen = DataGenerator(1, time1, time2)
    activities_list, drinking_list = gen.rand_multiple_data(100)
    print(len(activities_list))
    print(len(drinking_list))
