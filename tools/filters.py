import django_filters
from tools.models import JobUpdate, OperationModel


class JobFilter(django_filters.FilterSet):
    date = django_filters.CharFilter(lookup_expr="contains", label="Date")
    # job = django_filters.CharFilter(lookup_expr="contains", label="Job")
    meters = django_filters.CharFilter(lookup_expr="contains", label="Meters")

    class Meta:
        model = JobUpdate
        fields = "__all__"


class OperationFilter(django_filters.FilterSet):
    start_date = django_filters.CharFilter(lookup_expr="contains", label="Start date")
    finish_date = django_filters.CharFilter(lookup_expr="contains", label="Finish date")
    meters = django_filters.CharFilter(lookup_expr="contains", label="Meters")

    class Meta:
        model = OperationModel
        fields = "__all__"
