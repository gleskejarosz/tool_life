import django_filters
from django.forms import DateInput

from tools.models import JobUpdate, OperationModel


class JobFilter(django_filters.FilterSet):
    date = django_filters.DateFilter()
    date_gte = django_filters.DateFilter(label="Date after...", field_name='date',
                                               lookup_expr='gte', widget=DateInput(attrs={'type': 'date'}))
    date_lte = django_filters.DateFilter(label="Date before...", field_name='date',
                                               lookup_expr='lte', widget=DateInput(attrs={'type': 'date'}))
    job = django_filters.CharFilter(field_name='job_id__name', label="Job", lookup_expr="contains")
    parts = django_filters.CharFilter(lookup_expr="contains", label="Parts")

    class Meta:
        model = JobUpdate
        fields = "__all__"


class OperationFilter(django_filters.FilterSet):
    STATUS_CHOICES = (
        (True, "Used"),
        (False, "In use"),
    )

    station = django_filters.CharFilter(field_name='station_id__name', label="Station", lookup_expr="contains")
    tool = django_filters.CharFilter(field_name='tool_id__name', label="Tool", lookup_expr="contains")
    start_date = django_filters.DateFilter()
    start_date_gte = django_filters.DateFilter(label="Start Date after...", field_name='start_date',
                                               lookup_expr='gte', widget=DateInput(attrs={'type': 'date'}))
    start_date_lte = django_filters.DateFilter(label="Start Date before...", field_name='start_date',
                                               lookup_expr='lte', widget=DateInput(attrs={'type': 'date'}))
    finish_date = django_filters.DateFilter()
    finish_date_gte = django_filters.DateFilter(label="Finish Date after...", field_name='finish_date',
                                                lookup_expr='gte', widget=DateInput(attrs={'type': 'date'}))
    finish_date_lte = django_filters.DateFilter(label="Finish Date before...", field_name='finish_date',
                                                lookup_expr='lte', widget=DateInput(attrs={'type': 'date'}))
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES, label="Status")
    minutes = django_filters.NumberFilter()
    minutes_lte = django_filters.NumberFilter(label="Minutes less than...", field_name="minutes", lookup_expr="lte")
    minutes_gte = django_filters.NumberFilter(label="Minutes greater than...", field_name="minutes", lookup_expr="gte")

    class Meta:
        model = OperationModel
        fields = "__all__"
