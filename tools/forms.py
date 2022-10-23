from django import forms

from tools.models import ToolModel, MachineModel, StationModel, JobModel


class OperationUpdateForm(forms.Form):
    TOOL = "Tool"
    RUBBER = "Rubber"
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )

    machine = forms.ModelChoiceField(queryset=MachineModel.objects.all().order_by("name"))
    station = forms.ModelChoiceField(queryset=StationModel.objects.all().order_by("name"))
    tool = forms.ModelChoiceField(queryset=ToolModel.objects.all().order_by("name"))
    tool_type = forms.ChoiceField(choices=TOOL_CHOICES)
    start_date = forms.DateField()


class JobAddForm(forms.Form):
    date = forms.DateField()
    job = forms.ModelChoiceField(queryset=JobModel.objects.all().order_by("name"))
    meters = forms.IntegerField()
