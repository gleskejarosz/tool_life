import csv
import xlwt
from xlwt import XFStyle, Font
from datetime import datetime, timezone, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView, ListView
from django.db.models import Q

from gemba.filters import ParetoDetailFilter
from gemba.forms import ParetoDetailForm, DowntimeMinutes, ScrapQuantity, DowntimeAdd, NewPareto, ParetoUpdateForm, \
    NotScheduledToRunUpdateForm, ParetoTotalQtyDetailForm
from gemba.models import Pareto, ParetoDetail, DowntimeModel, DowntimeDetail, ScrapModel, ScrapDetail, DowntimeUser, \
    DowntimeGroup, ScrapUser, LineHourModel, JobModel2, Timer



class GembaIndex(TemplateView):
    template_name = 'gemba/index.html'


def downtimes_view(request):
    downtimes = DowntimeDetail.objects.all().order_by("-pareto_date")
    today_downtimes = DowntimeDetail.objects.filter(pareto_date__gte=datetime.now() - timedelta(days=7)).order_by(
        "-pareto_date")
    return render(request,
                  template_name="gemba/downtimes_view.html",
                  context={
                      "filter": downtimes,
                      "today_downtimes": today_downtimes,
                  })


def scraps_view(request):
    scraps = ScrapDetail.objects.all().order_by("-pareto_date")
    today_downtimes = ScrapDetail.objects.filter(pareto_date__gte=datetime.now() - timedelta(days=7)).order_by(
        "-pareto_date")
    return render(request,
                  template_name="gemba/scraps_view.html",
                  context={
                      "filter": scraps,
                      "today_downtimes": today_downtimes,
                  })


@login_required
def downtime_detail_create(request, pk):
    downtime = get_object_or_404(DowntimeModel, pk=pk)
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    pareto = pareto_qs[0]
    pareto_id = pareto.id
    pareto_date = pareto.pareto_date
    job = pareto.job_otg
    downtime_qs = DowntimeDetail.objects.filter(user=request.user, completed=False, downtime_id=pk, job=job)

    if downtime_qs.exists():
        downtime_id = downtime_qs[0].id
        downtime = get_object_or_404(DowntimeDetail, id=downtime_id)
        old_time = downtime.minutes
        form = DowntimeMinutes(request.POST or None)
        if form.is_valid():
            minutes = form.cleaned_data["minutes"]
            new_time = minutes + old_time
            downtime.minutes = new_time
            downtime.frequency += 1
            downtime.save()
            return redirect("gemba_app:pareto-summary")
    else:
        form = DowntimeMinutes(request.POST or None)
        if form.is_valid():
            minutes = form.cleaned_data["minutes"]
            user = request.user
            downtime_elem = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user, job=job,
                                                          pareto_id=pareto_id, pareto_date=pareto_date)
            pareto.downtimes.add(downtime_elem)
            return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@login_required
def scrap_detail_create(request, pk):
    scrap = get_object_or_404(ScrapModel, pk=pk)
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    pareto = pareto_qs[0]
    pareto_id = pareto.id
    pareto_date = pareto.pareto_date
    job = pareto.job_otg

    form = ScrapQuantity(request.POST or None)
    if form.is_valid():
        qty = form.cleaned_data["qty"]
        user = request.user
        scrap_qs = ScrapDetail.objects.filter(user=request.user, completed=False, scrap=scrap, job=job)

        if scrap_qs.exists():
            scrap_elem = ScrapDetail.objects.get(scrap=scrap, user=user, job=job)
            scrap_elem.qty += qty
            scrap_elem.save()
            return redirect("gemba_app:pareto-summary")
        else:
            scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job,
                                                            pareto_id=pareto_id, pareto_date=pareto_date)
            pareto.scrap.add(scrap_elem)
            return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@login_required
