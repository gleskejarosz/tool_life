# import django_filters
#
# from gemba.models import DowntimeDetail
#
#
# class DowntimeFilter(django_filters.FilterSet):
#     pareto_date = django_filters.DateFilter()
#     date_gte = django_filters.DateFilter(label="Pareto Date after...", field_name='pareto_date',
#                                                lookup_expr='gte')
#     date_lte = django_filters.DateFilter(label="Pareto Date before...", field_name='pareto_date',
#                                                lookup_expr='lte')
#
#     class Meta:
#         model = DowntimeDetail
#         fields = "__all__"

