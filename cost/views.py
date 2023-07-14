from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView

from cost.filters import DailyResultFilter
from cost.forms import TableUpdateForm, TableCreateForm
from cost.models import Table


@staff_member_required
def cost_table_view(request):
    table_qs = Table.objects.all().order_by("-id")
    items_filter = DailyResultFilter(request.GET, queryset=table_qs)

    sum_cost = 0
    for elem in items_filter.qs:
        elem_amount = elem.amount
        sum_cost += elem_amount

    return render(request,
                  template_name='cost/cost_table.html',
                  context={
                      "filter": items_filter,
                      "cost_table": table_qs,
                      "sum_cost": sum_cost,
                  },
                  )


@staff_member_required
def cost_table_detail_view(request, pk):
    table = Table.objects.get(pk=pk)

    return render(request,
                  template_name='cost/cost_table_detail.html',
                  context={
                      "object": table,
                  },
                  )


class TableUpdateView(UpdateView):
    model = Table
    template_name = "form.html"
    form_class = TableUpdateForm
    success_url = reverse_lazy("costs_app:index")


class CreateCost(CreateView):
    model = Table
    template_name = "form.html"
    form_class = TableCreateForm
    success_url = reverse_lazy("costs_app:index")


class CostDelete(DeleteView):
    model = Table
    success_url = reverse_lazy("costs_app:index")
