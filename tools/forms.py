from datetime import datetime

from django import forms

from tools.models import StationModel


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


class AddTool(forms.Form):
    station = forms.ModelChoiceField(queryset=StationModel.objects.all().order_by("num"))
    tool = forms.CharField()
