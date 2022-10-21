from django.urls import path
from tools import views

app_name = "tools_app"


urlpatterns = [
    path('tools/index/', views.index, name="index"),
    # path("job-update-create-view/", views.JobUpdateCreateView.as_view(), name="job-update-create-view"),
    path("job-add-form", views.JobFormView.as_view(), name="job-add-form"),
    # path("operation-update-create-view/", views.OperationUpdateCreateView.as_view(),
    #      name="operation-update-create-view"),
    path("search-form/", views.search, name="search-form"),
    # path("search-form-2/", views.search2, name="search-form-2"),
    path("returning/", views.returning, name="returning"),
    path("operation-update-view/", views.OperationFormView.as_view(), name="operation-update-view"),
    path("export_csv/", views.export_csv, name="export_csv")
    ]
