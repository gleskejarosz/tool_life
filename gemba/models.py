from datetime import datetime

import pytz
from django.conf import settings
from django.db import models


AM = "Morning shift"
PM = "Afternoon shift"
NS = "Night shift"

NOT_IN_USE = "Not in use"
PRODUCTIVE = "Productive"

SHIFT_CHOICES = (
    ("--", "No choice"),
    (AM, "Morning shift"),
    (PM, "Afternoon shift"),
    (NS, "Night shift"),
)

TC = "Total output, Total good"
HCI = "Hourly Good, Scrap items, Inners"
HCB = "Hourly Good, Scrap items, Bags"
MC = "Meter, Scrap items"

CALCULATION_CHOICES = (
    (TC, "Total output, Total good"),
    (HCI, "Hourly Good, Scrap items, Inners"),
    (HCB, "Hourly Good, Scrap items, Bags"),
    (MC, "Meter, Scrap items"),
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
                             on_delete=models.CASCADE, blank=True, null=True)
    pareto_date = models.DateField()
    shift = models.CharField(max_length=32, choices=SHIFT_CHOICES, default="--")
    hours = models.CharField(max_length=32, choices=HOUR_CHOICES, default=8)
    time_stamp = models.TimeField()
    completed = models.BooleanField(default=False)
    jobs = models.ManyToManyField("ParetoDetail")
    downtimes = models.ManyToManyField("DowntimeDetail")
    scrap = models.ManyToManyField("ScrapDetail")
    availability = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quality = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    oee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    not_scheduled_to_run = models.PositiveIntegerField(default=0)
    job_otg = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="job5", blank=True, null=True)
    ops_otg = models.PositiveIntegerField(blank=True, null=True)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines2", blank=True, null=True)

    def __str__(self):
        return f"{self.pareto_date}"

    class Meta:
        verbose_name = "Pareto"


class ParetoDetail(models.Model):
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs", blank=False, null=False)
    output = models.IntegerField(default=0)
    good = models.IntegerField(default=0)
    scrap = models.IntegerField(default=0)
    rework = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    ops = models.PositiveIntegerField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, blank=True)
    pareto_date = models.DateField(blank=True, null=True)
    start_meter = models.PositiveIntegerField(default=0)
    takt_time = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines3", blank=True, null=True)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Pareto Detail"

    def save(self, *args, **kwargs):
        self.modified = datetime.now(tz=pytz.UTC)
        super().save(*args, **kwargs)


class DowntimeModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Downtime Reason"


class DowntimeDetail(models.Model):
    downtime = models.ForeignKey(DowntimeModel, on_delete=models.CASCADE, related_name="downtime", blank=False,
                                 null=False)
    from_job = models.CharField(max_length=64, blank=True, null=True)
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs5", blank=False, null=False)
    minutes = models.PositiveIntegerField(default=0, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    completed = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    pareto_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, blank=True)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines4", blank=True, null=True)

    def __str__(self):
        return f"{self.downtime}"

    class Meta:
        verbose_name = "Downtime Detail"

    def save(self, *args, **kwargs):
        self.modified = datetime.now(tz=pytz.UTC)
        super().save(*args, **kwargs)


class DowntimeUser(models.Model):
    downtime = models.ForeignKey(DowntimeModel, on_delete=models.CASCADE, related_name="downtime_user", blank=False,
                                 null=False)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines13", blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True)
    gemba = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.downtime}"

    class Meta:
        verbose_name = "Downtime vs Line"


class ScrapModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)
    rework = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Scrap reason"


class ScrapDetail(models.Model):
    scrap = models.ForeignKey(ScrapModel, on_delete=models.CASCADE, related_name="scrap", blank=False, null=False)
    from_job = models.CharField(max_length=64, blank=True, null=True)
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs3", blank=False, null=False)
    qty = models.PositiveIntegerField(default=0, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    completed = models.BooleanField(default=False)
    quarantined = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, blank=True)
    pareto_date = models.DateField(blank=True, null=True)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines5", blank=True, null=True)

    def __str__(self):
        return f"{self.scrap}"

    class Meta:
        verbose_name = "Scrap Detail"

    def save(self, *args, **kwargs):
        self.modified = datetime.now(tz=pytz.UTC)
        super().save(*args, **kwargs)


class ScrapUser(models.Model):
    scrap = models.ForeignKey(ScrapModel, on_delete=models.CASCADE, related_name="scrap_user", blank=False,
                              null=False)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines14", blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True)
    gemba = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.scrap}"

    class Meta:
        verbose_name = "Scrap vs Line"


class LineHourModel(models.Model):
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines1", blank=True, null=True)
    start = models.TimeField()
    shift = models.CharField(max_length=32, choices=SHIFT_CHOICES, blank=False, null=False)

    def __str__(self):
        return f"{self.start}"

    class Meta:
        verbose_name = "Line Start Hour"


class JobModel2(models.Model):
    name = models.CharField(max_length=64)
    inner_size = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Job"


class JobLine(models.Model):
    job = models.ForeignKey(JobModel2, on_delete=models.CASCADE, related_name="job", blank=True, null=True)
    target = models.IntegerField(default=0)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines19", blank=True, null=True)
    factor = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Job vs Line"


class Editors(models.Model):
    editor_name = models.CharField(max_length=200)
    num_users = models.IntegerField()

    def __str__(self):
        return "{}-{}".format(self.editor_name, self.num_users)


# line setup as primary key
class Line(models.Model):
    LINE_STATUS = (
        (PRODUCTIVE, "Productive"),
        (NOT_IN_USE, "Not in use"),
    )
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=16)
    description = models.CharField(max_length=64, blank=True, null=True)
    line_status = models.CharField(max_length=64, choices=LINE_STATUS, default=PRODUCTIVE)
    calculation = models.CharField(max_length=32, choices=CALCULATION_CHOICES, blank=False, default=HCI)

    def __str__(self):
        return f"{self.name}"


class LineUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="lines", blank=False, null=False)

    def __str__(self):
        return f"{self.line}"

    class Meta:
        verbose_name = "User vs Line"


class Timer(models.Model):
    start = models.DateTimeField(auto_now_add=True, blank=True)
    end = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start}"

    class Meta:
        verbose_name = "Timer"


class MonthlyResults(models.Model):
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=16)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="lines20", blank=True, null=True)
    total_output = models.PositiveIntegerField(default=0)
    total_good = models.IntegerField(default=0)
    total_scrap = models.PositiveIntegerField(default=0)
    total_rework = models.PositiveIntegerField(default=0)
    total_available_time = models.PositiveIntegerField(default=0)
    total_availability = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_performance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quality = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_oee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    counter = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.year} - {self.month}"

    class Meta:
        verbose_name = "Monthly Result"


class QuarantineHistoryDetail(models.Model):
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs6", blank=False, null=False)
    initial_qty = models.PositiveIntegerField(default=0, blank=False, null=False)
    good = models.IntegerField(default=0)
    scrap = models.IntegerField(default=0)
    scraps = models.ManyToManyField("ScrapDetail")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    pareto_id = models.PositiveIntegerField(default=0)
    modified = models.DateTimeField(auto_now_add=True, blank=True)
    pareto_date = models.DateField(blank=True, null=True)
    line = models.ForeignKey("Line", on_delete=models.CASCADE, related_name="lines21", blank=True, null=True)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Quarantine Record"

    def save(self, *args, **kwargs):
        self.modified = datetime.now(tz=pytz.UTC)
        super().save(*args, **kwargs)
