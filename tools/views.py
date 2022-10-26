import csv
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from tools.filters import JobFilter, OperationFilter
from tools.forms import JobAddForm, OperationBarcodeForm, OperationUpdateForm, JobAddBarcodeForm
from tools.models import JobUpdate, OperationModel, JobModel, JobStationModel


def index(request):
    return render(
        request,
        template_name="tools/index.html"
    )


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


class JobFormBarcodeView(LoginRequiredMixin, FormView):
    template_name = 'form.html'
    form_class = JobAddBarcodeForm
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


class OperationFormView(FormView):
    template_name = 'form.html'
    form_class = OperationUpdateForm
    success_url = reverse_lazy("tools_app:returning")

    def form_valid(self, form):
        tool = form.cleaned_data["tool"]
        tool_type = form.cleaned_data["tool_type"]
        machine = form.cleaned_data["machine"]
        station = form.cleaned_data["station"]
        start_date = form.cleaned_data["start_date"]
        OperationModel.objects.create(tool=tool, tool_type=tool_type, machine=machine, station=station,
                                      start_date=start_date)

        tools = OperationModel.objects.filter(
            machine=machine).filter(station=station).filter(status=False).values("id", "tool", "tool_type",
                                                                                 "status", "finish_date")

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
                    if tool.tool_type == tool_type:
                        tool.status = True
                        tool.finish_date = datetime.now()
                        tool.save()

        return super().form_valid(form)


class OperationBarcodeFormView(FormView):
    template_name = 'form.html'
    form_class = OperationBarcodeForm
    success_url = reverse_lazy("tools_app:returning")

    def form_valid(self, form):
        tool = form.cleaned_data["tool"]
        tool_type = form.cleaned_data["tool_type"]
        machine = form.cleaned_data["machine"]
        station = form.cleaned_data["station"]
        start_date = form.cleaned_data["start_date"]
        OperationModel.objects.create(tool=tool, tool_type=tool_type, machine=machine, station=station,
                                      start_date=start_date)

        tools = OperationModel.objects.filter(
            machine=machine).filter(station=station).filter(status=False).values("id", "tool", "tool_type",
                                                                                 "status", "finish_date")

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
                    if tool.tool_type == tool_type:
                        tool.status = True
                        tool.finish_date = datetime.now()
                        tool.save()

        return super().form_valid(form)


def returning(request):
    operations = OperationModel.objects.all().order_by("-start_date")
    operations_filter = OperationFilter(request.GET, queryset=operations)
    return render(request, "tools/return.html", {"filter": operations_filter})


def export_csv(request):
    operations = OperationModel.objects.all()
    search_result = OperationFilter(request.GET, queryset=operations).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Operations.csv"'
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


def export_csv2(request):
    jobs = JobUpdate.objects.all()
    search_result = JobFilter(request.GET, queryset=jobs).qs
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Completed_jobs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Job', 'Meters'])
    for e in search_result.values_list('date',
                                       'job_id__name',
                                       'meters'):
        writer.writerow(e)
    return response


def tool_in_use(request):
    tools_in_use = OperationModel.objects.filter(status=False).order_by("machine").order_by("station__num")
    return render(request, template_name="tools/in_use.html", context={"tools_in_use": tools_in_use})
