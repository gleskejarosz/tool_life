from django.contrib import admin

from gemba.models import DowntimeDetail, DowntimeModel, HourModel, LineHourModel, Pareto, ParetoDetail, ScrapDetail, ScrapModel


class ScrapDetailAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("scrap", "job", "qty", "completed", )
    list_display_links = ("scrap",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "scrap", "job", "qty", "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user"]


class DowntimeDetailAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("downtime", "job", "minutes", "completed", )
    list_display_links = ("downtime",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "downtime", "job", "minutes", "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user"]


class ParetoDetailAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("job", "qty", "good", "completed", )
    list_display_links = ("job",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "job", "qty", "good", "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user"]


class ParetoAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("pareto_date", "user", "shift", "hours", "completed", )
    list_display_links = ("pareto_date",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "pareto_date", "user", "shift", "hours", "time_stamp", "completed", "jobs", "downtimes",
                       "scrap"],
        }),
    ]
    readonly_fields = ["id", "user", "jobs", "downtimes", "scrap"]


class ScrapModelAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("code", "description", )
    list_display_links = ("code",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "code", "description"],
        }),
    ]
    readonly_fields = ["id"]


class DowntimeModelAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("code", "description", )
    list_display_links = ("code",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "code", "description"],
        }),
    ]
    readonly_fields = ["id"]


admin.site.register(Pareto, ParetoAdmin)
admin.site.register(ParetoDetail, ParetoDetailAdmin)
admin.site.register(DowntimeModel, DowntimeModelAdmin)
admin.site.register(DowntimeDetail, DowntimeDetailAdmin)
admin.site.register(HourModel)
admin.site.register(LineHourModel)
admin.site.register(ScrapModel, ScrapModelAdmin)
admin.site.register(ScrapDetail, ScrapDetailAdmin)

