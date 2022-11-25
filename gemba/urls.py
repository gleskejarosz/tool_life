from django.urls import path

from gemba import views

app_name = "gemba_app"


urlpatterns = [
    path('gemba/index/', views.index, name="index"),
    path('gemba/daily_pareto/', views.daily_pareto, name="daily-pareto"),
    path('gemba/pareto_summary/', views.ParetoSummary.as_view(), name="pareto-summary"),
    path("add_to_pareto/<pk>/", views.add_to_pareto, name="add-to-pareto"),
    path("job_detail_view/<pk>/", views.DowntimeDetailView.as_view(), name="job-detail-view"),
    path("pareto_details_create_view/", views.pareto_detail_form, name="pareto-details-create-view"),
    path("downtime_detail_add/<pk>/", views.downtime_detail_create, name="downtime-detail-create"),
    path("scrap_detail_add/<pk>/", views.scrap_detail_create, name="scrap-detail-create"),
    path("close_pareto/", views.close_pareto, name="close-pareto"),
    path("assign_shift/", views.assign_shift, name="assign-shift"),
    ]