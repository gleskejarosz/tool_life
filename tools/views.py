import csv
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, ListView, DeleteView

from gemba.models import JobModel2
from tools.filters import JobFilter, OperationFilter
from tools.forms import JobAddForm, OperationUpdateForm, JobUpdateForm
from tools.models import JobUpdate, OperationModel, JobStationModel, ToolModel, ToolJobModel


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
        parts = form.cleaned_data["parts"]

        new_job = JobUpdate.objects.create(date=date, job=job, parts=parts)
        new_job_id = new_job.id

        new_job_obj = JobUpdate.objects.get(id=new_job_id)
        new_minutes = new_job_obj.minutes

        operations_qs = OperationModel.objects.exclude(start_date__gt=date).exclude(finish_date__lt=date)
        # operations2_qs = OperationModel.objects.filter(start_date=date).filter(status=False)
        # operations_qs = operations1_qs.difference(operations2_qs)

        for operation in operations_qs:
            station = operation.station
            machine = operation.machine
            # new_id = operation.id
            used_minutes = operation.minutes

            jobs_qs = JobStationModel.objects.filter(machine=machine).filter(station=station)
            print(jobs_qs)
            for job_elem in jobs_qs:
                job_id = job_elem.job_id
                job_name = JobModel2.objects.get(id=job_id)
                if job == job_name:
                    # updated_object = OperationModel.objects.get(id=new_id)
                    print(f"Tool minutes: {used_minutes} + new minutes {new_minutes}")
                    operation.minutes += new_minutes
                    operation.save()

        return super().form_valid(form)


def search(request):
    items_list = JobUpdate.objects.all().order_by("-date")
    items_filter = JobFilter(request.GET, queryset=items_list)
    return render(request, "tools/filter_list.html", {"filter": items_filter})


class OperationFormView(LoginRequiredMixin, FormView):
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

        tool_availability = ToolModel.objects.get(name=tool)
        tool_availability.tool_status = "In use"
        tool_availability.save()

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
                        tool.finish_date = start_date
                        tool.save()
                        print(tool)
                        tool_availability = ToolModel.objects.get(name=tool)
                        tool_availability.tool_status = "Spare"
                        tool_availability.save()

        return super().form_valid(form)


def returning(request):
    operations = OperationModel.objects.all().order_by("-start_date")
    operations_filter = OperationFilter(request.GET, queryset=operations)
    return render(request, "tools/return.html", {"filter": operations_filter})


def export_csv(request):
    operations = OperationModel.objects.all()
    search_result = OperationFilter(request.GET, queryset=operations).qs
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Operations.csv"'
    writer = csv.writer(response)
    writer.writerow(["Machine", "Station", "Tool", "Minutes", "Start Date", "Finish Date", "Status"])
    for e in search_result.values_list("machine_id__name",
                                       "station_id__name",
                                       "tool_id__name",
                                       "minutes",
                                       "start_date",
                                       "finish_date",
                                       "status"):
        writer.writerow(e)
    return response


def export_csv2(request):
    jobs = JobUpdate.objects.all()
    search_result = JobFilter(request.GET, queryset=jobs).qs
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Completed_jobs.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date", "Job", "Parts", "Minutes"])
    for e in search_result.values_list("date",
                                       "job_id__name",
                                       "parts",
                                       "minutes"):
        writer.writerow(e)
    return response


def tool_in_use(request):
    tools_in_use = OperationModel.objects.filter(status=False).order_by("station__num")
    return render(request, template_name="tools/in_use.html", context={"tools_list": tools_in_use})


class JobDetailView(DetailView):
    model = JobUpdate
    template_name = "tools/completed_job_details.html"


class JobListView(ListView):
    template_name = "tools/job_list.html"
    model = JobUpdate

    def get_ordering(self):
        ordering = self.request.GET.get('-date')
        return ordering


def jobs(request):
    items_list = JobUpdate.objects.all().order_by("-date")
    return render(
        request,
        template_name='tools/job_list.html',
        context={'object_list': items_list},
    )


def update_parts(pk, old_minutes):
    changed_job = JobUpdate.objects.get(pk=pk)
    date = changed_job.date
    job = changed_job.job
    new_minutes = changed_job.minutes

    operations1_qs = OperationModel.objects.exclude(start_date__gt=date).exclude(finish_date__lt=date)
    print(operations1_qs)
    operations2_qs = OperationModel.objects.filter(start_date=date).filter(status=False)
    print(operations2_qs)
    operations_qs = operations1_qs.difference(operations2_qs)
    print(operations_qs)

    for operation in operations_qs:
        station = operation.station
        machine = operation.machine
        new_id = operation.id
        used_minutes = operation.minutes
        jobs_qs = JobStationModel.objects.filter(machine=machine).filter(station=station)
        for j_dict in jobs_qs:
            job_id = j_dict.job_id
            job_name = JobModel2.objects.get(id=job_id)
            if job == job_name:
                updated_object = OperationModel.objects.get(id=new_id)
                print(new_id)
                new_used_minutes = new_minutes - old_minutes
                print(f"Tool minutes: {used_minutes} + (Difference: {new_minutes} - {old_minutes})")
                updated_object.minutes += new_used_minutes
                updated_object.save()

    return redirect("tools_app:search-form")


@login_required
def job_update(request, pk):
    job_to_update = get_object_or_404(JobUpdate, pk=pk)
    old_minutes = job_to_update.minutes

    form = JobUpdateForm(instance=job_to_update)
    if request.method == "POST":
        form = JobUpdateForm(request.POST, instance=job_to_update)

    if form.is_valid():
        form.save()

        update_parts(pk=pk, old_minutes=old_minutes)
        return redirect("tools_app:search-form")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = JobUpdate
    template_name = "tools/delete_scrap.html"
    success_url = reverse_lazy("tools_app:search-form")
