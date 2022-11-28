from django.urls import path

from gemba import views

app_name = "gemba_app"


urlpatterns = [
    path("gemba/index/", views.GembaIndex.as_view(), name="index"),
    path("gemba/daily_pareto/", views.daily_pareto, name="daily-pareto"),
    path("gemba/pareto_summary/", views.ParetoSummary.as_view(), name="pareto-summary"),
    path("gemba/pareto_view/", views.pareto_view, name="pareto-view"),
    path("pareto_detail_view/<pk>/", views.pareto_detail_view, name="pareto-detail-view"),
    path("add_to_pareto/<pk>/", views.add_to_pareto, name="add-to-pareto"),
    path("gemba/pareto_details_create_view/", views.pareto_detail_form, name="pareto-details-create-view"),
    path("downtime_detail_add/<pk>/", views.downtime_detail_create, name="downtime-detail-create"),
    path("scrap_detail_add/<pk>/", views.scrap_detail_create, name="scrap-detail-create"),
    path("gemba/close_pareto/", views.close_pareto, name="close-pareto"),
    path("gemba/assign_shift/", views.assign_shift, name="assign-shift"),
    path("gemba/daily_oee_report", views.daily_oee_report, name="daily-oee-report"),
    ]