def pareto_detail_form(request):
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    pareto = pareto_qs[0]
    job = pareto.job_otg
    # setup on id=0 Not selected
    job_message = JobModel2.objects.get(id=1)

    if job is None:
        pareto.job_otg = job_message
        pareto.save()
        return redirect("gemba_app:pareto-summary")

    if job == job_message:
        return redirect("gemba_app:pareto-summary")

    pareto_details_qs = ParetoDetail.objects.filter(user=request.user, completed=False)
    total_output = 0
    total_good = 0
    if pareto_details_qs.exists():
        for elem in pareto_details_qs:
            if elem.job == job:
                total_output += elem.qty
                total_good += elem.good
            else:
                total_output = 0
                total_good = 0

    pareto_id = pareto.id
    pareto_date = pareto.pareto_date
    down_group = DowntimeGroup.objects.get(user=request.user)
    calc_form = down_group.calculation_id
    user = request.user

    if calc_form == 1:
        form = ParetoTotalQtyDetailForm(request.POST or None)
        if form.is_valid():
            qty = form.cleaned_data["qty"] - total_output
            good = form.cleaned_data["good"] - total_good
            pareto_item = ParetoDetail.objects.create(job=job, qty=qty, user=user, good=good, pareto_id=pareto_id,
                                                      pareto_date=pareto_date)
            pareto.jobs.add(pareto_item)
            return redirect("gemba_app:pareto-summary")
    else:
        form = ParetoDetailForm(request.POST or None)
        if form.is_valid():
            qty = form.cleaned_data["qty"]
            good = form.cleaned_data["good"]
            pareto_item = ParetoDetail.objects.create(job=job, qty=qty, user=user, good=good, pareto_id=pareto_id,
                                                      pareto_date=pareto_date)
            pareto.jobs.add(pareto_item)
            return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


class ParetoSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            user = self.request.user
            pareto = Pareto.objects.get(user=user, completed=False)
            pareto_status = ""
            status = pareto.completed
            hours = pareto.hours
            time_stamp = pareto.time_stamp
            not_scheduled_to_run = pareto.not_scheduled_to_run

            message_status = ""
            job_otg = pareto.job_otg
            #setup on id=0 Not selected
            job_message = JobModel2.objects.get(id=29)
            if job_otg == job_message:
                message_status = "Display"

            available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp,
                                                not_scheduled_to_run=not_scheduled_to_run)

            scrap_details = ParetoDetail.objects.filter(user=user, completed=False).values("id", "qty", "good", "job")
            total_good = 0
            total_output = 0
            if scrap_details.exists():
                for scrap_cal in scrap_details:
                    output = scrap_cal["qty"]
                    total_output += output
                    good = scrap_cal["good"]
                    total_good += good
            total_scrap_cal = total_output - total_good

            quality = quality_cal(good=total_good, output=total_output)

            down_qs = DowntimeDetail.objects.filter(user=user, completed=False).values("id", "minutes")
            total_down = 0
            if down_qs.exists():
                for down in down_qs:
                    quantity = down["minutes"]
                    total_down += quantity

            availability = availability_cal(available_time=available_time, downtime=total_down)

            scrap_qs = ScrapDetail.objects.filter(user=user, completed=False).values("id", "qty")
            total_scrap = 0
            if scrap_qs.exists():
                for scrap in scrap_qs:
                    qty = scrap["qty"]
                    total_scrap += qty

            performance_numerator = 0

            if scrap_details.exists():
                for pareto_detail in scrap_details:
                    job_elem = pareto_detail["job"]
                    job_model = JobModel2.objects.get(id=job_elem)
                    takt_time = round(60 / job_model.target, 5)
                    qty_elem = pareto_detail["qty"]
                    performance_numerator += (qty_elem * takt_time)

            performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                          downtime=total_down)

            oee = oee_cal(availability=availability, performance=performance, quality=quality)

            return render(self.request,
                          template_name='gemba/pareto.html',
                          context={
                              "pareto_list": pareto,
                              "user": user,
                              "pareto_status": pareto_status,
                              "message_status": message_status,
                              "available_time": available_time,
                              "availability": availability,
                              "quality": quality,
                              "performance": performance,
                              "oee": oee,
                              "total_scrap": total_scrap,
                              "total_down": total_down,
                              "total_output": total_output,
                              "total_good": total_good,
                              "total_scrap_cal": total_scrap_cal,
                          },
                          )
        except ObjectDoesNotExist:
            pareto_status = "Not exist"
            message_status = ""
            user = self.request.user
            available_time = 0
            availability = 0
            quality = 0
            performance = 0
            oee = 0
            total_scrap = 0
            total_down = 0
            total_output = 0
            total_good = 0
            total_scrap_cal = 0

            return render(self.request,
                          template_name='gemba/pareto.html',
                          context={
                              "available_time": available_time,
                              "user": user,
                              "availability": availability,
                              "quality": quality,
                              "performance": performance,
                              "oee": oee,
                              "pareto_status": pareto_status,
                              "total_scrap": total_scrap,
                              "total_down": total_down,
                              "total_output": total_output,
                              "total_good": total_good,
                              "total_scrap_cal": total_scrap_cal,
                              "message_status": message_status,
                          }
                          )


