from django.urls import path
from tools import views

app_name = "tools_app"


urlpatterns = [
    path('tools/index/', views.index, name="index"),
    path("job_add_form", views.JobFormView.as_view(), name="job-add-form"),
    path("job_detail_view/<pk>/", views.JobDetailView.as_view(), name="job-detail-view"),
    path("job_update/<pk>/", views.job_update, name="job-update-view"),
    path("job_delete_view/<pk>/", views.JobDeleteView.as_view(), name="job-delete-view"),
    path("job_list_view", views.JobListView.as_view(), name="job-list-view"),
    path("jobs", views.jobs, name="jobs"),
    path("search_form/", views.search, name="search-form"),
    path("returning/", views.returning, name="returning"),
    path("in_use/", views.tool_in_use, name="in-use"),
    # path("operation_change_tool/", views.OperationFormView.as_view(), name="operation-update-view"),
    path("export_csv/", views.export_csv, name="export_csv"),
    path("export_csv2/", views.export_csv2, name="export_csv2"),
    path("update_parts/", views.update_parts, name="update-parts"),

    path("select_tool/", views.select_tool, name="select-tool"),
    path("change_tool/<tool_id>/", views.change_tool, name="change-tool"),

    path("machines_view/", views.machines_view, name="machines"),
    path("tools_vs_jobs/<machine_id>", views.tools_vs_jobs_table, name="tools_vs_jobs"),
    path("machines_tools_view/", views.machines_view2, name="tools-machines"),
    path("tools/<machine_id>", views.tools, name="tools"),
    ]
