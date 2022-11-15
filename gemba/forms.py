from django import forms

from tools.models import JobModel


class ParetoDetailForm(forms.Form):
    job = forms.ModelChoiceField(queryset=JobModel.objects.all().order_by("name"))
    qty = forms.IntegerField()


class DowntimeMinutes(forms.Form):
    minutes = forms.IntegerField(min_value=0)


class ScrapQuantity(forms.Form):
    qty = forms.IntegerField(min_value=0)
