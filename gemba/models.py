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

TC = "Total output, Total good"
HC = "Hourly Good, Scrap items"
MC = "Meter, Scrap items"

CALCULATION_CHOICES = (
    (TC, "Total output, Total good"),
    (HC, "Hourly Good, Scrap items"),
    (MC, "Meter, Scrap items"),
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
    ops = models.PositiveIntegerField(default=0)
    availability = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quality = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    oee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    not_scheduled_to_run = models.PositiveIntegerField(default=0)
    job_otg = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="job5", blank=True, null=True)

    def __str__(self):
        return f"{self.pareto_date}"

    class Meta:
        verbose_name = "Pareto"


class ParetoDetail(models.Model):
    job = models.ForeignKey("JobModel2", on_delete=models.CASCADE, related_name="jobs", blank=False, null=False)
    output = models.PositiveIntegerField(default=0)
    good = models.PositiveIntegerField(default=0)
    scrap = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    completed = models.BooleanField(default=False)
    pareto_id = models.PositiveIntegerField(default=0)
    pareto_date = models.DateField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True)
    frequency = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.downtime}"

    class Meta:
        ordering = ["-datetime"]
        verbose_name = "Downtime Detail"


class DowntimeGroup(models.Model):
    name = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, unique=True)
    calculation = models.CharField(max_length=32, choices=CALCULATION_CHOICES, blank=False, default=HC)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "User Group Name"


class DowntimeUser(models.Model):
    downtime = models.ForeignKey(DowntimeModel, on_delete=models.CASCADE, related_name="downtime_user", blank=False,
                                 null=False)
    group = models.ForeignKey(DowntimeGroup, on_delete=models.CASCADE, related_name="downtime_group", blank=True,
                              null=True)
    order = models.PositiveIntegerField(blank=True, null=True)
    gemba = models.PositiveIntegerField(blank=True, null=True)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
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
    gemba = models.PositiveIntegerField(blank=True, null=True)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=True)
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
    inner_size = models.PositiveSmallIntegerField(default=1)
    group = models.ForeignKey(DowntimeGroup, on_delete=models.CASCADE, related_name="job_group", blank=True,
                              null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Job"


class CalculationModel(models.Model):
    code = models.CharField(max_length=10, blank=False, null=False)
    description = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Hourly Calculation"


class Editors(models.Model):
    editor_name = models.CharField(max_length=200)
    num_users = models.IntegerField()

    def __str__(self):
        return "{}-{}".format(self.editor_name, self.num_users)


class Line(models.Model):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=16)
    description = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class LineUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="lines", blank=False, null=False)

    def __str__(self):
        return f"{self.user} - {self.line}"

