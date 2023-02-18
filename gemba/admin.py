from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from gemba.models import DowntimeDetail, DowntimeModel, LineHourModel, LineUser, Pareto, \
    ParetoDetail, ScrapDetail, ScrapModel, DowntimeUser, ScrapUser, JobModel2, Line, Timer, JobLine, \
    MonthlyResults, QuarantineHistoryDetail


class ScrapDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "line", "pareto_date", "modified", "scrap", "user", "job", "qty", "pareto_id", "completed", )
    list_display_links = ("id",)
    list_per_page = 20
    list_filter = ("line",)
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "pareto_id", "modified", "pareto_date", "scrap", "job", "qty", "from_job", "user",
                       "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "modified"]


class DowntimeDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    @admin.display(description='Pareto date')
    def admin_downtimes(self, obj):
        return obj.pareto_date.strftime('%d-%m-%Y')
    ordering = ("-id",)
    list_display = ("id", "line", "pareto_date", "modified", "downtime", "user", "job", "minutes", "pareto_id", "completed", )
    list_display_links = ("id",)
    list_per_page = 20
    list_filter = ("line",)
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "pareto_id", "pareto_date", "modified", "downtime", "job", "minutes", "from_job",
                       "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "modified"]


class ParetoDetailAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "line", "pareto_date", "created", "modified", "job", "output", "good", "scrap", "takt_time",
                    "ops", "pareto_id", "completed", )
    list_display_links = ("id",)
    list_filter = ("line",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "pareto_id", "pareto_date", "created", "modified", "job", "output", "good", "scrap",
                       "ops", "takt_time", "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "created", "modified"]


class ParetoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "pareto_date", "user", "line", "shift", "hours", "not_scheduled_to_run",
                    "availability", "performance", "quality", "oee", "completed", "ops_otg", )
    list_display_links = ("id",)
    list_per_page = 20
    list_filter = ("line", "shift",)
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "user", "pareto_date", "time_stamp", "shift", "hours", "not_scheduled_to_run",
                       "availability", "performance", "quality", "oee", "jobs", "job_otg", "downtimes", "scrap",
                       "ops_otg", "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "jobs", "downtimes", "scrap", "availability", "performance", "quality", "oee"]


class ScrapModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("code",)
    list_display = ("code", "description", "rework", )
    list_display_links = ("code",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "code", "description", "rework"],
        }),
    ]
    readonly_fields = ["id"]


class DowntimeModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("code",)
    list_display = ("code", "description", )
    list_display_links = ("code",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "code", "description"],
        }),
    ]
    readonly_fields = ["id"]


class DowntimeUserModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("downtime", "line", "order", "gemba", )
    list_display_links = ("downtime",)
    list_filter = ("line",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "downtime", "line", "order", "gemba"],
        }),
    ]
    readonly_fields = ["id"]


class ScrapUserModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("scrap", "line", "order", "gemba", )
    list_display_links = ("scrap",)
    list_per_page = 20
    list_filter = ("line",)
    fieldsets = [
        ("General", {
            "fields": ["id", "scrap", "line", "order", "gemba"],
        }),
    ]
    readonly_fields = ["id"]


class JobModelAdmin2(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("id", "name", "inner_size", )
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name", "inner_size"],
        }),
    ]
    readonly_fields = ["id"]


class LineHourModelAdmin(admin.ModelAdmin):
    ordering = ("line",)
    list_display = ("line", "start", "shift", "id", )
    list_display_links = ("line",)
    list_per_page = 20
    list_filter = ("line",)
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "start", "shift"],
        }),
    ]
    readonly_fields = ["id"]


class LineModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "id", "code", "description", "line_status", "calculation", "target", )
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "code", "name", "description", "calculation", "line_status", "target"],
        }),
    ]
    readonly_fields = ["id"]


class JobLineModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("job",)
    list_display = ("job", "target", "line", "factor")
    list_display_links = ("job",)
    list_per_page = 20
    list_filter = ("line",)
    fieldsets = [
        ("General", {
            "fields": ["id", "job", "target", "line", "factor"],
        }),
    ]
    readonly_fields = ["id"]


class TimerModelAdmin(admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("user", "start",)
    list_display_links = ("user",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "user", "start", "end", "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "start", "end", "completed"]


class MonthlyResultsAdmin(admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("year", "month", "line", "total_output", "total_good", "total_scrap", "total_rework")
    list_display_links = ("line",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "year", "month", "line", "total_output", "total_good", "total_scrap", "total_rework",
                       "total_available_time", "total_availability", "total_performance", "total_quality", "total_oee",
                       "counter"],
        }),
    ]
    readonly_fields = ["id"]


admin.site.register(Pareto, ParetoAdmin)
admin.site.register(ParetoDetail, ParetoDetailAdmin)
admin.site.register(DowntimeModel, DowntimeModelAdmin)
admin.site.register(DowntimeDetail, DowntimeDetailAdmin)
admin.site.register(LineHourModel, LineHourModelAdmin)
admin.site.register(ScrapModel, ScrapModelAdmin)
admin.site.register(ScrapDetail, ScrapDetailAdmin)
admin.site.register(DowntimeUser, DowntimeUserModelAdmin)
admin.site.register(ScrapUser, ScrapUserModelAdmin)
admin.site.register(JobModel2, JobModelAdmin2)
admin.site.register(LineUser)
admin.site.register(Timer, TimerModelAdmin)
admin.site.register(Line, LineModelAdmin)
admin.site.register(JobLine, JobLineModelAdmin)
admin.site.register(MonthlyResults, MonthlyResultsAdmin)
admin.site.register(QuarantineHistoryDetail)
