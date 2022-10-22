import django_filters

from tools.models import JobUpdate, OperationModel


class JobFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(lookup_expr="contains", label="Date")
    job = django_filters.CharFilter(field_name='job_id__name', label="Job", lookup_expr="contains")
    meters = django_filters.CharFilter(lookup_expr="contains", label="Meters")

    class Meta:
        model = JobUpdate
        fields = "__all__"


class OperationFilter(django_filters.FilterSet):
    STATUS_CHOICES = (
        (True, "Used"),
        (False, "In use"),
    )

    station = django_filters.CharFilter(field_name='station_id__name', label="Station", lookup_expr="contains")
    start_date = django_filters.DateFilter()
    start_date_gte = django_filters.DateFilter(label="Start Date after...", field_name='start_date',
                                               lookup_expr='gte')
    start_date_lte = django_filters.DateFilter(label="Start Date before...", field_name='start_date',
                                               lookup_expr='lte')
    finish_date = django_filters.DateFilter()
    finish_date_gte = django_filters.DateFilter(label="Finish Date after...", field_name='finish_date',
                                                lookup_expr='gte')
    finish_date_lte = django_filters.DateFilter(label="Finish Date before...", field_name='finish_date',
                                                lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES, label="Status")
    meters = django_filters.NumberFilter()
    meters_lte = django_filters.NumberFilter(label="Meters less than...", field_name="meters", lookup_expr="lte")
    meters_gte = django_filters.NumberFilter(label="Meters greater than...", field_name="meters", lookup_expr="gte")

    class Meta:
        model = OperationModel
        fields = "__all__"
