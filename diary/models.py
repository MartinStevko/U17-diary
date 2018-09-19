from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "{}".format(self.name)

class Account(models.Model):
    idUser = models.ForeignKey(User, on_delete=models.PROTECT)
    approved = models.BooleanField(default=False)

    club = models.ForeignKey(Club, on_delete=models.PROTECT)

    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}".format(self.idUser.username)

class Week(models.Model):
    idAccount = models.ForeignKey(Account, on_delete=models.CASCADE)

    ordinal_number = models.PositiveIntegerField(blank=False)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}. týždeň - {}".format(self.ordinal_number, self.idAccount.idUser.username)

class Activity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    # points per minute
    ppm = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Activities"

    def __str__(self):
        return "{}".format(self.name)

class Action(models.Model):
    idAccount = models.ForeignKey(Account, on_delete=models.CASCADE)
    idActivity = models.ForeignKey(Activity, on_delete=models.PROTECT)

    duration = models.PositiveIntegerField(default=0)

    description = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.duration > 60:
            hours = self.duration // 60
            minutes = self.duration - 60*hours
            return "{} - {} hodín {} minút".format(self.idActivity.name, hours, minutes)
        else:
            return "{} - {} minút".format(self.idActivity.name, self.duration)

class Message(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)

    idAction = models.ForeignKey(Action, on_delete=models.CASCADE)
    content = models.TextField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} - {}".format(self.from_user.username, self.time)

class Code(models.Model):
    value = models.CharField(max_length=20)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}".format(self.value)

class EvaulationChanges(models.Model):
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{}".format(self.time)

class OldPoints(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    time = models.ForeignKey(EvaulationChanges, on_delete=models.PROTECT)
    value = models.PositiveIntegerField()

    def __str__(self):
        return "{} - {}".format(self.time.time, self.account.idUser.username)

class DuplicateError(models.Model):
    time = models.DateTimeField(default=timezone.now)

    idUser = models.ForeignKey(User, on_delete=models.CASCADE)
    error_message = models.TextField(blank=False)

    solved = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.time, self.idUser.username)
