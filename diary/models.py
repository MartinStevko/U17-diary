from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from datetime import date

types = (
    ('challange', 'challange'),
    ('item', 'item'),
)


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

    class Meta:
        verbose_name_plural = "Evaluation changes"

    def __str__(self):
        return "{}".format(self.time)


class OldPoints(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    time = models.ForeignKey(EvaulationChanges, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Old points"

    def __str__(self):
        return "{} - {}".format(self.time.time, self.account.idUser.username)


class DailyChallange(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField(default=date.today)

    points = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Daily challanges"

    def __str__(self):
        return "{} - {}".format(self.date, self.name)


class ChallangeItem(models.Model):
    challange = models.ForeignKey(DailyChallange, on_delete=models.CASCADE)

    action = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = "Challange items"

    def __str__(self):
        return "{} - {}".format(self.challange.date, self.action)


class ItemResult(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    item = models.ForeignKey(ChallangeItem, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Item results"

    def __str__(self):
        return "{} - {}".format(self.account.idUser.username, self.item.action)


class ChallangeResult(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    challange = models.ForeignKey(DailyChallange, on_delete=models.PROTECT)
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Challange results"

    def __str__(self):
        return "{} - {}".format(self.account.idUser.username, self.challange.name)


class DuplicateError(models.Model):
    time = models.DateTimeField(default=timezone.now)

    idUser = models.ForeignKey(User, on_delete=models.CASCADE)
    error_message = models.TextField(blank=False)

    solved = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.time, self.idUser.username)
