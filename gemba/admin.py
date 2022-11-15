from django.contrib import admin

from gemba.models import DowntimeDetail, DowntimeModel, Pareto, ParetoDetail, ScrapDetail, ScrapModel

admin.site.register(Pareto)
admin.site.register(ParetoDetail)
admin.site.register(DowntimeModel)
admin.site.register(DowntimeDetail)
admin.site.register(ScrapModel)
admin.site.register(ScrapDetail)
