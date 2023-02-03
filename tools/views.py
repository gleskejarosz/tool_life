import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from gemba.models import JobModel2, Line, PRODUCTIVE, JobLine
from tools.filters import OperationFilter, ToolFilter
from tools.forms import ToolChangeForm, AddTool
from tools.models import OperationModel, ToolStationModel, ToolJobModel, SPARE, USE


@staff_member_required
def index(request):
    return render(
        request,
        template_name="tools/index.html"
    )


@staff_member_required
def change_tool(request, tool_id):
    tool_obj = ToolStationModel.objects.get(id=tool_id)
    tool_type = tool_obj.tool_type
    station = tool_obj.station.name
    machine = tool_obj.machine.name

    form = ToolChangeForm(request.POST or None)

    if form.is_valid():
        start_date = form.cleaned_data["start_date"]

        OperationModel.objects.create(machine=machine, station=station, tool=tool_obj, tool_type=tool_type,
                                      start_date=start_date)

        operation_qs = OperationModel.objects.filter(machine=machine, station=station,
                                                     tool_type=tool_type).order_by("-start_date")
        len_operation_qs = len(operation_qs)
        if len_operation_qs > 1:
            operation_obj = operation_qs[1]
            operation_obj.status = True
            operation_obj.finish_date = start_date
            operation_obj.tool.tool_status = SPARE
            operation_obj.save()
            operation_obj.tool.save()

        tool_obj.tool_status = USE
        tool_obj.save()

        return redirect("tools_app:tool-actions")

    return render(
        request,
        template_name="tools/tool_form.html",
        context={
            "form": form,
            "tool": tool_obj,
        }
    )


@staff_member_required
def select_tool(request):
    tools_qs = ToolStationModel.objects.filter(machine__line_status=PRODUCTIVE).order_by("machine__name", "station__name")
    tools_filter = ToolFilter(request.GET, queryset=tools_qs)

    return render(request,
                  template_name="tools/tool.html",
                  context={
                      "filter": tools_filter,
                  })


@staff_member_required
def tool_actions_view(request):
    operations = OperationModel.objects.all().order_by("-start_date")
    operations_filter = OperationFilter(request.GET, queryset=operations)
    return render(request, "tools/tool_actions.html", {"filter": operations_filter})


@staff_member_required
def export_csv(request):
    operations = OperationModel.objects.all()
    search_result = OperationFilter(request.GET, queryset=operations).qs
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Operations.csv"'
    writer = csv.writer(response)
    writer.writerow(["Machine", "Station", "Tool", "Minutes", "Start Date", "Finish Date", "Status"])
    for e in search_result.values_list("machine",
                                       "station",
                                       "tool__tool",
                                       "minutes",
                                       "start_date",
                                       "finish_date",
                                       "status"):
        writer.writerow(e)
    return response


@staff_member_required
def tool_in_use(request):
    tools_in_use = OperationModel.objects.filter(status=False).order_by("machine", "station")
    return render(request, template_name="tools/in_use.html", context={"tools_list": tools_in_use})


def tools_update(job, output, target, modified):
    minutes = int(round((output / target) * 60))

    tools = set()
    tools_qs = ToolJobModel.objects.filter(job=job, status=True)
    for tool_obj in tools_qs:
        tool_name = tool_obj.tool.tool
        tools.add(tool_name)

    actions_qs = OperationModel.objects.exclude(start_date__gt=modified).exclude(finish_date__lt=modified)

    for action in actions_qs:
        tool = action.tool.tool

        if tool in tools:
            action.minutes += minutes
            if action.minutes < 0:
                action.minutes = 0
            action.save()


@staff_member_required
def machines_view(request):
    machine_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    return render(request, "tools/machines.html", {"machine_qs": machine_qs})


@staff_member_required
def machines_view_3(request):
    machine_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    return render(request, "tools/machines_3.html", {"machine_qs": machine_qs})


