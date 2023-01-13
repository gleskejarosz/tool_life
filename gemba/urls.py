from django.urls import path

from gemba import views


app_name = "gemba_app"


urlpatterns = [
    path("index/", views.GembaIndex.as_view(), name="index"),
    path("pareto_summary_view/", views.ParetoSummary.as_view(), name="pareto-summary"),
    path("downtimes_view/", views.downtimes_view, name="downtimes-view"),
    path("scraps_view/", views.scraps_view, name="scraps-view"),
    path("pareto_view/", views.pareto_view, name="pareto-view"),
    path("pareto-details/", views.pareto_details_query, name="pareto-details"),
    path("pareto_detail_view/<pk>/", views.pareto_detail_view, name="pareto-detail-view"),
    path("pareto_details_create_view/", views.pareto_detail_create, name="pareto-details-create-view"),
    path("downtime_detail_add/<pk>/", views.downtime_detail_create, name="downtime-detail-create"),
    path("scrap_detail_add/<pk>/", views.scrap_detail_create, name="scrap-detail-create"),
    path("close_pareto/", views.close_pareto, name="close-pareto"),
    path("final_confirmation_before_close_pareto/", views.final_confirmation_before_close_pareto,
         name="final-confirmation-before-close-pareto"),
    path("before_close_pareto/", views.before_close_pareto, name="before-close-pareto"),
    path("pareto_start_new", views.pareto_create_new, name="pareto-start-new"),
    path("job_user_view/", views.job_user_list, name="job-user-view"),
    path("downtime_user_view/", views.downtime_user_list, name="downtime-user-view"),
    path("scrap_user_view/", views.scrap_user_list, name="scrap-user-view"),
    path("search_result/", views.SearchResultsView.as_view(), name="search-result"),
    path("scrap_search_result/", views.ScrapSearchResultsView.as_view(), name="scrap-search-result"),
    path("daily_pareto_search_result", views.DailyParetoSearchResultsView.as_view(), name="daily-pareto-search-result"),
    path("scrap_detail_view/<pk>/", views.ScrapDetailView.as_view(), name="scrap-detail-view"),
    path("pareto_update_view/<pk>/", views.ParetoUpdateView.as_view(), name="pareto-update-view"),
    path("pareto_ns_update_view/<pk>/", views.ParetoNSUpdateView.as_view(), name="pareto-ns-update-view"),
    path("scrap_update_view/<pk>/", views.ScrapUpdateView.as_view(), name="scrap-update-view"),
    path("scrap_delete_view/<pk>/", views.ScrapDeleteView.as_view(), name="scrap-delete-view"),
    path("add_scrap_view/<pk>/", views.add_scrap_detail, name="add-scrap-view"),
    path("downtime_detail_view/<pk>/", views.DowntimeDetailView.as_view(), name="downtime-detail-view"),
    path("downtime_update_view/<pk>/", views.DowntimeUpdateView.as_view(), name="downtime-update-view"),
    path("downtime_delete_view/<pk>/", views.DowntimeDeleteView.as_view(), name="downtime-delete-view"),
    path("add_downtime_view/<pk>/", views.add_downtime_time, name="add-downtime-view"),
    path("pareto_details_view/<pk>/", views.ParetoDetailView.as_view(), name="pareto-details-view"),
    path("pareto_details_update_view/<pk>/", views.ParetoDetailUpdateView.as_view(), name="pareto-details-update-view"),
    path("pareto_details_delete_view/<pk>/", views.ParetoDetailDeleteView.as_view(), name="pareto-details-delete-view"),
    path("quarantine_view/", views.quarantine_view, name="quarantine-view"),
    path("export_scrap_csv/", views.export_scrap_search_csv, name="export-scrap-csv"),
    path("export_downtimes_csv/", views.export_downtime_search_result_csv, name="export-downtimes-csv"),
    path("export_downtimes_xls/", views.export_downtimes_xls, name="export-downtimes-xls"),
    path("export_daily_oee_report/", views.export_daily_oee_report_xls, name="export_daily_oee_report"),
    path("select_job/<pk>/", views.select_job, name="select-job"),
    path("tableau/<pk>/", views.tableau_export, name="tableau"),
    path("chart/", views.EditorChartView.as_view(), name="chart"),
    ]
