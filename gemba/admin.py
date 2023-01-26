from django.contrib import admin

from gemba.models import DowntimeDetail, DowntimeModel, LineHourModel, LineUser, Pareto, \
    ParetoDetail, ScrapDetail, ScrapModel, DowntimeUser, ScrapUser, JobModel2, Editors, Line, Timer, JobLine


class ScrapDetailAdmin(admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "line", "pareto_date", "modified", "scrap", "user", "job", "qty", "pareto_id", "completed", )
    list_display_links = ("id",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "pareto_id", "modified", "pareto_date", "scrap", "job", "qty", "from_job", "user",
                       "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "modified"]


class DowntimeDetailAdmin(admin.ModelAdmin):
    @admin.display(description='Pareto date')
    def admin_downtimes(self, obj):
        return obj.pareto_date.strftime('%d-%m-%Y')
    ordering = ("-id",)
    list_display = ("id", "line", "pareto_date", "modified", "downtime", "user", "job", "minutes", "pareto_id", "completed", )
    list_display_links = ("id",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "pareto_id", "pareto_date", "modified", "downtime", "job", "minutes", "from_job",
                       "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "modified"]


class ParetoDetailAdmin(admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "line", "pareto_date", "created", "modified", "job", "output", "good", "scrap", "takt_time",
                    "ops", "pareto_id", "completed", )
    list_display_links = ("id",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "pareto_id", "pareto_date", "created", "modified", "job", "output", "good", "scrap",
                       "ops", "takt_time", "user", "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "created", "modified"]


class ParetoAdmin(admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "pareto_date", "user", "line", "shift", "hours", "not_scheduled_to_run",
                    "availability", "performance", "quality", "oee", "completed", )
    list_display_links = ("id",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "user", "pareto_date", "time_stamp", "shift", "hours", "not_scheduled_to_run",
                       "availability", "performance", "quality", "oee", "jobs", "job_otg", "downtimes", "scrap",
                       "completed"],
        }),
    ]
    readonly_fields = ["id", "user", "jobs", "downtimes", "scrap", "availability", "performance", "quality", "oee"]


class ScrapModelAdmin(admin.ModelAdmin):
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


class DowntimeModelAdmin(admin.ModelAdmin):
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


class DowntimeUserModelAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("downtime", "line", "order", "gemba", )
    list_display_links = ("downtime",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "downtime", "line", "order", "gemba"],
        }),
    ]
    readonly_fields = ["id"]


class ScrapUserModelAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("scrap", "line", "order", "gemba", )
    list_display_links = ("scrap",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "scrap", "line", "order", "gemba"],
        }),
    ]
    readonly_fields = ["id"]


class JobModelAdmin2(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("id", "name", "target", "inner_size", "line", )
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name", "target", "inner_size", "line"],
        }),
    ]
    readonly_fields = ["id"]


class LineHourModelAdmin(admin.ModelAdmin):
    ordering = ("line",)
    list_display = ("line", "start", "shift", "id", )
    list_display_links = ("line",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "line", "start", "shift"],
        }),
    ]
    readonly_fields = ["id"]


class LineModelAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "id", "code", "description", "line_status", "calculation", )
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "code", "name", "description", "calculation", "col_vector", "downtime_rows",
                       "scrap_rows", "line_status"],
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
admin.site.register(Editors)
admin.site.register(LineUser)
admin.site.register(Timer)
admin.site.register(Line, LineModelAdmin)
admin.site.register(JobLine)
