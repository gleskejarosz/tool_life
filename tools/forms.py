from datetime import datetime

from django import forms
from django.forms import DateInput

from gemba.models import JobModel2
from tools.models import ToolModel, MachineModel, StationModel

TODAY = datetime.today().strftime('%d-%m-%Y')


class OperationUpdateForm(forms.Form):
    TOOL = "Tool"
    RUBBER = "Rubber"
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )
    SPARE = "Spare"

    machine = forms.ModelChoiceField(queryset=MachineModel.objects.all().order_by("name"))
    station = forms.ModelChoiceField(queryset=StationModel.objects.all().order_by("name"))
    tool = forms.ModelChoiceField(queryset=ToolModel.objects.filter(tool_status=SPARE).order_by("name"))
    tool_type = forms.ChoiceField(choices=TOOL_CHOICES)
    start_date = forms.DateField(
        required=True,
        initial=TODAY,
        widget=DateInput(attrs={"type": "date"}),
    )


# class OperationBarcodeForm(forms.Form):
#     TOOL = "Tool"
#     RUBBER = "Rubber"
#     TOOL_CHOICES = (
#         (TOOL, "Tool"),
#         (RUBBER, "Rubber"),
#     )
#
#     machine = forms.ModelChoiceField(queryset=MachineModel.objects.all().order_by("name"))
#     station = forms.ModelChoiceField(queryset=StationModel.objects.all().order_by("name"))
#     tool = forms.CharField(label='Barcode data (tool, rubber)', max_length=64, required=True)
#     tool_type = forms.ChoiceField(choices=TOOL_CHOICES)
#     start_date = forms.DateField(
#         required=True,
#         initial=TODAY,
#         widget=DateInput(attrs={"type": "date"}, format='%Y-%m-%d'),
#     )


class JobAddForm(forms.Form):
    date = forms.DateField(
        required=True,
        initial=TODAY,
        widget=DateInput(format='%d/%m/%Y', attrs={"type": "date"}),
    )
    job = forms.ModelChoiceField(queryset=JobModel2.objects.all().order_by("name"))
    parts = forms.IntegerField()


# class JobAddBarcodeForm(forms.Form):
#     date = forms.DateField(
#         required=True,
#         initial=TODAY,
#         widget=DateInput(format='%d/%m/%Y', attrs={"type": "date"}),
#     )
#     job = forms.CharField()
#     parts = forms.IntegerField()
