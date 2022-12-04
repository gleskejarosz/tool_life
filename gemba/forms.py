from django import forms
from django.contrib.auth.models import User

from gemba.models import SHIFT_CHOICES, HOUR_CHOICES, DowntimeModel, DowntimeGroup, JobUser
from tools.models import JobModel


class ParetoDetailForm(forms.Form):
    # def __init__(self, user, *args, **kwargs):
    #     super(ParetoDetailForm, self).__init__(*args, **kwargs)
    #     group = DowntimeGroup.objects.get(user=user)
    #     self.fields['job'].queryset = JobUser.objects.filter(group=group)
    #
    # # job =
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
