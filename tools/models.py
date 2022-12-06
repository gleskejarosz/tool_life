from django.db import models

# from gemba.models import DowntimeGroup
from tools.utils import hours_recalculate


class MachineModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Machine"


class StationModel(models.Model):
    name = models.CharField(max_length=64)
    num = models.DecimalField(default=100, max_digits=3, decimal_places=0, blank=False, null=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Station"


class JobModel(models.Model):
    name = models.CharField(max_length=64)
    target = models.IntegerField(default=1615)
    inner_size = models.PositiveSmallIntegerField(default=0)
    # group = models.ForeignKey(DowntimeGroup, on_delete=models.CASCADE, related_name="job_group_", blank=False,
    #                           null=False)
    # order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Job"


class ToolModel(models.Model):
    SPARE = "Spare"
    USE = "In use"
    SCRAPPED = "Scrapped"
    TOOL_STATUS = (
        (SPARE, "Spare"),
        (USE, "In use"),
        (SCRAPPED, "Scrapped"),
    )
    name = models.CharField(max_length=64)
    tool_status = models.CharField(max_length=64, choices=TOOL_STATUS, default=SPARE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Tool"


class JobStationModel(models.Model):
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines1", blank=False,
                                null=False)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations2", blank=False,
                                null=False)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs1", blank=False, null=False)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Job Station"


class OperationModel(models.Model):
    TOOL = "Tool"
    RUBBER = "Rubber"
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )

    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools", blank=True, null=True)
    tool_type = models.CharField(max_length=64, choices=TOOL_CHOICES, default=TOOL)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines2", blank=False,
                                null=False)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations", blank=False,
                                null=False)
    start_date = models.DateField(blank=False, null=False)
    finish_date = models.DateField(blank=True, null=True)
    status = models.BooleanField(default=False)
    hours = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tool change"


class JobUpdate(models.Model):
    date = models.DateField(blank=False, null=False)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs2", blank=False, null=False)
    parts = models.PositiveSmallIntegerField(default=0)
    hours = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.date} - {self.job} - {self.parts}"

    class Meta:
        verbose_name = "Job update"

    def save(self, *args, **kwargs):
        self.hours = hours_recalculate(self.parts, self.job)
        super().save(*args, **kwargs)

