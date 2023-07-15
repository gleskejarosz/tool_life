from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from cost.models import Table


class CostTableAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    ordering = ("-id",)
    list_display = ("id", "cost_date", "desc", "amount", "cat", )
    list_display_links = ("id",)
    list_per_page = 20
    list_filter = ("cost_date", "cat")
    fieldsets = [
        ("General", {
            "fields": ["id", "cost_date", "desc", "amount", "cat"],
        }),
    ]
    readonly_fields = ["id"]


admin.site.register(Table, CostTableAdmin)
