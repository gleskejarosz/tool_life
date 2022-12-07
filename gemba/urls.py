from django.urls import path

from gemba import views

app_name = "gemba_app"


urlpatterns = [
    path("gemba/index/", views.GembaIndex.as_view(), name="index"),
    path("gemba/pareto_summary/", views.ParetoSummary.as_view(), name="pareto-summary"),
    path("gemba/downtimes_view/", views.downtimes_view, name="downtimes-view"),
    path("pareto_detail_view/<pk>/", views.pareto_detail_view, name="pareto-detail-view"),
    #path("add_to_pareto/<pk>/", views.add_to_pareto, name="add-to-pareto"),
    path("gemba/pareto_details_create_view/", views.pareto_detail_form, name="pareto-details-create-view"),
    path("downtime_detail_add/<pk>/", views.downtime_detail_create, name="downtime-detail-create"),
    path("scrap_detail_add/<pk>/", views.scrap_detail_create, name="scrap-detail-create"),
    path("gemba/close_pareto/", views.close_pareto, name="close-pareto"),
    path("gemba/daily_oee_report", views.daily_oee_report, name="daily-oee-report"),
    path("pareto_start_new", views.pareto_create_new, name="pareto-start-new"),
    path("downtime_user_view/", views.downtime_user_list, name="downtime-user-view"),
    path("scrap_user_view/", views.scrap_user_list, name="scrap-user-view"),
    path("job_user_view/", views.job_user_list, name="job-user-view"),
    path("scrap_detail_view/<pk>/", views.ScrapDetailView.as_view(), name="scrap-detail-view"),
    path("scrap_update_view/<pk>/", views.ScrapUpdateView.as_view(), name="scrap-update-view"),
    path("scrap_delete_view/<pk>/", views.ScrapDeleteView.as_view(), name="scrap-delete-view"),
    path("add_scrap_view/<pk>/", views.add_scrap_detail, name="add-scrap-view"),
    path("downtime_detail_view/<pk>/", views.DowntimeDetailView.as_view(), name="downtime-detail-view"),
    path("downtime_update_view/<pk>/", views.DowntimeUpdateView.as_view(), name="downtime-update-view"),
    path("downtime_delete_view/<pk>/", views.DowntimeDeleteView.as_view(), name="downtime-delete-view"),
    path("add_downtime_view/<pk>/", views.add_downtime_time, name="add-downtime-view"),
    path("add_downtime_detail/", views.add_downtime_detail, name="add-downtime-detail"),
    path("pareto_details_view/<pk>/", views.ParetoDetailView.as_view(), name="pareto-details-view"),
    path("pareto_details_update_view/<pk>/", views.ParetoDetailUpdateView.as_view(), name="pareto-details-update-view"),
    path("pareto_details_delete_view/<pk>/", views.ParetoDetailDeleteView.as_view(), name="pareto-details-delete-view"),
    ]
