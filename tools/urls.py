from django.urls import path
from tools import views

app_name = "tools_app"


urlpatterns = [
    path('tools/index/', views.index, name="index"),
    path("job-update-create-view/", views.JobUpdateCreateView.as_view(), name="job-update-create-view"),
    path("operation-update-create-view/", views.OperationUpdateCreateView.as_view(),
         name="operation-update-create-view"),
    path('search-form/', views.search, name="search-form"),
    path('search-form-2/', views.search2, name="search-form-2"),
    path('returning/', views.returning, name="returning"),
    path('completed-job/', views.completed_job, name="completed-job"),
    path('update-meters/', views.update_meters, name='update-meters'),
    ]
