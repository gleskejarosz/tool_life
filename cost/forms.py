from django import forms

from cost.models import Table


class TableUpdateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["cost_date", "desc", "amount", "room"]


class TableCreateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["cost_date", "desc", "amount", "room"]
        widgets = {
            "cost_date": forms.DateInput(
                attrs={"type": "date", "placeholder": "dd.mm.yyyy", "class": "form-control"}
            ),
            "desc": forms.Textarea(
                attrs={'cols': 30, 'rows': 5}
            )
        }
