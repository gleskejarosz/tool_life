from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.urls import path

admin.autodiscover()

from gemba import views, views_export, views_report

app_name = "gemba_app"


urlpatterns = [
    path("index/", views.GembaIndex.as_view(), name="index"),
    path("admin/", admin.site.urls),
    # pareto model
    path("pareto_summary_view/", staff_member_required(views.ParetoSummary.as_view()), name="pareto-summary"),
    path("pareto_start_new", views.pareto_create_new, name="pareto-start-new"),
    path("before_close_pareto/", views.before_close_pareto, name="before-close-pareto"),
    path("final_confirmation_before_close_pareto/", views.final_confirmation_before_close_pareto,
         name="final-confirmation-before-close-pareto"),
    path("close_pareto/", views.close_pareto, name="close-pareto"),
    path("open_pareto/<pk>/", views.open_pareto, name="open-pareto"),
    path("pareto_update_view/<pk>/", staff_member_required(views.ParetoUpdateView.as_view()), name="pareto-update-view"),
    path("select_job/<pk>/", views.select_job, name="select-job"),
    # pareto detail
    path("job_user_view/", views.job_user_list, name="job-user-view"),
    path("pareto_details_create_view/", views.pareto_detail_create, name="pareto-details-create-view"),
    path("pareto_detail_view/<pk>/", staff_member_required(views.ParetoDetailView.as_view()), name="pareto-details-view"),
    path("pareto_details_update_view/<pk>/", views.pareto_detail_update, name="pareto-details-update-view"),
    path("pareto_details_delete/<pk>/", views.pareto_detail_delete, name="pareto-details-delete"),
    # pareto downtime
    path("downtime_user_view/", views.downtime_user_list, name="downtime-user-view"),
    path("downtime_detail_add/<pk>/", views.downtime_detail_create, name="downtime-detail-create"),
    path("downtime_detail_view/<pk>/", staff_member_required(views.DowntimeDetailView.as_view()), name="downtime-detail-view"),
    path("add_downtime_view/<pk>/", views.add_downtime_time, name="add-downtime-view"),
    path("pareto_ns_update_view/<pk>/", staff_member_required(views.ParetoNSUpdateView.as_view()), name="pareto-ns-update-view"),
    path("downtime_update_view/<pk>/", staff_member_required(views.DowntimeUpdateView.as_view()), name="downtime-update-view"),
    path("downtime_delete_view/<pk>/", staff_member_required(views.DowntimeDeleteView.as_view()), name="downtime-delete-view"),
    path("timer/", views.timer, name="timer"),
    path("reset_timer/", views.reset_timer, name="reset-timer"),
    # pareto scrap
    path("scrap_user_view/", views.scrap_user_list, name="scrap-user-view"),
    path("scrap_detail_add/<pk>/", views.scrap_detail_create, name="scrap-detail-create"),
    path("scrap_detail_view/<pk>/", staff_member_required(views.ScrapDetailView.as_view()), name="scrap-detail-view"),
    path("add_scrap_view/<pk>/", views.add_scrap_detail, name="add-scrap-view"),
    path("scrap_update_view/<pk>/", staff_member_required(views.ScrapUpdateView.as_view()), name="scrap-update-view"),
    path("scrap_delete_view/<pk>/", staff_member_required(views.ScrapDeleteView.as_view()), name="scrap-delete-view"),
    # daily oee report
    path("daily_oee_view/", views.pareto_view, name="pareto-view"),
    path("daily_pareto_search_result", staff_member_required(views.DailyParetoSearchResultsView.as_view()), name="daily-pareto-search-result"),
    path("pareto_details_view/<pk>/", views.pareto_detail_view, name="pareto-detail-view"),
    # produced report
    path("pareto_produced_details/", views.pareto_details_view, name="pareto-details"),
    path("pareto_details_search_result/", staff_member_required(views.ParetoDetailsSearchResultsView.as_view()),
         name="pareto-details-search-result"),
    # downtimes report
    path("downtimes_view/", views.downtimes_view, name="downtimes-view"),
    path("downtime_search_result/", staff_member_required(views.DowntimeSearchResultsView.as_view()),
         name="search-result"),
    path("lines_2/", views.lines_2, name="lines-2"),
    path("downtime_rate_report/<line_id>/", views.downtime_rate_report_by_week, name="downtime-rate-report"),
    # scraps report
    path("scraps_view/", views.scraps_view, name="scraps-view"),
    path("scrap_search_result/", staff_member_required(views.ScrapSearchResultsView.as_view()), name="scrap-search-result"),
    path("lines/", views.lines, name="lines"),
    path("scrap_rate_report/<line_id>/", views.scrap_rate_report_by_week, name="scrap-rate-report"),
    # downtimes & scrap report
    path("report_choices/", views.report_choices, name="report-choices"),
    path("scrap_downtime_compare/", views.scrap_downtime_compare, name="scrap-downtime-compare"),
    path("lines_3/", views.lines_3, name="lines-3"),
    path("downtime_scrap_set_up/<line_id>/", views.downtime_scrap_set_up, name="downtime-scrap-set-up"),
    # quarantine report
    path("quarantine_view/", views.quarantine_view, name="quarantine-view"),
    # exports and other
    path("export_scrap_csv/", views_export.export_scrap_search_csv, name="export-scrap-csv"),
    path("export_downtimes_csv/", views_export.export_downtime_search_result_csv, name="export-downtimes-csv"),
    path("export_downtimes_xls/", views_export.export_downtimes_xls, name="export-downtimes-xls"),
    path("export_daily_oee_report/", views_export.export_daily_oee_report_xls, name="export_daily_oee_report"),
    path("export_to_gemba/", views_export.gemba_export2, name="export-to-gemba"),
    path("tableau/<pk>/", views_export.tableau_export, name="tableau"),
    path("export_pareto_to_pdf/<pk>/", views_export.export_pareto_to_pdf, name="export-pareto-to-pdf"),
    path("chart/", views.EditorChartView.as_view(), name="chart"),
    # dashboard
    path("dashboard/", views_report.dashboard, name="dashboard"),
    ]
