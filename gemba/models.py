from django.conf import settings
from django.db import models

from tools.models import JobModel


AM = "Morning shift"
PM = "Afternoon shift"
NS = "Night shift"
SHIFT_CHOICES = (
    (AM, "Morning shift"),
    (PM, "Afternoon shift"),
    (NS, "Night shift"),
    )


class Pareto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    pareto_date = models.DateField()
    # shift = models.CharField(max_length=32, choices=SHIFT_CHOICES, default=AM)
    time_stamp = models.DateTimeField()
    completed = models.BooleanField(default=False)
    jobs = models.ManyToManyField("ParetoDetail")
    downtimes = models.ManyToManyField("DowntimeDetail")
    scrap = models.ManyToManyField("ScrapDetail")

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = "Pareto"


class ParetoDetail(models.Model):
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs", blank=False, null=False)
    qty = models.PositiveIntegerField(default=0)
    good = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Pareto Detail"


class DowntimeModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return f"{self.code}"

    class Meta:
        verbose_name = "Downtime"


class DowntimeDetail(models.Model):
    downtime = models.ForeignKey(DowntimeModel, on_delete=models.CASCADE, related_name="downtime", blank=False, null=False)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs5", blank=False, null=False)
    minutes = models.PositiveIntegerField(default=0, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.downtime}"

    class Meta:
        verbose_name = "Downtime Detail"


class ScrapModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return f"{self.code}"

    class Meta:
        verbose_name = "Scrap reason"


class ScrapDetail(models.Model):
    scrap = models.ForeignKey(ScrapModel, on_delete=models.CASCADE, related_name="scrap", blank=False, null=False)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs3", blank=False, null=False)
    qty = models.PositiveIntegerField(default=0, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.scrap}"

    class Meta:
        verbose_name = "Scrap detail"
