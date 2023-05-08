from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from tools.models import ToolStationModel, OperationModel, StationModel, ToolJobModel


class ToolStationModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("tool",)
    list_display = ("tool", "id", "station", "machine", "tool_type", "tool_status", )
    list_display_links = ("tool",)
    list_per_page = 20
    list_filter = ("machine", "station")
    fieldsets = [
        ("General", {
            "fields": ["id", "machine", "station", "tool_type", "tool", "tool_status"],
        }),
    ]
    readonly_fields = ["id"]


class StationModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("id", "name",)
    list_display_links = ("id",)
    list_per_page = 20
    fieldsets = [
        ("General", {
            "fields": ["id", "name"],
        }),
    ]
    readonly_fields = ["id"]


class OperationModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("-start_date",)
    list_display = ("tool", "machine", "station", "start_date", "tool_type", "finish_date", "status", "minutes",)
    list_display_links = ("tool",)
    list_per_page = 20
    list_filter = ("status",)
    fieldsets = [
        ("General", {
            "fields": ["id", "tool", "machine", "station", "tool_type", "start_date", "finish_date", "status", "minutes"],
        }),
    ]
    readonly_fields = ["id", "machine", "station"]


class ToolJobStationModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("tool",)
    list_display = ("job", "tool", "status", )
    list_display_links = ("job",)
    list_per_page = 20
    list_filter = ("job", "tool", )
    fieldsets = [
        ("General", {
            "fields": ["id", "job", "tool", "status"],
        }),
    ]
    readonly_fields = ["id"]


admin.site.register(ToolStationModel, ToolStationModelAdmin)
admin.site.register(OperationModel, OperationModelAdmin)
admin.site.register(StationModel, StationModelAdmin)
admin.site.register(ToolJobModel, ToolJobStationModelAdmin)
