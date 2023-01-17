from datetime import datetime, date

from django import forms
from django.forms import DateInput, DateTimeInput

from gemba.models import JobModel2
from tools.models import ToolModel, MachineModel, StationModel, JobUpdate, OperationModel, JobStationModel

TODAY = datetime.today().strftime('%d-%m-%Y')


# class JobAddForm(forms.Form):
#     date = forms.DateField(
#         required=True,
#         initial=TODAY,
#         widget=DateInput(format='%d/%m/%Y', attrs={"type": "date"}),
#     )
#     job = forms.ModelChoiceField(queryset=JobModel2.objects.all().order_by("name"))
#     parts = forms.IntegerField()
#
#
# class JobUpdateForm(forms.ModelForm):
#     date = forms.DateField(widget=forms.TextInput(attrs={
#         "type": "date",
#         "class": "form-control",
#         "placeholder": "date"
#     }))
#     job = forms.ModelChoiceField(queryset=JobModel2.objects.all().order_by("name"))
#     parts = forms.CharField(widget=forms.TextInput(attrs={
#         "type": "number",
#         "class": "form-control",
#         "placeholder": "parts"
#     }))
#
#     class Meta:
#         model = JobUpdate
#         fields = [
#             "date", "job", "parts"
#         ]


class ToolChangeForm(forms.Form):
    TOOL = "Tool"
    RUBBER = "Rubber"
    TOOL_CHOICES = (
        (TOOL, "Tool"),
        (RUBBER, "Rubber"),
    )
    SPARE = "Spare"

    tool_type = forms.ChoiceField(choices=TOOL_CHOICES)
    start_date = forms.DateTimeField(initial=datetime.now())

