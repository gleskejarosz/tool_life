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
    path("pareto_update_view/<pk>/", staff_member_required(views.ParetoUpdateView.as_view()),
         name="pareto-update-view"),
    path("select_job/<pk>/", views.select_job, name="select-job"),
    path("finished_update_view/<pk>/", staff_member_required(views.FinishedUpdateView.as_view()),
         name="finished-update-view"),
    # pareto detail
    path("job_user_view/", views.job_user_list, name="job-user-view"),
    path("pareto_details_create_view/", views.pareto_detail_create, name="pareto-details-create-view"),
    path("pareto_detail_view/<pk>/", staff_member_required(views.ParetoDetailView.as_view()),
         name="pareto-details-view"),
    path("pareto_details_update_view/<pk>/", views.pareto_detail_update, name="pareto-details-update-view"),
    path("pareto_details_delete/<pk>/", views.pareto_detail_delete, name="pareto-details-delete"),
    # pareto downtime
    path("downtime_user_view/", views.downtime_user_list, name="downtime-user-view"),
    path("downtime_detail_add/<pk>/", views.downtime_detail_create, name="downtime-detail-create"),
    path("downtime_detail_view/<pk>/", staff_member_required(views.DowntimeDetailView.as_view()),
         name="downtime-detail-view"),
    path("add_downtime_view/<pk>/", views.add_downtime_time, name="add-downtime-view"),
    path("pareto_ns_update_view/<pk>/", staff_member_required(views.ParetoNSUpdateView.as_view()),
         name="pareto-ns-update-view"),
    path("downtime_update_view/<pk>/", staff_member_required(views.DowntimeUpdateView.as_view()),
         name="downtime-update-view"),
    path("downtime_delete_view/<pk>/", staff_member_required(views.DowntimeDeleteView.as_view()),
         name="downtime-delete-view"),
    path("timer/", views.timer, name="timer"),
    path("reset_timer/", views.reset_timer, name="reset-timer"),
    # pareto scrap
    path("scrap_user_view/", views.scrap_user_list, name="scrap-user-view"),
    path("scrap_detail_add/<pk>/", views.scrap_detail_create, name="scrap-detail-create"),
    path("scrap_detail_view/<pk>/", staff_member_required(views.ScrapDetailView.as_view()), name="scrap-detail-view"),
    path("add_scrap_view/<pk>/", views.add_scrap_detail, name="add-scrap-view"),
    path("scrap_update_view/<pk>/", views.scrap_update_view, name="scrap-update-view"),
    path("scrap_delete_view/<pk>/", staff_member_required(views.ScrapDeleteView.as_view()), name="scrap-delete-view"),
    # daily oee report
    path("daily_oee_view/", views.pareto_view, name="pareto-view"),
    path("daily_oee_report/", views.daily_oee_report, name="daily-oee-report"),
    path("daily_oee_report_by_shift/<pareto_date>/", views.daily_oee_report_by_shift, name="daily-oee-report_by-shift"),

    path("pareto_details_view/<pk>/", views.pareto_detail_view, name="pareto-detail-view"),
    # pareto view
    path("report_choices_2/", views.report_choices_2, name="report-choices-2"),
    path("paretos_view/", views.paretos_view, name="paretos-view"),
    path("paretos_view_choices/<line>/<date_from>/<date_to>/", views.paretos_view_choices, name="paretos-view-choices"),

    path("report_choices_3/", views_report.report_choices_3, name="report-choices-3"),
    path("weekly_report_by_line/", views_report.weekly_report_by_line, name="weekly-report-by-line"),

    # produced report
    path("pareto_produced_details/", views.pareto_details_view, name="pareto-details"),
    path("pareto_details_search_result/", staff_member_required(views.ParetoDetailsSearchResultsView.as_view()),
         name="pareto-details-search-result"),
    # downtimes report
    path("downtimes_view/", views.downtimes_view, name="downtimes-view"),
    path("downtime_search_result/", staff_member_required(views.DowntimeSearchResultsView.as_view()),
         name="search-result"),
    path("lines_2/", views_report.lines_2, name="lines-2"),
    path("downtime_rate_report/", views_report.downtime_rate_report_by_week,
         name="downtime-rate-report"),
    path("previous_downtime_rate_report/<line_id>/<base_day>/", views_report.previous_downtime_rate_report_by_week,
         name="previous-downtime-rate-report"),
    path("next_downtime_rate_report/<line_id>/<base_day>/", views_report.next_downtime_rate_report_by_week,
         name="next-downtime-rate-report"),
    path("display_downtime_in_a_week/<line_id>/<base_day>/<week_no>/<down_id>/<down_rate>/",
         views_report.display_downtime_in_a_week, name="display-downtime-in-a-week"),
    # scraps report
    path("scraps_view/", views.scraps_view, name="scraps-view"),
    path("scrap_search_result/", staff_member_required(views.ScrapSearchResultsView.as_view()),
         name="scrap-search-result"),
    path("lines/", views_report.lines, name="lines"),
    path("scrap_rate_report/", views_report.scrap_rate_report_by_week, name="scrap-rate-report"),
    path("previous_scrap_rate_report/<line_id>/<base_day>/", views_report.previous_scrap_rate_report_by_week,
         name="previous-scrap-rate-report"),
    path("next_scrap_rate_report/<line_id>/<base_day>/", views_report.next_scrap_rate_report_by_week,
         name="next-scrap-rate-report"),
    path("display_scrap_in_a_week/<line_id>/<base_day>/<week_no>/<scrap_id>/<scrap_rate>/",
         views_report.display_scrap_in_a_week, name="display-scrap-in-a-week"),
    # downtimes & scrap report
    path("report_choices/", views.report_choices, name="report-choices"),
    path("scrap_downtime_compare/", views.scrap_downtime_compare, name="scrap-downtime-compare"),
    path("lines_3/", views.lines_3, name="lines-3"),
    path("downtime_scrap_set_up/<line_id>/", views.downtime_scrap_set_up, name="downtime-scrap-set-up"),
    # quarantine report
    path("quarantine_view/", views.quarantine_view, name="quarantine-view"),
    path("quarantine_detail/<scrap_id>/", views.pareto_quarantine_view, name="quarantine-detail"),
    path("quarantine_case_detail/<scrap_id>/<pareto_id>/", views.create_quarantine_historic_detail,
         name="quarantine-case-detail"),
    path("create_quarantined_scrap/<pk>/", views.create_quarantined_scrap, name="create-quarantined-scrap"),
    path("update_good_quarantine/<pk>/", staff_member_required(views.GoodUpdateView.as_view()),
         name="update-good-quarantine"),
    path("quarantine_case_summary/", views.quarantine_summary, name="quarantine-case-summary"),
    # exports and other
    path("export_scrap_csv/", views_export.export_scrap_search_csv, name="export-scrap-csv"),
    path("export_downtimes_csv/", views_export.export_downtime_search_result_csv, name="export-downtimes-csv"),
    path("export_downtimes_xls/", views_export.export_downtimes_xls, name="export-downtimes-xls"),
    path("export_daily_oee_report/", views_export.export_daily_oee_report_xls, name="export_daily_oee_report"),
    path("export_to_gemba/", views_export.gemba_export2, name="export-to-gemba"),
    path("tableau/<pk>/", views_export.tableau_export, name="tableau"),
    path("export_pareto_to_pdf/<pk>/", views_export.export_pareto_to_pdf, name="export-pareto-to-pdf"),
    path("export_job_model_csv/", views_export.export_job_model_csv, name="export-job-model-csv"),
    path("export_job_model_xls/", views_export.export_job_model_xls, name="export-job-model-xls"),
    path("update_database/", views_export.update_database_many_to_many_field, name="update-database"),
    # dashboard
    path("dashboard/", views_report.dashboard, name="dashboard"),
    path("dashboard2/", views_report.test_page, name="dashboard2"),
    ]
