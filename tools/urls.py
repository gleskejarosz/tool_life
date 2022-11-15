from django.urls import path
from tools import views

app_name = "tools_app"


urlpatterns = [
    path('tools/index/', views.index, name="index"),
    path("job_add_form", views.JobFormView.as_view(), name="job-add-form"),
    path("job_detail_view/<pk>/", views.JobDetailView.as_view(), name="job-detail-view"),
    path("job_update_view/<pk>/", views.JobUpdateView.as_view(), name="job-update-view"),
    path("job_delete_view/<pk>/", views.JobDeleteView.as_view(), name="job-delete-view"),
    path("job_list_view", views.JobListView.as_view(), name="job-list-view"),
    path("jobs", views.jobs, name="jobs"),
    path("job_add_barcode_form", views.JobFormBarcodeView.as_view(), name="job-add-barcode-form"),
    path("search_form/", views.search, name="search-form"),
    path("returning/", views.returning, name="returning"),
    path("in_use/", views.tool_in_use, name="in-use"),
    path("operation_update_view/", views.OperationFormView.as_view(), name="operation-update-view"),
    path("operation_barcode_view/", views.OperationBarcodeFormView.as_view(), name="operation-barcode-view"),
    path("export_csv/", views.export_csv, name="export_csv"),
    path("export_csv2/", views.export_csv2, name="export_csv2"),
    path("update_parts/", views.update_parts, name="update-parts"),
    ]
