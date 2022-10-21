import csv
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from tools.filters import JobFilter, OperationFilter
from tools.forms import OperationUpdateForm, JobAddForm
from tools.models import JobUpdate, OperationModel, JobModel, JobStationModel


def index(request):
    return render(
        request,
        template_name="tools/index.html"
    )


# class JobUpdateCreateView(LoginRequiredMixin, CreateView):
#     model = JobUpdate
#     template_name = "form.html"
#     fields = "__all__"
#     success_url = reverse_lazy("tools_app:search-form")


class JobFormView(LoginRequiredMixin, FormView):
    template_name = 'form.html'
    form_class = JobAddForm
    success_url = reverse_lazy("tools_app:search-form")

    def form_valid(self, form):
        date = form.cleaned_data["date"]
        job = form.cleaned_data["job"]
        meters = form.cleaned_data["meters"]
        JobUpdate.objects.create(date=date, job=job, meters=meters)

        operations = OperationModel.objects.exclude(start_date__gt=date).exclude(finish_date__lt=date).values("id",
                                                                                                              "meters",
                                                                                                              "station",
                                                                                                              "machine")

        for operation in operations:
            station = operation["station"]
            machine = operation["machine"]
            new_id = operation["id"]
            jobs = JobStationModel.objects.filter(machine=machine).filter(station=station).values("id", "job")
            for j_dict in jobs:
                job_num = j_dict["job"]
                job_name = JobModel.objects.get(id=job_num)
                if job == job_name:
                    updated_object = OperationModel.objects.get(id=new_id)
                    updated_object.meters += meters
                    updated_object.save()
        return super().form_valid(form)


def search(request):
    items_list = JobUpdate.objects.all().order_by("-date")
    items_filter = JobFilter(request.GET, queryset=items_list)
    return render(request, "tools/filter_list.html", {"filter": items_filter})


# class OperationUpdateCreateView(LoginRequiredMixin, CreateView):
#     model = OperationModel
#     template_name = "form.html"
#     fields = (
#         "machine",
#         "station",
#         "tool",
#         "start_date",
#     )
#     success_url = reverse_lazy("tools_app:returning")


class OperationFormView(FormView):
    template_name = 'form.html'
    form_class = OperationUpdateForm
    success_url = reverse_lazy("tools_app:returning")

    def form_valid(self, form):
        tool = form.cleaned_data["tool"]
        machine = form.cleaned_data["machine"]
        station = form.cleaned_data["station"]
        start_date = form.cleaned_data["start_date"]
        OperationModel.objects.create(tool=tool, machine=machine, station=station, start_date=start_date)

        tools = OperationModel.objects.filter(
            machine=machine).filter(station=station).filter(status=False).values("id", "tool", "status", "finish_date")

        max_id = 0
        if len(tools) > 1:
            for tool_dict in tools:
                tool_id = tool_dict["id"]
                if tool_id > max_id:
                    max_id = tool_id

            for tool_dict in tools:
                tool_id = tool_dict["id"]
                if tool_id != max_id:
                    tool = OperationModel.objects.get(id=tool_id)
                    tool.status = True
                    tool.finish_date = datetime.now()
                    tool.save()

        return super().form_valid(form)


# def search2(request):
#     operations_list = OperationModel.objects.all().order_by("-start_date")
#     operations_filter = OperationFilter(request.GET, queryset=operations_list)
#     return render(request, "tools/filter_list2.html", {"filter": operations_filter})


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


def export_csv(request):
    operations = OperationModel.objects.all()
    search_result = OperationFilter(request.GET, queryset=operations).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file.csv"'
    writer = csv.writer(response)
    writer.writerow(['Machine', 'Station', 'Tool', 'Start Date', 'Finish Date', 'Status', 'Meters'])
    for e in search_result.values_list('machine_id__name',
                                       'station_id__name',
                                       'tool_id__name',
                                       'start_date',
                                       'finish_date',
                                       'status',
                                       'meters'):
        writer.writerow(e)
    return response
