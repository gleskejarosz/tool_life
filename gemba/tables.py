import django_tables2 as tables

from gemba.models import ParetoDetail


class ParetoDetailHTMxMultiColumnTable(tables.Table):
    class Meta:
        model = ParetoDetail
        show_header = False
        template_name = "gemba/bootstrap_col_filter.html"
        fields = ["id", "line", "job", "output", "good", "scrap", "rework", "ops", "pareto_id", "pareto_date"]

