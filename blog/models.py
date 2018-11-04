from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Stats(models.Model):
    alcohol = models.FloatField()
    blood_pressure = models.IntegerField()
    steps = models.IntegerField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date_posted)


class Test(models.Model):
    date = models.DateTimeField(default=timezone.now)
    alcohol = models.IntegerField()
    steps = models.IntegerField()
    pressure = models.IntegerField()

    def __str__(self):
        return str(self.date)


class Activity(models.Model):
    user = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    steps = models.PositiveIntegerField(default=0)
    pulse = models.FloatField(default=0.0)

    def datetime(self):
        return self.timestamp.strftime("%Y.%m.%d %H:%M:%S")

    def __str__(self):
        d = {'user': self.user, 'datetime': self.datetime(), 'steps': self.steps, 'pulse': self.pulse}
        return str(d)


class Drinking(models.Model):
    user = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    alcohol = models.FloatField(default=0.0)

    def datetime(self):
        return self.timestamp.strftime("%Y.%m.%d %H:%M:%S")

    def __str__(self):
        d = {'user': self.user, 'datetime': self.datetime(), 'alcohol': self.alcohol}
        return str(d)