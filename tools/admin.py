from django.contrib import admin

from tools.models import JobStationModel, JobUpdate, MachineModel, OperationModel, StationModel, ToolModel,\
    ToolJobModel


class JobStationModelAdmin(admin.ModelAdmin):
    ordering = ("tool",)
    list_display = ("tool", "station", "machine", )
    list_display_links = ("tool",)
    list_per_page = 20
    list_filter = ("machine", "station", "tool")
    fieldsets = [
        ("General", {
            "fields": ["id", "machine", "station", "tool"],
        }),
    ]
    readonly_fields = ["id"]


class JobUpdateAdmin(admin.ModelAdmin):
    ordering = ("-date",)
    list_display = ("date", "job", "parts", "minutes", )
    list_display_links = ("date",)
    list_per_page = 20
    list_filter = ("job",)
    fieldsets = [
        ("General", {
            "fields": ["id", "date", "job", "parts", "minutes"],
        }),
    ]
    readonly_fields = ["id"]


class MachineModelAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "machine_status", "id", )
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name", "machine_status"],
        }),
    ]
    readonly_fields = ["id"]


class StationModelAdmin(admin.ModelAdmin):
    ordering = ("name", "num",)
    list_display = ("name", "machine", "num",)
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name", "machine", "num"],
        }),
    ]
    readonly_fields = ["id"]


class ToolModelAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "tool_status", )
    list_display_links = ("name",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name", "tool_status"],
        }),
    ]
    readonly_fields = ["id"]


class OperationModelAdmin(admin.ModelAdmin):
    ordering = ("-start_date",)
    list_display = ("tool", "machine", "station", "tool_type", "start_date", "finish_date", "status", "minutes",)
    list_display_links = ("tool",)
    list_per_page = 20
    list_filter = ("status", "machine", "station", "tool_type",)
    fieldsets = [
        ("General", {
            "fields": ["id", "machine", "station", "tool", "tool_type", "start_date", "finish_date", "status", "minutes"],
        }),
    ]
    readonly_fields = ["id", "machine", "station"]


class ToolJobStationModelAdmin(admin.ModelAdmin):
    ordering = ("tool",)
    list_display = ("job", "tool",)
    list_display_links = ("job",)
    list_per_page = 20
    list_filter = ("job", "tool", )
    fieldsets = [
        ("General", {
            "fields": ["id", "job", "tool"],
        }),
    ]
    readonly_fields = ["id"]


admin.site.register(JobUpdate, JobUpdateAdmin)
admin.site.register(JobStationModel, JobStationModelAdmin)
admin.site.register(MachineModel, MachineModelAdmin)
admin.site.register(OperationModel, OperationModelAdmin)
admin.site.register(StationModel, StationModelAdmin)
admin.site.register(ToolModel, ToolModelAdmin)
admin.site.register(ToolJobModel, ToolJobStationModelAdmin)
