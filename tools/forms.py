from datetime import datetime

import pytz
from django import forms

from tools.models import StationModel


class ToolChangeForm(forms.Form):
    start_date = forms.DateTimeField(initial=datetime.now(tz=pytz.UTC))


class AddTool(forms.Form):
    station = forms.ModelChoiceField(queryset=StationModel.objects.all().order_by("name"))
    tool = forms.CharField()
