from django import forms

from gemba.models import SHIFT_CHOICES, HOUR_CHOICES, DowntimeModel
from tools.models import JobModel


class ParetoDetailForm(forms.Form):
    job = forms.ModelChoiceField(queryset=JobModel.objects.all().order_by("name"))
    qty = forms.IntegerField(label="Output")
    good = forms.IntegerField()


class DowntimeAdd(forms.Form):
    downtime = forms.ModelChoiceField(queryset=DowntimeModel.objects.all().order_by("code"))
    minutes = forms.IntegerField()


class DowntimeJobAdd(forms.Form):
    job = forms.ModelChoiceField(queryset=JobModel.objects.all().order_by("name"))
    downtime = forms.ModelChoiceField(queryset=DowntimeModel.objects.all().order_by("code"))
    minutes = forms.IntegerField()


class DowntimeMinutes(forms.Form):
    minutes = forms.IntegerField(min_value=0)


class DowntimeMinutesJob(forms.Form):
    minutes = forms.IntegerField(min_value=0)
    job = forms.ModelChoiceField(queryset=JobModel.objects.all().order_by("name"))


class ScrapQuantity(forms.Form):
    qty = forms.IntegerField(min_value=0)


class ScrapQuantityJob(forms.Form):
    qty = forms.IntegerField(min_value=0)
    job = forms.ModelChoiceField(queryset=JobModel.objects.all().order_by("name"))


class NewPareto(forms.Form):
    shift = forms.ChoiceField(choices=SHIFT_CHOICES)
    hours = forms.ChoiceField(choices=HOUR_CHOICES)
