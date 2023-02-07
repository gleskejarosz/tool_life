import django_filters
from django.forms import DateInput
from gemba.models import Pareto, MonthlyResults


class DailyParetoFilter(django_filters.FilterSet):
    pareto_date = django_filters.DateFilter(label="Pick up date", field_name='pareto_date',
                                            widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Pareto
        fields = ["pareto_date"]


# class ParetoDetailFilter(django_filters.FilterSet):
#     pareto_date = django_filters.DateFilter()
#     pareto_date_gte = django_filters.DateFilter(label="Date after...", field_name='pareto_date',
#                                                 lookup_expr='gte', widget=DateInput(attrs={'type': 'date'}))
#     pareto_date_lte = django_filters.DateFilter(label="Date before...", field_name='pareto_date',
#                                                 lookup_expr='lte', widget=DateInput(attrs={'type': 'date'}))
#     job = django_filters.CharFilter(field_name='job_id__name', label="Job", lookup_expr="contains")
#     user = django_filters.CharFilter(field_name='user__username', label="Line / User", lookup_expr="contains")
#
#     class Meta:
#         model = ParetoDetail
#         fields = "__all__"


class DowntimeFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name='downtime__code', label="Code", lookup_expr="contains")
    description = django_filters.CharFilter(field_name='downtime__description', label="Description",
                                            lookup_expr="contains")


class ScrapFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name='scrap__code', label="Code", lookup_expr="contains")
    description = django_filters.CharFilter(field_name='scrap__description', label="Description",
                                            lookup_expr="contains")


class JobFilter(django_filters.FilterSet):
    job = django_filters.CharFilter(field_name='job__name', label="Job", lookup_expr="contains")


JANUARY = "January"
FEBRUARY = "February"
MARCH = "March"
APRIL = "April"
MAY = "May"
JUNE = "June"
JULY = "July"
AUGUST = "August"
SEPTEMBER = "September"
OCTOBER = "October"
NOVEMBER = "November"
DECEMBER = "December"

class MonthlyResultFilter(django_filters.FilterSet):
    MONTH_CHOICES = (
        (JANUARY, "January"),
        (FEBRUARY, "February"),
        (MARCH, "March"),
        (APRIL, "April"),
        (MAY, "May"),
        (JUNE, "June"),
        (JULY, "July"),
        (AUGUST, "August"),
        (SEPTEMBER, "September"),
        (OCTOBER, "October"),
        (NOVEMBER, "November"),
        (DECEMBER, "December"),
    )
    month = django_filters.ChoiceFilter(choices=MONTH_CHOICES, label="Month")

    class Meta:
        model = MonthlyResults
        fields = ("month", "line", )
