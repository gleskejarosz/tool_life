from django.conf import settings
from django.db import models

AM = "Morning shift"
PM = "Afternoon shift"
NS = "Night shift"
SHIFT_CHOICES = (
    ("--", "No choice"),
    (AM, "Morning shift"),
    (PM, "Afternoon shift"),
    (NS, "Night shift"),
)
HOUR_CHOICES = (
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12"),
)


class Pareto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    pareto_date = models.DateField()
    shift = models.CharField(max_length=32, choices=SHIFT_CHOICES, default="--")
    hours = models.CharField(max_length=32, choices=HOUR_CHOICES, default=8)
    time_stamp = models.TimeField()
    completed = models.BooleanField(default=False)
    jobs = models.ManyToManyField("ParetoDetail")
    downtimes = models.ManyToManyField("DowntimeDetail")
    scrap = models.ManyToManyField("ScrapDetail")
    ops = models.PositiveIntegerField(default=0)
    not_scheduled_to_run = models.PositiveIntegerField(default=0)
    job_otg = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="job5", blank=True, null=True)

    def __str__(self):
        return f"{self.pareto_date}"

    class Meta:
        verbose_name = "Pareto"


class ParetoDetail(models.Model):
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs", blank=False, null=False)
    qty = models.PositiveIntegerField(default=0)
    good = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    pareto_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Pareto Detail"


class DowntimeModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Downtime"


class DowntimeDetail(models.Model):
    downtime = models.ForeignKey(DowntimeModel, on_delete=models.CASCADE, related_name="downtime", blank=False,
                                 null=False)
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs5", blank=False, null=False)
    minutes = models.PositiveIntegerField(default=0, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    pareto_date = models.DateField(blank=True, null=True)
    frequency = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.downtime}"

    class Meta:
        verbose_name = "Downtime Detail"


class DowntimeGroup(models.Model):
    name = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, unique=True)
    calculation = models.ForeignKey("CalculationModel", default=1, on_delete=models.CASCADE, related_name="calc_settings",
                                    blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "User Group Name"


class DowntimeUser(models.Model):
    downtime = models.ForeignKey(DowntimeModel, on_delete=models.CASCADE, related_name="downtime_user", blank=False,
                                 null=False)
    group = models.ForeignKey(DowntimeGroup, on_delete=models.CASCADE, related_name="downtime_group", blank=False,
                              null=False)
    order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.downtime}"

    class Meta:
        verbose_name = "Downtime vs Group"


class ScrapModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Scrap reason"


class ScrapDetail(models.Model):
    scrap = models.ForeignKey(ScrapModel, on_delete=models.CASCADE, related_name="scrap", blank=False, null=False)
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs3", blank=False, null=False)
    qty = models.PositiveIntegerField(default=0, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    pareto_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.scrap}"

    class Meta:
        verbose_name = "Scrap detail"


class ScrapUser(models.Model):
    scrap = models.ForeignKey(ScrapModel, on_delete=models.CASCADE, related_name="scrap_user", blank=False,
                              null=False)
    group = models.ForeignKey(DowntimeGroup, on_delete=models.CASCADE, related_name="scrap_group", blank=False,
                              null=False)
    order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.scrap}"

    class Meta:
        verbose_name = "Scrap vs Group"


class HourModel(models.Model):
    start = models.TimeField()

    def __str__(self):
        return f"{self.start}"

    class Meta:
        verbose_name = "Hour"


class LineHourModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=False, null=True)
    start = models.ForeignKey(HourModel, on_delete=models.CASCADE, related_name="starts", blank=False,
                              null=False)
    shift = models.CharField(max_length=32, choices=SHIFT_CHOICES, blank=False, null=False)

    def __str__(self):
        return f"{self.start}"

    class Meta:
        verbose_name = "Line start hour"


class JobModel2(models.Model):
    name = models.CharField(max_length=64)
    target = models.IntegerField(default=1615)
    inner_size = models.PositiveSmallIntegerField(default=0)
    group = models.ForeignKey(DowntimeGroup, on_delete=models.CASCADE, related_name="job_group", blank=False,
                              null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Job"


class CalculationModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Hourly Calculation"


from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class TimerException(Exception):
    pass


class TimerStartException(TimerException):
    pass


class TimerResumeException(TimerException):
    pass


class TimerQuerySet(models.QuerySet):

    def start(self, user=None):
        timer = self.create(user=user)
        timer.start()
        return timer


class Timer(models.Model):

    STATUS = (
        ('running', _('running')),
        ('paused', _('paused')),
        ('stopped', _('stopped')),
    )

    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=12, choices=STATUS)

    objects = TimerQuerySet.as_manager()

    def duration(self):
        return sum([segment.duration() for segment in self.segment_set.all()], timedelta())

    def start(self):
        if self.segment_set.count() > 0:
            raise TimerStartException(_('Timer has already been started.'))
        self.segment_set.create()
        self.status = 'running'
        self.save()

    def stop(self):
        self.pause()
        self.status = 'stopped'
        self.save()

    def pause(self):
        self.segment_set.last().stop()
        self.status = 'paused'
        self.save()

    def resume(self):
        if self.status == 'stopped':
            raise TimerResumeException(_('Timer has been stopped and cannot be resumed.'))
        if not self.segment_set.last().stop_time:
            raise TimerResumeException(_('Cannot resume, if timer is still running.'))
        self.segment_set.create()
        self.status = 'running'
        self.save()


class Segment(models.Model):

    timer = models.ForeignKey(to=Timer, on_delete=models.CASCADE)

    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(null=True)

    def duration(self):
        if not self.stop_time:
            return now() - self.start_time
        return self.stop_time - self.start_time

    def stop(self):
        if not self.stop_time:
            self.stop_time = now()
            self.save()
