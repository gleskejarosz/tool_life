from django import forms

from cost.models import Table


class TableUpdateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["cost_date", "desc", "amount", "cat"]
        widgets = {
            "cost_date": forms.DateInput(
                attrs={"type": "date", "placeholder": "dd.mm.yyyy", "class": "form-control"}
            ),
            "desc": forms.Textarea(
                attrs={'rows': 5, "placeholder": "Opis zakupionej rzeczy", "class": "form-control"}
            )
        }


class TableCreateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["cost_date", "desc", "amount", "cat"]
        widgets = {
            "cost_date": forms.DateInput(
                attrs={"type": "date", "placeholder": "dd.mm.yyyy", "class": "form-control"}
            ),
            "desc": forms.Textarea(
                attrs={'rows': 5, "placeholder": "Opis zakupionej rzeczy", "class": "form-control"}
            )
        }
