from django.contrib import admin

from tools.models import JobModel, JobStationModel, JobUpdate, MachineModel, OperationModel, StationModel, ToolModel


class JobModelAdmin(admin.ModelAdmin):
    ordering = ("name", )
    list_display = ("name", )
    list_display_links = ("name", )
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name"],
        }),
    ]
    readonly_fields = ["id"]


class JobStationModelAdmin(admin.ModelAdmin):
    ordering = ("job", )
    list_display = ("job", "station", "machine", )
    list_display_links = ("job", )
    list_per_page = 20
    list_filter = ("machine", "station", "job", )
    fieldsets = [
        ("General", {
            "fields": ["id", "machine", "station", "job"],
        }),
    ]
    readonly_fields = ["id"]


class JobUpdateAdmin(admin.ModelAdmin):
    ordering = ("-date", )
    list_display = ("date_format", "job", "meters", )
    list_display_links = ("date_format", )
    list_per_page = 20
    list_filter = ("job", )
    fieldsets = [
        ("General", {
            "fields": ["id", "date", "job", "meters"],
        }),
    ]
    readonly_fields = ["id"]

    @staticmethod
    def date_format(obj):
        if obj is not None:
            return obj.date.strftime("%d-%m-%Y")


class MachineModelAdmin(admin.ModelAdmin):
    ordering = ("name", )
    list_display = ("name", )
    list_display_links = ("name", )
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name"],
        }),
    ]
    readonly_fields = ["id"]


class StationModelAdmin(admin.ModelAdmin):
    ordering = ("name", "num", )
    list_display = ("name", "num", )
    list_display_links = ("name", )
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name", "num"],
        }),
    ]
    readonly_fields = ["id"]


class ToolModelAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name",)
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name"],
        }),
    ]
    readonly_fields = ["id"]


class OperationModelAdmin(admin.ModelAdmin):
    ordering = ("-start_date", )
    list_display = ("tool", "tool_type", "station", "machine", "start_date", "finish_date", "status", "meters", )
    list_display_links = ("tool", )
    list_per_page = 20
    list_filter = ("machine", "station", "status", "tool", "tool_type", )
    fieldsets = [
        ("General", {
            "fields": ["id", "tool", "tool_type", "machine", "station", "start_date", "finish_date", "status",
                       "meters"],
        }),
    ]
    readonly_fields = ["id"]

    @staticmethod
    def start_date_format(obj):
        return obj.start_date.strftime("%d-%m-%Y")

    @staticmethod
    def finish_date_format(obj):
        if obj is not None:
            return obj.finish_date.strftime("%d-%m-%Y")


admin.site.register(JobModel, JobModelAdmin)
admin.site.register(JobUpdate, JobUpdateAdmin)
admin.site.register(JobStationModel, JobStationModelAdmin)
admin.site.register(MachineModel, MachineModelAdmin)
admin.site.register(OperationModel, OperationModelAdmin)
admin.site.register(StationModel, StationModelAdmin)
admin.site.register(ToolModel, ToolModelAdmin)
