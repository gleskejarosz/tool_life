from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from tools.filters import JobFilter, OperationFilter
from tools.models import JobUpdate, OperationModel, ToolModel, RelationModel, JobModel


def index(request):
    return render(
        request,
        template_name="tools/index.html"
    )


class JobUpdateCreateView(LoginRequiredMixin, CreateView):
    model = JobUpdate
    template_name = "form.html"
    fields = "__all__"
    success_url = reverse_lazy("tools_app:search-form")


def completed_job(request):
    if request.method == "POST":
        job = JobModel.objects.get(id=int(request.POST['job']))
        meters = request.POST['meters']

        finished_job = JobUpdate(job=job, meters=meters)
        finished_job.save()

    finished_job = JobUpdate.objects.all()
    return render(request, "form.html", {"finished_job": finished_job})


def update_meters(request):
    done = 1000
    start = '2022-10-13'
    tools = OperationModel.objects.exclude(start_date__lt=start)

    for tool in tools:
        tool.meters += done

    return render(request, "tools/update.html", {"tools": tools})


def search(request):
    items_list = JobUpdate.objects.all().order_by("-date")
    items_filter = JobFilter(request.GET, queryset=items_list)
    return render(request, "tools/filter_list.html", {"filter": items_filter})


class OperationUpdateCreateView(LoginRequiredMixin, CreateView):
    model = OperationModel
    template_name = "form.html"
    fields = (
        "machine",
        "station",
        "tool",
        "start_date",
    )
    success_url = reverse_lazy("tools_app:returning")


def search2(request):
    operations_list = OperationModel.objects.all().order_by("-start_date")
    operations_filter = OperationFilter(request.GET, queryset=operations_list)
    return render(request, "tools/filter_list2.html", {"filter": operations_filter})


def returning(request):
    if request.method == "POST":
        b_id = int(request.POST["tool_id"])
        borrow = OperationModel.objects.get(id=b_id)
        borrow.finish_date = datetime.now()
        borrow.status = True
        borrow.save()
        return redirect('/tools/returning/')
    borrows = OperationModel.objects.all().order_by("-start_date")
    operations_filter = OperationFilter(request.GET, queryset=borrows)
    return render(request, "tools/return.html", {"filter": operations_filter})