def available_time_cal(status, hours, time_stamp, not_scheduled_to_run):
    if status is True:
        available_time = int(hours) * 60 - not_scheduled_to_run
    else:
        now = datetime.now()
        sec_now = int(now.strftime('%S'))
        sec_now += int(now.strftime('%M')) * 60
        sec_now += int(now.strftime('%H')) * 60 * 60

        sec_start = int(time_stamp.strftime('%S'))
        sec_start += int(time_stamp.strftime('%M')) * 60
        sec_start += int(time_stamp.strftime('%H')) * 60 * 60

        available_time = round((sec_now - sec_start) / 60.0)
    return available_time


def performance_cal(performance_numerator, available_time, downtime):
    if available_time - downtime != 0:
        performance = round((performance_numerator / (available_time - downtime)) * 100)
    else:
        performance = 0
    return performance


def quality_cal(good, output):
    if output != 0:
        quality = round((good / output) * 100)
    else:
        quality = 0
    return quality


def availability_cal(available_time, downtime):
    if available_time == 0:
        availability = 0
    else:
        availability = round(((available_time - downtime) / available_time * 100))
    return availability


def oee_cal(availability, performance, quality):
    oee = round(availability * performance * quality / 10000)
    return oee


def pareto_detail_view(request, pk):
    pareto = get_object_or_404(Pareto, pk=pk)

    status = pareto.completed
    hours = pareto.hours
    time_stamp = pareto.time_stamp
    not_scheduled_to_run = pareto.not_scheduled_to_run
    available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp,
                                        not_scheduled_to_run=not_scheduled_to_run)

    output = 0
    good = 0
    performance_numerator = 0

    for detail in pareto.jobs.all():
        output += detail.qty
        good += detail.good
        performance_numerator += (detail.qty * (60 / detail.job.target))

    quality = quality_cal(good=good, output=output)

    downtime = 0
    for down_elem in pareto.downtimes.all():
        downtime += down_elem.minutes

    performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                  downtime=downtime)

    availability = availability_cal(available_time=available_time, downtime=downtime)

    oee = oee_cal(availability=availability, performance=performance, quality=quality)

    scrap = 0
    for scrap_elem in pareto.scrap.all():
        scrap += scrap_elem.qty

    return render(request,
                  template_name='gemba/pareto_details.html',
                  context={
                      "pareto_list": pareto,
                      "available_time": available_time,
                      "output": output,
                      "good": good,
                      "downtime": downtime,
                      "availability": availability,
                      "quality": quality,
                      "performance": performance,
                      "oee": oee,
                      "scrap": scrap,
                  },
                  )


@login_required
def close_pareto(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)

    down_items = pareto.downtimes.all()
    down_items.update(completed=True)
    for item in down_items:
        item.save()

    scrap_items = pareto.scrap.all()
    scrap_items.update(completed=True)
    for item in scrap_items:
        item.save()

    details_item = pareto.jobs.all()
    details_item.update(completed=True)
    for item in details_item:
        item.save()

    pareto.completed = True
    pareto.save()

    return redirect("gemba_app:index")


@login_required
def tableau_export(request):
    pareto = Pareto.objects.get(id=24)
    pareto_id = pareto.id
    user = pareto.user
    shift = pareto.shift

    down_items = pareto.downtimes.all()
    scrap_items = pareto.scrap.all()
    details_item = pareto.jobs.all()

    pareto_details = []
    jobs = set()

    for idx, elem in enumerate(details_item):
        job = elem.job.name
        jobs.add(job)
        output = elem.qty
        good = elem.good
        if idx == 0:
            print(1)
            pareto_details.append([job, output, good])
        elif idx > 0:
            print(2)
            for pareto_detail in pareto_details:
                job_qs = pareto_detail[0]
                print(job)
                print(job_qs)
                if job == job_qs:
                    pareto_detail[1] += output
                    pareto_detail[2] += good
                    break
                else:
                    print(3)
                    pareto_details.append([job, output, good])
        print(pareto_details)

    return render(request,
                  template_name='gemba/tableau.html',
                  context={
                      "pareto_details": pareto_details,
                  },
                  )


def get_details_to_display(object_list):
    """
    Organizing data to be displayed in the form of a list of dictionaries, taking into account OEE calculations.
    Used in Daily OEE Report.
    """
    report_list = []
    for pareto in object_list:
        date = pareto.pareto_date
        id = pareto.id
        shift = pareto.shift
        user = pareto.user.username
        status = pareto.completed
        hours = pareto.hours
        time_stamp = pareto.time_stamp
        job_otg = pareto.job_otg
        not_scheduled_to_run = pareto.not_scheduled_to_run
        available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp,
                                            not_scheduled_to_run=not_scheduled_to_run)

        output = 0
        good = 0
        performance_numerator = 0

        for detail in pareto.jobs.all():
            output += detail.qty
            good += detail.good
            performance_numerator += (detail.qty * (60 / detail.job.target))

        quality = quality_cal(good=good, output=output)

        downtime = 0
        for down_elem in pareto.downtimes.all():
            downtime += down_elem.minutes

        performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                      downtime=downtime)

        availability = availability_cal(available_time=available_time, downtime=downtime)

        oee = oee_cal(availability=availability, performance=performance, quality=quality)

        scrap = 0
        for scrap_elem in pareto.scrap.all():
            scrap += scrap_elem.qty

        report_list.append({
            "id": id,
            "date": date,
            "shift": shift,
            "job_otg": job_otg,
            "user": user,
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee,
        })
    return report_list


class DailyParetoSearchResultsView(ListView):
    model = Pareto
    template_name = "gemba/daily_oee_report.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        report_list = Pareto.objects.filter(
            Q(pareto_date__exact=query)
        ).order_by("-user", "shift")
        object_list = get_details_to_display(object_list=report_list)
        return object_list