@staff_member_required
def tools_vs_jobs(request, machine_id):
    # machine = Line.objects.get(pk=machine_id)
    tools_qs = ToolJobModel.objects.all().order_by("job__name")

    jobs_list = []
    jobs_qs = JobLine.objects.filter(line=machine_id).order_by("job")
    for job_elem in jobs_qs:
        job_id = job_elem.job_id
        job = JobModel2.objects.get(id=job_id)
        job_name = job.name
        if job not in jobs_list:
            jobs_list.append(job_name)

    new_tools_qs = []
    for tool_obj in tools_qs:
        job = tool_obj.job.name
        if job in jobs_list:
            new_tools_qs.append(tool_obj)

    return render(
        request,
        template_name="tools/tools_vs_jobs.html",
        context={"new_tools_qs": new_tools_qs},
    )


@staff_member_required
def tools_vs_jobs_table(request, machine_id):
    machine = Line.objects.get(pk=machine_id)

    tools_qs = ToolStationModel.objects.filter(machine=machine).order_by("station")

    jobs_list = []
    for tool_obj in tools_qs:
        tool_id = tool_obj.id
        jobs_qs = ToolJobModel.objects.filter(tool=tool_id)
        for job_elem in jobs_qs:
            job_id = job_elem.job_id
            job = JobModel2.objects.get(id=job_id)
            job_name = job.name
            if job not in jobs_list:
                jobs_list.append(job_name)

    jobs_set = set(jobs_list)
    jobs_list = sorted(list(jobs_set))

    table_qs = []

    for idx, tool_elem in enumerate(tools_qs):
        station = tool_elem.station.name
        tool = tool_elem.tool
        tool_id = tool_elem.id
        table_qs.append({
            "Station": station,
            "Tool": tool,
        })
        for job in jobs_list:
            table_elem = table_qs[idx]
            table_elem[job] = 0

        tool_jobs_qs = ToolJobModel.objects.filter(tool=tool_id).order_by("job")
        for job_elem in tool_jobs_qs:
            if job_elem.status is True:
                job_id = job_elem.job_id
                job_item = JobModel2.objects.get(id=job_id)
                job_elem_name = job_item.name
                table_elem = table_qs[idx]
                table_elem[job_elem_name] = 1

    return render(
        request,
        template_name="tools/tools_vs_jobs_table.html",
        context={"table_qs": table_qs},
    )


@staff_member_required
def update_tool_vs_job(request, pk):
    tool_job_obj = ToolJobModel.objects.get(pk=pk)
    tool_id = tool_job_obj.tool_id
    tool = ToolStationModel.objects.get(id=tool_id)
    machine_id = tool.machine_id

    if tool_job_obj.status is True:
        tool_job_obj.status = False
    else:
        tool_job_obj.status = True
    tool_job_obj.save()
    return HttpResponseRedirect(reverse('tools_app:tools-vs-jobs', kwargs={'machine_id': machine_id}))


@staff_member_required
def machines_view2(request):
    machine_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    return render(request, "tools/tools_machines.html", {"machine_qs": machine_qs})


@staff_member_required
def tools_on_the_machine(request, machine_id):
    machine = get_object_or_404(Line, pk=machine_id)
    machine_name = machine.name

    qs = ToolStationModel.objects.filter(machine=machine_id).order_by("station")

    return render(
        request,
        template_name="tools/tools.html",
        context={
            "qs": qs,
            "machine_id": machine_id,
            "machine_name": machine_name,
        },
    )


@staff_member_required
def add_tool(request, machine_id):
    machine = get_object_or_404(Line, pk=machine_id)

    form = AddTool(request.POST or None)

    if form.is_valid():
        station = form.cleaned_data["station"]
        tool = form.cleaned_data["tool"]

        tool_obj = ToolStationModel.objects.create(machine=machine, station=station, tool=tool)

        jobs_qs = JobLine.objects.filter(line=machine)

        for job_obj in jobs_qs:
            job_id = job_obj.job_id
            job = JobModel2.objects.get(id=job_id)
            ToolJobModel.objects.create(job=job, tool=tool_obj)

        return HttpResponseRedirect(reverse('tools_app:tools', kwargs={'machine_id': machine_id}))

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )






