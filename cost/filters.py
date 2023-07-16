import django_filters
from django.forms import DateInput
from django_filters import ChoiceFilter

from cost.models import Table, ROOM_CHOICES


class DailyResultFilter(django_filters.FilterSet):
    cost_date = django_filters.DateFilter(label="Date", field_name='cost_date',
                                          widget=DateInput(attrs={'type': 'date'}))
    cat = ChoiceFilter(choices=ROOM_CHOICES, label="Category")

    class Meta:
        model = Table
        fields = ("cost_date", "cat", )