def export_daily_oee_report_csv(request):
    query = request.GET.get("q")
    report_list = Pareto.objects.filter(
        Q(pareto_date__exact=query)
    ).order_by("-user")
    object_list = get_details_to_display(object_list=report_list)

    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="Daily_OEE_Report.xls"'

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Report")

    fnt = Font()
    fnt.height = 300
    fnt.bold = True
    style = XFStyle()
    style.font = fnt

    ws.write(0, 0, f"Daily OEE Report - {object_list[0]['date']}", style)
    row_num = 2

    row_list = ["id", "user", "shift", "availability", "performance", "quality", "oee"]

    headers = ["Pareto Id", "Line/User", "Shift", "Availability", "Performance", "Quality", "OEE"]

    percentage = ["availability", "performance", "quality", "oee"]

    for col_num in range(len(row_list)):
        style1 = xlwt.easyxf("font: bold 1")
        ws.write(1, col_num, headers[col_num], style1)

    style2 = XFStyle()
    style2.num_format_str = "0%"

    style3 = XFStyle()
    style3.num_format_str = "D-MMM-YY"

    for row in object_list:
        for col_num in range(len(row_list)):
            dict_key = row_list[col_num]
            elem = row[dict_key]
            if dict_key == "date":
                ws.write(row_num, col_num, elem, style3)
            elif dict_key in percentage:
                perc_value = elem / 100
                ws.write(row_num, col_num, perc_value, style2)
            else:
                ws.write(row_num, col_num, elem)
        row_num += 1

    wb.save(response)
    return response


def pareto_view(request):
    today_pareto = Pareto.objects.filter(pareto_date=datetime.now()).order_by("-user", "shift")

    report_list = get_details_to_display(object_list=today_pareto)

    return render(request,
                  template_name="gemba/pareto_view.html",
                  context={
                      "report_list": report_list,
                  },
                  )


@login_required
def pareto_create_new(request):
    user = request.user
    pareto_date = datetime.now(timezone.utc).date()
    form = NewPareto(request.POST or None)
    if form.is_valid():
        shift = form.cleaned_data["shift"]
        hours = form.cleaned_data["hours"]
        ops = form.cleaned_data["ops"]
        time_start = LineHourModel.objects.get(user=user, shift=shift)

        time_stamp = datetime.strptime(str(time_start), "%H:%M:%S")
        Pareto.objects.create(user=user, completed=False, shift=shift, hours=hours, pareto_date=pareto_date,
                              time_stamp=time_stamp, ops=ops)
        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


class ParetoUpdateView(UpdateView):
    model = Pareto
    template_name = "form.html"
    form_class = ParetoUpdateForm
    success_url = reverse_lazy("gemba_app:pareto-summary")


class ScrapDetailView(DetailView):
    model = ScrapDetail
    template_name = "gemba/scrap_detail_view.html"


class ScrapUpdateView(UpdateView):
    model = ScrapDetail
    fields = ("job", "qty",)
    template_name = "form.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class ScrapDeleteView(DeleteView):
    model = ScrapDetail
    template_name = "gemba/delete_scrap.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class DowntimeDetailView(DetailView):
    model = DowntimeDetail
    template_name = "gemba/downtime_detail_view.html"


class DowntimeUpdateView(UpdateView):
    model = DowntimeDetail
    fields = ("job", "minutes", "frequency", )
    template_name = "form.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class DowntimeDeleteView(DeleteView):
    model = DowntimeDetail
    template_name = "gemba/delete_downtime.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class ParetoDetailView(DetailView):
    model = ParetoDetail
    template_name = "gemba/pareto_detail_view.html"


class ParetoDetailUpdateView(UpdateView):
    model = ParetoDetail
    fields = ("job", "qty", "good",)
    template_name = "form.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class ParetoDetailDeleteView(DeleteView):
    model = ParetoDetail
    template_name = "gemba/delete_detail.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


@login_required
def add_scrap_detail(request, pk):
    scrap = get_object_or_404(ScrapDetail, pk=pk)
    old_qty = scrap.qty
    form = ScrapQuantity(request.POST or None)
    if form.is_valid():
        qty = form.cleaned_data["qty"]
        new_qty = qty + old_qty

        scrap.qty = new_qty
        scrap.save()
        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@login_required
def add_downtime_time(request, pk):
    downtime = get_object_or_404(DowntimeDetail, pk=pk)
    old_time = downtime.minutes
    form = DowntimeMinutes(request.POST or None)
    if form.is_valid():
        minutes = form.cleaned_data["minutes"]
        new_time = minutes + old_time

        downtime.minutes = new_time
        downtime.save()
        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


def downtime_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    general_list = DowntimeUser.objects.filter(group=1).order_by("order")
    group_qs = DowntimeGroup.objects.filter(user=request.user)
    message_status = ""
    job_otg = pareto.job_otg
    # setup on id=0 Not selected
    job_message = JobModel2.objects.get(id=1)

    if job_otg == job_message:
        message_status = "Display"

    if group_qs.exists():
        group = group_qs[0]
        items_list = DowntimeUser.objects.filter(group=group).order_by("order")
    else:
        items_list = {}

    return render(
        request,
        template_name="gemba/downtime_user_view.html",
        context={
            "pareto": pareto,
            "message_status": message_status,
            "general_list": general_list,
            "items_list": items_list,
        },
    )


def scrap_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    general_list = ScrapUser.objects.filter(group=1).order_by("order")
    group_qs = DowntimeGroup.objects.filter(user=request.user)
    message_status = ""
    job_otg = pareto.job_otg
    # setup on id=0 Not selected
    job_message = JobModel2.objects.get(id=1)

    if job_otg == job_message:
        message_status = "Display"

    if group_qs.exists():
        group = group_qs[0]
        items_list = ScrapUser.objects.filter(group=group).order_by("order")
    else:
        items_list = {}

    return render(
        request,
        template_name="gemba/scrap_user_view.html",
        context={
            "pareto": pareto,
            "message_status": message_status,
            "general_list": general_list,
            "items_list": items_list,
        },
    )


def job_user_list(request):
    group = DowntimeGroup.objects.get(user=request.user)
    job_qs = JobModel2.objects.filter(group=group).order_by("name")

    return render(
        request,
        template_name="gemba/job_user_view.html",
        context={
            "job_list": job_qs,
        },
    )


def select_job(request, pk):
    job = get_object_or_404(JobModel2, pk=pk)
    pareto = Pareto.objects.get(user=request.user, completed=False)
    pareto.job_otg = job
    pareto.save()
    return redirect("gemba_app:pareto-summary")


class SearchResultsView(ListView):
    model = DowntimeDetail
    template_name = "gemba/downtimes_search.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = DowntimeDetail.objects.filter(
            Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
            Q(downtime__code__icontains=query) | Q(downtime__description__icontains=query) |
            Q(minutes__icontains=query) | Q(job__name__icontains=query) |
            Q(pareto_id__icontains=query)
        ).order_by('-id')
        return object_list


class ScrapSearchResultsView(ListView):
    model = ScrapDetail
    template_name = "gemba/scraps_search.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = ScrapDetail.objects.filter(
            Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
            Q(scrap__code__icontains=query) | Q(scrap__description__icontains=query) |
            Q(qty__icontains=query) | Q(job__name__icontains=query) |
            Q(pareto_id__icontains=query)
        ).order_by('-id')
        return object_list


def quarantine_view(request):
    quarantine_qs = ScrapDetail.objects.filter(scrap=8).order_by("-id")

    return render(
        request,
        template_name="gemba/quarantine_view.html",
        context={
            "quarantine_qs": quarantine_qs,
        },
    )


def export_scrap_search_csv(request):
    query = request.GET.get("q")
    object_list = ScrapDetail.objects.filter(
        Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
        Q(scrap__code__icontains=query) | Q(scrap__description__icontains=query) |
        Q(qty__icontains=query) | Q(job__name__icontains=query) |
        Q(pareto_id__icontains=query)
    ).order_by('id')
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Scrap_reasons.csv"'
    writer = csv.writer(response)
    writer.writerow(["Id", "Date", "User/Line", "Code - Description", "Qty", "Job", "Pareto id"])
    for e in object_list:
        writer.writerow([e.id,
                         e.pareto_date,
                         e.user,
                         e.scrap,
                         e.qty,
                         e.job,
                         e.pareto_id,
                         ])
    return response


