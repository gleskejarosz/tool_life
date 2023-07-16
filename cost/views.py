from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView, TemplateView

from cost.filters import DailyResultFilter
from cost.forms import TableUpdateForm, TableCreateForm, ContentsUpdateForm, ContentsCreateForm
from cost.models import Table, Contents


class CostIndex(TemplateView):
    template_name = 'cost/index.html'


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
    success_url = reverse_lazy("costs_app:our-costs")


class CreateCost(CreateView):
    model = Table
    template_name = "form.html"
    form_class = TableCreateForm
    success_url = reverse_lazy("costs_app:our-costs")


class CostDelete(DeleteView):
    model = Table
    success_url = reverse_lazy("costs_app:our-costs")


@staff_member_required
def contents_table_view(request):
    table_qs = Contents.objects.all().order_by("-id")

    sum_weight = 0
    for elem in table_qs:
        elem_weight = elem.weight
        sum_weight += elem_weight

    return render(request,
                  template_name='cost/contents.html',
                  context={
                      "contents_table": table_qs,
                      "sum_weight": sum_weight,
                  },
                  )


@staff_member_required
def contents_detail_view(request, pk):
    contents = Contents.objects.get(pk=pk)

    return render(request,
                  template_name='cost/contents_detail.html',
                  context={
                      "object": contents,
                  },
                  )


class ContentsUpdateView(UpdateView):
    model = Contents
    template_name = "form.html"
    form_class = ContentsUpdateForm
    success_url = reverse_lazy("costs_app:contents")


class ContentsCreate(CreateView):
    model = Contents
    template_name = "form.html"
    form_class = ContentsCreateForm
    success_url = reverse_lazy("costs_app:contents")


class ContentsDelete(DeleteView):
    model = Contents
    success_url = reverse_lazy("costs_app:contents")
