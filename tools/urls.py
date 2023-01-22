from django.urls import path
from tools import views

app_name = "tools_app"


urlpatterns = [
    path('tools/index/', views.index, name="index"),
    path("tool_actions/", views.tool_actions_view, name="tool-actions"),
    path("select_tool/", views.select_tool, name="select-tool"),
    path("change_tool/<tool_id>/", views.change_tool, name="change-tool"),
    path("add_tool/<machine_id>/", views.add_tool, name="add-tool"),
    # reports
    path("in_use/", views.tool_in_use, name="in-use"),
    path("machines_view/", views.machines_view, name="machines"),
    path("machines_view_3/", views.machines_view_3, name="machines-3"),
    path("tools_vs_jobs/<machine_id>", views.tools_vs_jobs, name="tools-vs-jobs"),
    path("tools_vs_jobs_table/<machine_id>", views.tools_vs_jobs_table, name="tools-vs-jobs-table"),
    path("update_tool_vs_job/<pk>/", views.update_tool_vs_job, name="update-tools-vs-jobs"),
    path("machines_tools_view/", views.machines_view2, name="tools-machines"),
    path("tools/<machine_id>", views.tools_on_the_machine, name="tools"),
    path("export_csv/", views.export_csv, name="export_csv"),
    ]
