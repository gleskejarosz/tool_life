from django.urls import path
from tools import views

app_name = "tools_app"


urlpatterns = [
    path('tools/index/', views.index, name="index"),
    path("job-add-form", views.JobFormView.as_view(), name="job-add-form"),
    path("search-form/", views.search, name="search-form"),
    path("returning/", views.returning, name="returning"),
    path("operation-update-view/", views.OperationFormView.as_view(), name="operation-update-view"),
    path("export_csv/", views.export_csv, name="export_csv"),
    path("export_csv2/", views.export_csv2, name="export_csv2"),
    ]
