from datetime import datetime

from django.db import models


class MachineModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Machine"


class StationModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Station"


class JobModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Job"


class ToolModel(models.Model):
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines",
                                blank=True, null=True)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations1",
                                blank=True, null=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Tool"


class JobStationModel(models.Model):
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines1",
                                blank=True, null=True)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations2",
                                blank=True, null=True)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs1", blank=True, null=True)

    def __str__(self):
        return f"{self.job}"

    class Meta:
        verbose_name = "Job Station"


class OperationModel(models.Model):
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools", blank=True, null=True)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines2", blank=True, null=True)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations", blank=True, null=True)
    start_date = models.DateTimeField(default=datetime.now)
    finish_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    meters = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.tool}"

    class Meta:
        verbose_name = "Tool change"


class JobUpdate(models.Model):
    date = models.DateTimeField(default=datetime.now)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs2", blank=True, null=True)
    meters = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.job} - {self.meters}"

    class Meta:
        verbose_name = "Job update"
