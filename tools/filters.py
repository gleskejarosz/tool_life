import django_filters
from django.forms import DateInput

from gemba.models import Line, PRODUCTIVE
from tools.models import OperationModel, ToolStationModel, StationModel


class OperationFilter(django_filters.FilterSet):
    STATUS_CHOICES = (
        (True, "Used"),
        (False, "In use"),
    )
    machine = django_filters.CharFilter(field_name='machine', label="Machine", lookup_expr="contains")
    station = django_filters.CharFilter(field_name='station', label="Station", lookup_expr="contains")
    tool = django_filters.CharFilter(field_name='tool_id__tool', label="Tool", lookup_expr="contains")
    tool_type = django_filters.CharFilter(field_name='tool_type', label="Tool Type", lookup_expr="contains")
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


class ToolFilter(django_filters.FilterSet):
    machine = django_filters.ModelChoiceFilter(queryset=Line.objects.filter(line_status=PRODUCTIVE).order_by("name"))
    station = django_filters.ModelChoiceFilter(queryset=StationModel.objects.all().order_by("name"))
    # station = django_filters.CharFilter(field_name='station_id__name', label="Station", lookup_expr="contains")
    tool = django_filters.CharFilter(field_name='tool', label="Tool", lookup_expr="contains")

    class Meta:
        model = ToolStationModel
        fields = ("machine", "station", "tool", )
