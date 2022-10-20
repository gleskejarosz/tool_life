from datetime import datetime

from django import forms
from django.http import request
from django.shortcuts import render

from tools.models import ToolModel, MachineModel, StationModel, OperationModel, JobModel


class OperationUpdateForm(forms.Form):
    machine = forms.ModelChoiceField(queryset=MachineModel.objects.all())
    station = forms.ModelChoiceField(queryset=StationModel.objects.all())
    tool = forms.ModelChoiceField(queryset=ToolModel.objects.all())
    start_date = forms.DateTimeField()


class JobAddForm(forms.Form):
    date = forms.DateTimeField()
    job = forms.ModelChoiceField(queryset=JobModel.objects.all())
    meters = forms.IntegerField()
