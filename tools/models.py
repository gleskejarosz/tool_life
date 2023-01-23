from django.db import models

from gemba.models import JobModel2, Line

SPARE = "Spare"
USE = "In use"
SCRAPPED = "Scrapped"
TOOL = "Tool"
RUBBER = "Rubber"


class StationModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Station"


class ToolModel(models.Model):
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
        verbose_name = "Tool to delete"


class ToolStationModel(models.Model):
    TOOL_STATUS = (
        (SPARE, "Spare"),
        (USE, "In use"),
        (SCRAPPED, "Scrapped"),
    )
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )
    machine = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="lines10", blank=False, null=False)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations1", blank=False,
                                null=False)
    tool = models.CharField(max_length=64)
    tool_type = models.CharField(max_length=64, choices=TOOL_CHOICES, default=TOOL)
    tool_status = models.CharField(max_length=64, choices=TOOL_STATUS, default=SPARE)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tool"


class ToolJobModel(models.Model):
    job = models.ForeignKey(JobModel2, on_delete=models.CASCADE, related_name="jobs_3", blank=False, null=False)
    tool = models.ForeignKey(ToolStationModel, on_delete=models.CASCADE, related_name="tools1", blank=False, null=False)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Jobs vs Tool"


class OperationModel(models.Model):
    machine = models.CharField(max_length=64, blank=True, null=True)
    station = models.CharField(max_length=64, blank=True, null=True)
    tool = models.ForeignKey(ToolStationModel, on_delete=models.CASCADE, related_name="tools5", blank=True, null=True)
    tool_type = models.CharField(max_length=64, blank=True, null=True)
    start_date = models.DateTimeField()
    finish_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    minutes = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tool change"
