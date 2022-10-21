from django import forms

from tools.models import ToolModel, MachineModel, StationModel, JobModel


class OperationUpdateForm(forms.Form):
    machine = forms.ModelChoiceField(queryset=MachineModel.objects.all())
    station = forms.ModelChoiceField(queryset=StationModel.objects.all())
    tool = forms.ModelChoiceField(queryset=ToolModel.objects.all())
    start_date = forms.DateField()


class JobAddForm(forms.Form):
    date = forms.DateField()
    job = forms.ModelChoiceField(queryset=JobModel.objects.all())
    meters = forms.IntegerField()
