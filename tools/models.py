from django.db import models

from gemba.models import JobModel2
from tools.utils import minutes_recalculate


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
    job = models.ForeignKey(JobModel2, on_delete=models.CASCADE, related_name="jobs1", blank=False, null=False)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Job Station"


class ToolJobModel(models.Model):
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools1", blank=False, null=False)
    job = models.ForeignKey(JobModel2, on_delete=models.CASCADE, related_name="jobs_3", blank=False, null=False)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tools vs Job"


class OperationModel(models.Model):
    TOOL = "Tool"
    RUBBER = "Rubber"
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )

    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools", blank=True, null=True)
    tool_type = models.CharField(max_length=64, choices=TOOL_CHOICES, default=TOOL)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines", blank=False,
                                null=False)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations", blank=False,
                                null=False)
    start_date = models.DateField(blank=False, null=False)
    finish_date = models.DateField(blank=True, null=True)
    status = models.BooleanField(default=False)
    minutes = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tool change"


class JobUpdate(models.Model):
    date = models.DateField(blank=False, null=False)
    job = models.ForeignKey(JobModel2, on_delete=models.CASCADE, related_name="jobs2", blank=False, null=False)
    parts = models.PositiveSmallIntegerField(default=0)
    minutes = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.job} - {self.parts}"

    class Meta:
        verbose_name = "Job update"

    def save(self, *args, **kwargs):
        self.minutes = minutes_recalculate(self.parts, self.job)
        super().save(*args, **kwargs)
