from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from cost import views

app_name = "costs_app"


urlpatterns = [
    path('costs/index/', views.cost_table_view, name="index"),
    path('costs/cost_detail_view/<pk>/', views.cost_table_detail_view, name="cost-detail-view"),
    path("costs/cost_update_detail/<pk>/", staff_member_required(views.TableUpdateView.as_view()),
         name="cost-update-detail"),
    path("costs/create_cost_detail/", staff_member_required(views.CreateCost.as_view()),
         name="create-cost-detail"),
    path("costs/delete_cost_detail/<pk>/", staff_member_required(views.CostDelete.as_view()),
         name="delete-cost-detail"),
]
