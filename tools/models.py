from datetime import datetime

from django.db import models


class MachineModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f" {self.name}"

    class Meta:
        verbose_name_plural = "Machines"


class StationModel(models.Model):
    name = models.CharField(max_length=64)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines", blank=True, null=True)

    def __str__(self):
        return f" {self.name}"

    class Meta:
        verbose_name_plural = "Stations"


class JobModel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f" {self.name}"

    class Meta:
        verbose_name_plural = "Jobs"


class ToolModel(models.Model):
    name = models.CharField(max_length=64)

    # job_list = models.ManyToManyField("RelationModel", blank=True, null=True)

    def __str__(self):
        return f" {self.name}"

    class Meta:
        verbose_name_plural = "Tools"


class RelationModel(models.Model):
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools2", blank=True, null=True)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs", blank=True, null=True)

    def __str__(self):
        return f" {self.job}"

    class Meta:
        verbose_name_plural = "Relations"


class OperationModel(models.Model):
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE, related_name="tools", blank=True, null=True)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, related_name="machines2", blank=True, null=True)
    station = models.ForeignKey(StationModel, on_delete=models.CASCADE, related_name="stations", blank=True, null=True)
    start_date = models.DateTimeField(default=datetime.now)
    finish_date = models.DateField(blank=True, null=True)
    status = models.BooleanField(default=False)
    meters = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f" {self.tool}"


class JobUpdate(models.Model):
    date = models.DateTimeField(default=datetime.now)
    job = models.ForeignKey(JobModel, on_delete=models.CASCADE, related_name="jobs2", blank=True, null=True)
    meters = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f" {self.date} - {self.job} - {self.meters}"
