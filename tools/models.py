from django.db import models

from gemba.models import JobModel2
from tools.utils import minutes_recalculate

NOT_IN_USE = "Not in use"
PRODUCTIVE = "Productive"


class MachineModel(models.Model):
    MACHINE_STATUS = (
        (NOT_IN_USE, "Not in use"),
        (PRODUCTIVE, "Productive"),
    )
    name = models.CharField(max_length=64)
    machine_status = models.CharField(max_length=64, choices=MACHINE_STATUS, default=PRODUCTIVE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Machine"


class StationModel(models.Model):
    name = models.CharField(max_length=64)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines2", blank=True,
                                null=True)
    num = models.PositiveSmallIntegerField(default=1)

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
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools2", blank=True, null=True)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tool Station"


class ToolJobModel(models.Model):
    job = models.ForeignKey(JobModel2, on_delete=models.CASCADE, related_name="jobs_3", blank=False, null=False)
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools1", blank=False, null=False)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Jobs vs Tool"


class OperationModel(models.Model):
    TOOL = "Tool"
    RUBBER = "Rubber"
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )

    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools", blank=False, default="")
    tool_type = models.CharField(max_length=64, choices=TOOL_CHOICES, default=TOOL)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines", blank=True,
                                null=True)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations", blank=True,
                                null=True)
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
