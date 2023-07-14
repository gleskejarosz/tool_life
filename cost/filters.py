import django_filters
from django.forms import DateInput

from cost.models import Table


class DailyResultFilter(django_filters.FilterSet):
    cost_date = django_filters.DateFilter(label="Pick up date", field_name='cost_date',
                                          widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Table
        fields = ("cost_date", "room", )