def export_downtime_search_result_csv(request):
    query = request.GET.get("q")
    object_list = DowntimeDetail.objects.filter(
        Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
        Q(downtime__code__icontains=query) | Q(downtime__description__icontains=query) |
        Q(minutes__icontains=query) | Q(job__name__icontains=query) |
        Q(pareto_id__icontains=query)
    ).order_by('id')
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Downtime_reasons.csv"'
    writer = csv.writer(response)
    writer.writerow(["Id", "Date", "User/Line", "Code - Description", "Minutes", "Job", "Pareto id"])
    for e in object_list:
        writer.writerow([e.id,
                         e.pareto_date,
                         e.user,
                         e.downtime,
                         e.minutes,
                         e.job,
                         e.pareto_id,
                         ])
    return response


def export_downtimes_xls(request):
    query = request.GET.get("q")
    object_list = DowntimeDetail.objects.filter(
        Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
        Q(downtime__code__icontains=query) | Q(downtime__description__icontains=query) |
        Q(minutes__icontains=query) | Q(job__name__icontains=query) |
        Q(pareto_id__icontains=query)
    ).order_by('id')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Downtime_reasons.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Report')

    row_num = 1
    rows = object_list.values('id', 'pareto_date', 'user__username', 'downtime__code', 'downtime__description',
                              'minutes', 'job__name', 'pareto_id')
    row_list = ['id', 'pareto_date', 'user__username', 'downtime__code', 'downtime__description',
                'minutes', 'job__name', 'pareto_id']
    headers = ["Id", "Pareto date", "Line / User", "Code", "Description", "Minutes", "Job", "Pareto Id"]
    for col_num in range(len(row_list)):
        style = xlwt.easyxf('font: bold 1')
        ws.write(0, col_num, headers[col_num], style)

    for row in rows:
        for col_num in range(len(row_list)):
            elem = row[row_list[col_num]]
            ws.write(row_num, col_num, elem)
        row_num += 1
    wb.save(response)

    return response


class IndexView(ListView):
    model = Timer

    def post(self, request):
        Timer.objects.create()
        return redirect('gemba/index.html')


class ParetoNSUpdateView(UpdateView):
    model = Pareto
    template_name = "form.html"
    form_class = NotScheduledToRunUpdateForm
    success_url = reverse_lazy("gemba_app:pareto-summary")


def pareto_details_query(request):
    details = ParetoDetail.objects.all().order_by("-pareto_date")
    details_filter = ParetoDetailFilter(request.GET, queryset=details)

    details_list = details_filter.qs
    total_output = 0
    total_good = 0
    for detail in details_list.values_list("qty", "good"):
        total_output += detail[0]
        total_good += detail[1]
    return render(
        request,
        template_name="gemba/pareto_details_view.html",
        context={
            "filter": details_filter,
            "total_output": total_output,
            "total_good": total_good,
        },
    )


from django.views.generic import View
from django.http import JsonResponse, Http404

from gemba.models import Timer, TimerResumeException


class TimerView(View):

    def get_json_response(self):
        if not hasattr(self, 'timer') or not self.timer:
            raise Http404
        return JsonResponse({
            'status': self.timer.status,
            'duration': self.timer.duration().total_seconds(),
        })

    def get_timer(self, pk):
        try:
            return Timer.objects.get(pk=pk)
        except Timer.DoesNotExist:
            pass

    def post(self, request, pk=None):
        self.timer = self.get_timer(pk)
        self.action(request, pk)
        return self.get_json_response()

    def get_user(self, request):
        if request.user.is_authenticated:
            return request.user

    def action(self, request, pk):
        raise NotImplementedError('{} has to define an action method.'.format(self.__class__))


class Start(TimerView):

    def action(self, request, pk):
        self.timer.start()


class Pause(TimerView):

    def action(self, request, pk):
        self.timer.pause()


class Resume(TimerView):

    def action(self, request, pk):
        try:
            self.timer.resume()
        except TimerResumeException:
            pass


class Stop(TimerView):

    def action(self, request, pk):
        self.timer.stop()
