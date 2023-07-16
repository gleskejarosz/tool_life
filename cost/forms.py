from django import forms

from cost.models import Table, Contents


class TableUpdateForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["cost_date", "desc", "amount", "cat"]
        widgets = {
            "cost_date": forms.DateInput(
                attrs={"type": "date", "placeholder": "dd.mm.yyyy", "class": "form-control"}
            ),
            "desc": forms.Textarea(
                attrs={'rows': 5, "class": "form-control"}
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


class ContentsUpdateForm(forms.ModelForm):
    class Meta:
        model = Contents
        fields = "__all__"
        widgets = {
            "desc": forms.Textarea(
                attrs={'rows': 5, "class": "form-control"}
            )
        }


class ContentsCreateForm(forms.ModelForm):
    class Meta:
        model = Contents
        fields = "__all__"
        widgets = {
            "desc": forms.Textarea(
                attrs={'rows': 5, "placeholder": "Zawartość pudełka", "class": "form-control"}
            )
        }
