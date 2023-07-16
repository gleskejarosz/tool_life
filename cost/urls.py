from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from cost import views

app_name = "costs_app"


urlpatterns = [
    path('costs/index/', staff_member_required(views.CostIndex.as_view()), name="index"),
    path('costs/our_costs/', views.cost_table_view, name="our-costs"),
    path('costs/cost_detail_view/<pk>/', views.cost_table_detail_view, name="cost-detail-view"),
    path("costs/cost_update_detail/<pk>/", staff_member_required(views.TableUpdateView.as_view()),
         name="cost-update-detail"),
    path("costs/create_cost_detail/", staff_member_required(views.CreateCost.as_view()),
         name="create-cost-detail"),
    path("costs/delete_cost_detail/<pk>/", staff_member_required(views.CostDelete.as_view()),
         name="delete-cost-detail"),
    path('costs/contents/', views.contents_table_view, name="contents"),
    path('costs/contents_detail_view/<pk>/', views.contents_detail_view, name="contents-detail-view"),
    path("costs/contents_update_detail/<pk>/", staff_member_required(views.ContentsUpdateView.as_view()),
         name="contents-update-detail"),
    path("costs/create_content_detail/", staff_member_required(views.ContentsCreate.as_view()),
         name="create-content-detail"),
    path("costs/delete_content_detail/<pk>/", staff_member_required(views.ContentsDelete.as_view()),
         name="delete-content-detail"),
]
