import csv
from itertools import chain

import pytz
import xlwt
from django.core.paginator import Paginator
from xlwt import XFStyle, Font
from datetime import datetime, timezone, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView, ListView
from django.db.models import Q

from gemba.forms import DowntimeMinutes, ScrapQuantity, NewPareto, ParetoUpdateForm, \
    NotScheduledToRunUpdateForm, ParetoTotalQtyDetailForm, ParetoDetailUpdateForm, OperatorsChoice, ParetoDetailHCBForm, \
    ParetoDetailHCIForm
from gemba.models import Pareto, ParetoDetail, DowntimeModel, DowntimeDetail, ScrapModel, ScrapDetail, DowntimeUser, \
    ScrapUser, LineHourModel, JobModel2, SHIFT_CHOICES, TC, Editors, LineUser, Line, Timer, JobLine, \
    PRODUCTIVE, HCI, HCB
from tools.views import tools_update


class GembaIndex(TemplateView):
    template_name = 'gemba/index.html'


def downtimes_view(request):
    downtimes = DowntimeDetail.objects.all().order_by("-modified")
    last_week_downtimes = DowntimeDetail.objects.filter(pareto_date__gte=datetime.now() - timedelta(days=7)).order_by(
        "-modified")

    paginator = Paginator(last_week_downtimes, 100)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,
                  template_name="gemba/downtimes_view.html",
                  context={
                      "filter": downtimes,
                      "page_obj": page_obj,
                  })


def scraps_view(request):
    scraps = ScrapDetail.objects.all().order_by("-modified")
    last_week_scraps = ScrapDetail.objects.filter(pareto_date__gte=datetime.now() - timedelta(days=7)).order_by(
        "-modified")
    paginator = Paginator(last_week_scraps, 100)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,
                  template_name="gemba/scraps_view.html",
                  context={
                      "filter": scraps,
                      "page_obj": page_obj,
                  })


def pareto_details_view(request):
    pareto_details = ParetoDetail.objects.all().order_by("-modified")
    last_week_pareto_details = ParetoDetail.objects.filter(pareto_date__gte=datetime.now() - timedelta(days=7)
                                                           ).order_by("-modified")
    paginator = Paginator(last_week_pareto_details, 100)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,
                  template_name="gemba/pareto_details_view.html",
                  context={
                      "filter": pareto_details,
                      "page_obj": page_obj,
                  })


@login_required
def downtime_detail_create(request, pk):
    downtime = get_object_or_404(DowntimeModel, pk=pk)
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    pareto = pareto_qs[0]
    pareto_id = pareto.id
    pareto_date = pareto.pareto_date
    job = pareto.job_otg
    line = pareto.line

    # make sure this is set up downtime reason
    if pk == "7":
        pareto_before_qs = ParetoDetail.objects.filter(user=request.user).order_by("-id")
        pareto_before_obj = pareto_before_qs[1]
        job_before_id = pareto_before_obj.job_id
        job_before_obj = JobModel2.objects.get(id=job_before_id)
        job_before = job_before_obj.name
    else:
        job_before = ""

    if job is None:
        return redirect("gemba_app:pareto-summary")

    # downtime_qs = DowntimeDetail.objects.filter(user=request.user, completed=False, downtime_id=pk, job=job)
    #
    # if downtime_qs.exists():
    #     downtime_id = downtime_qs[0].id
    #     downtime = DowntimeDetail.objects.get(id=downtime_id)
    #     old_time = downtime.minutes
    #     form = DowntimeMinutes(request.POST or None)
    #     if form.is_valid():
    #         minutes = form.cleaned_data["minutes"]
    #         new_time = minutes + old_time
    #         downtime.minutes = new_time
    #         downtime.frequency += 1
    #         downtime.save()
    #         return redirect("gemba_app:pareto-summary")
    # else:
    form = DowntimeMinutes(request.POST or None)

    if form.is_valid():
        minutes = form.cleaned_data["minutes"]
        user = request.user
        downtime_elem = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user, job=job,
                                                      from_job=job_before, pareto_id=pareto_id, pareto_date=pareto_date,
                                                      line=line)
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
    line = pareto.line

    # make sure this is set up
    if pk == "1":
        pareto_before_qs = ParetoDetail.objects.filter(user=request.user).order_by("-id")
        pareto_before_obj = pareto_before_qs[1]
        job_before_id = pareto_before_obj.job_id
        job_before_obj = JobModel2.objects.get(id=job_before_id)
        job_before = job_before_obj.name
    else:
        job_before = ""

    if job is None:
        return redirect("gemba_app:pareto-summary")

    form = ScrapQuantity(request.POST or None)
    if form.is_valid():
        qty = form.cleaned_data["qty"]
        user = request.user
        # scrap_qs = ScrapDetail.objects.filter(user=request.user, completed=False, scrap=scrap, job=job)

        # if scrap_qs.exists():
        #     scrap_elem = ScrapDetail.objects.get(scrap=scrap, user=user, job=job)
        #     scrap_elem.qty += qty
        #     scrap_elem.save()
        #     return redirect("gemba_app:pareto-summary")
        # else:
        scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job, from_job=job_before,
                                                pareto_id=pareto_id, pareto_date=pareto_date, line=line)
        pareto.scrap.add(scrap_elem)
        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@login_required
def pareto_detail_create(request):
    user = request.user
    pareto_qs = Pareto.objects.filter(user=user, completed=False)
    pareto = pareto_qs[0]
    job = pareto.job_otg
    ops = pareto.ops_otg

    line = pareto.line
    if job is None:
        return redirect("gemba_app:pareto-summary")

    name_id = pareto.job_otg_id
    job_qs = JobLine.objects.filter(job=name_id)
    job_obj = job_qs[0]
    target = job_obj.target
    takt_time = round(60 / target, ndigits=5)
    pareto_details_qs = ParetoDetail.objects.filter(user=user, completed=False, job=job)

    total_output = 0
    total_good = 0

    for elem in pareto_details_qs:
        total_output += elem.output
        total_good += elem.good

    pareto_id = pareto.id
    pareto_date = pareto.pareto_date
    line_qs = Line.objects.filter(name=line)
    calc_option = line_qs[0].calculation

    if calc_option == TC:
        form = ParetoTotalQtyDetailForm(request.POST or None)
        if form.is_valid():
            output = form.cleaned_data["output"]
            good = form.cleaned_data["good"]

            new_output = output - total_output
            new_good = good - total_good
            scrap = output - good
            scrap_qs = ScrapDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)

            rework_cal = 0
            for scrap_elem in scrap_qs:
                scrap_id = scrap_elem.scrap_id
                scrap_obj = ScrapModel.objects.get(id=scrap_id)
                rework = scrap_obj.rework
                if rework is True:
                    rework_cal += scrap_elem.qty

            if pareto_details_qs.exists():
                pareto_elem = ParetoDetail.objects.get(user=user, job=job, pareto_id=pareto_id)
                pareto_elem.output += new_output
                pareto_elem.good += new_good
                pareto_elem.scrap = scrap
                pareto_elem.rework = rework_cal
                pareto_elem.save()

                # tools update
                modified = pareto_elem.modified
                tools_update(job=job, output=new_output, target=target, modified=modified)

                return redirect("gemba_app:pareto-summary")

            else:
                pareto_elem = ParetoDetail.objects.create(job=job, output=output, user=user, good=good,
                                                          pareto_id=pareto_id, line=line, ops=ops, rework=rework_cal,
                                                          pareto_date=pareto_date, scrap=scrap, takt_time=takt_time)
                pareto.jobs.add(pareto_elem)

                # tools update
                modified = pareto_elem.modified
                tools_update(job=job, output=output, target=target, modified=modified)

                return redirect("gemba_app:pareto-summary")

        return render(
            request,
            template_name="gemba/form.html",
            context={
                "form": form,
                "total_output": total_output,
                "total_good": total_good,
            })
    elif calc_option == HCI:
        form = ParetoDetailHCIForm(request.POST or None)
        if form.is_valid():
            good = form.cleaned_data["good"]

            scrap_qs = ScrapDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)

            scrap = 0
            rework_cal = 0
            for scrap_elem in scrap_qs:
                scrap_id = scrap_elem.scrap_id
                scrap_obj = ScrapModel.objects.get(id=scrap_id)
                rework = scrap_obj.rework
                if rework is False:
                    scrap += scrap_elem.qty
                else:
                    rework_cal += scrap_elem.qty

            good_qs = ParetoDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)
            old_good = 0
            for good_elem in good_qs:
                old_good += good_elem.good

            job_elem = JobModel2.objects.get(name=job)
            inner_size = job_elem.inner_size

            cal_good = good * inner_size
            output = old_good + cal_good + scrap

            if pareto_details_qs.exists():
                pareto_elem = ParetoDetail.objects.get(user=user, job=job, pareto_id=pareto_id)
                pareto_elem.output = output
                pareto_elem.good += cal_good
                pareto_elem.scrap = scrap
                pareto_elem.rework = rework_cal
                pareto_elem.save()
                return redirect("gemba_app:pareto-summary")
            else:
                pareto_item = ParetoDetail.objects.create(job=job, output=output, user=user, good=cal_good,
                                                          pareto_id=pareto_id, line=line, ops=ops,
                                                          pareto_date=pareto_date, scrap=scrap, rework=rework_cal,
                                                          takt_time=takt_time)
                pareto.jobs.add(pareto_item)
                return redirect("gemba_app:pareto-summary")

        return render(
            request,
            template_name="form.html",
            context={
                "form": form,
            })

    elif calc_option == HCB:
        form = ParetoDetailHCBForm(request.POST or None)
        if form.is_valid():
            good = form.cleaned_data["good"]

            scrap_qs = ScrapDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)

            scrap = 0
            rework_cal = 0
            for scrap_elem in scrap_qs:
                scrap_id = scrap_elem.scrap_id
                scrap_obj = ScrapModel.objects.get(id=scrap_id)
                rework = scrap_obj.rework
                if rework is False:
                    scrap += scrap_elem.qty
                else:
                    rework_cal += scrap_elem.qty

            good_qs = ParetoDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)
            old_good = 0
            for good_elem in good_qs:
                old_good += good_elem.good

            output = old_good + good + scrap

            if pareto_details_qs.exists():
                pareto_elem = ParetoDetail.objects.get(user=user, job=job, pareto_id=pareto_id)
                pareto_elem.output = output
                pareto_elem.good += good
                pareto_elem.scrap = scrap
                pareto_elem.rework = rework_cal
                pareto_elem.save()
                return redirect("gemba_app:pareto-summary")
            else:
                pareto_item = ParetoDetail.objects.create(job=job, output=output, user=user, good=good,
                                                          pareto_id=pareto_id, line=line, ops=ops,
                                                          pareto_date=pareto_date, scrap=scrap, rework=rework_cal,
                                                          takt_time=takt_time)
                pareto.jobs.add(pareto_item)
                return redirect("gemba_app:pareto-summary")

        return render(
            request,
            template_name="form.html",
            context={
                "form": form,
            })
    else:
        pass


class ParetoSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user = self.request.user
        pareto_qs = Pareto.objects.filter(user=user, completed=False)
        if pareto_qs.exists():
            pareto = pareto_qs[0]

            pareto_id = pareto.id
            pareto_status = ""
            status = pareto.completed
            hours = pareto.hours
            time_stamp = pareto.time_stamp
            not_scheduled_to_run = pareto.not_scheduled_to_run

            message_status = ""
            job_otg = pareto.job_otg
            if job_otg is None:
                message_status = "Display"

            available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp,
                                                not_scheduled_to_run=not_scheduled_to_run)

            pareto_details = ParetoDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id)
            total_good = 0
            total_output = 0
            total_rework = 0
            if pareto_details.exists():
                for scrap_cal in pareto_details:
                    output = scrap_cal.output
                    rework = scrap_cal.rework
                    total_output += output
                    good = scrap_cal.good
                    total_good += good
                    total_rework += rework
            total_scrap_cal = total_output - total_good

            quality = quality_cal(good=total_good, output=total_output)

            down_qs = DowntimeDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id).order_by(
                "-modified")
            total_down = 0
            if down_qs.exists():
                for down in down_qs:
                    quantity = down.minutes
                    total_down += quantity

            availability = availability_cal(available_time=available_time, downtime=total_down)

            scrap_qs = ScrapDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id).order_by("-modified")

            total_scrap = 0
            for scrap_elem in scrap_qs:
                scrap_id = scrap_elem.scrap_id
                scrap = ScrapModel.objects.get(id=scrap_id)
                rework = scrap.rework
                qty = scrap_elem.qty
                if rework is False:
                    total_scrap += qty

            performance_numerator = 0

            if pareto_details.exists():
                for pareto_detail in pareto_details:
                    job_elem = pareto_detail.job_id
                    job_qs = JobLine.objects.filter(job=job_elem)
                    job_obj = job_qs[0]
                    takt_time = round(60 / job_obj.target, 5)
                    qty_elem = pareto_detail.output
                    performance_numerator += (qty_elem * takt_time)

            performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                          downtime=total_down)

            oee = oee_cal(availability=availability, performance=performance, quality=quality)

            return render(self.request,
                          template_name='gemba/pareto.html',
                          context={
                              "pareto_list": pareto,
                              "down_qs": down_qs,
                              "scrap_qs": scrap_qs,
                              "user": user,
                              "pareto_status": pareto_status,
                              "message_status": message_status,
                              "available_time": available_time,
                              "availability": availability,
                              "quality": quality,
                              "performance": performance,
                              "oee": oee,
                              "total_scrap": total_scrap,
                              "total_rework": total_rework,
                              "total_down": total_down,
                              "total_output": total_output,
                              "total_good": total_good,
                              "total_scrap_cal": total_scrap_cal,
                          },
                          )
        else:
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
            total_rework = 0

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
                              "total_rework": total_rework,
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
        performance = round((performance_numerator / (available_time - downtime)) * 100, ndigits=2)
    else:
        performance = 0
    return performance


def quality_cal(good, output):
    if output != 0:
        quality = round((good / output) * 100, ndigits=2)
    else:
        quality = 0
    return quality


def availability_cal(available_time, downtime):
    if available_time == 0:
        availability = 0
    else:
        availability = round(((available_time - downtime) / available_time * 100), ndigits=2)
    return availability


def oee_cal(availability, performance, quality):
    divider = 10000

    if availability == 0 or performance == 0 or quality == 0:
        return 0

    availability = int(availability * 100)
    divider *= 100
    performance = int(performance * 100)
    divider *= 100
    quality = int(quality * 100)
    divider *= 100

    oee = round(availability * performance * quality / divider, ndigits=2)

    return oee


def pareto_detail_view(request, pk):
    pareto = Pareto.objects.get(pk=pk)
    report_list = oee_calculation(pareto)

    downtimes = []
    downtimes_list = []
    for down_obj in pareto.downtimes.all():
        down_code = down_obj.downtime.code
        down_desc = down_obj.downtime.description
        job = down_obj.job.name
        if down_desc not in downtimes:
            down_time = down_obj.minutes
            downtimes_list.append({
                "job": job,
                "code": down_code,
                "description": down_desc,
                "minutes": down_time,
                "frequency": 1,
            })
            downtimes.append(down_desc)
        else:
            pos = downtimes.index(down_desc)
            minutes = down_obj.minutes
            elem_job = downtimes_list[pos]["job"]
            if elem_job == job:
                downtimes_list[pos]["minutes"] += minutes
                downtimes_list[pos]["frequency"] += 1
            else:
                downtimes_list.append({
                    "job": job,
                    "code": down_code,
                    "description": down_desc,
                    "minutes": minutes,
                    "frequency": 1,
                })
    scraps = []
    scraps_list = []
    for scrap_obj in pareto.scrap.all():
        scrap_code = scrap_obj.scrap.code
        scrap_desc = scrap_obj.scrap.description
        scrap_id = scrap_obj.scrap_id
        job = scrap_obj.job.name
        if scrap_id not in scraps:
            scrap_qty = scrap_obj.qty
            scraps_list.append({
                "job": job,
                "code": scrap_code,
                "description": scrap_desc,
                "qty": scrap_qty,
                "frequency": 1,
            })
            scraps.append(scrap_id)
        else:
            pos = scraps.index(scrap_id)
            qty = scrap_obj.qty
            elem_job = scraps_list[pos]["job"]
            print(f"Job {job} == {elem_job} + {qty}")
            if elem_job == job:
                scraps_list[pos]["qty"] += qty
                scraps_list[pos]["frequency"] += 1
            else:
                scraps_list.append({
                    "job": job,
                    "code": scrap_code,
                    "description": scrap_desc,
                    "qty": qty,
                    "frequency": 1,
                })

    return render(request,
                  template_name='gemba/pareto_details.html',
                  context={
                      "pareto_list": pareto,
                      "report_list": report_list,
                      "downtimes_list": downtimes_list,
                      "scraps_list": scraps_list,
                  },
                  )


# when depends on the status
def oee_calculation(pareto):
    hours = pareto.hours
    not_scheduled_to_run = pareto.not_scheduled_to_run
    status = pareto.completed
    time_stamp = pareto.time_stamp

    available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp,
                                        not_scheduled_to_run=not_scheduled_to_run)
    calculation = {}

    output = 0
    good = 0
    performance_numerator = 0

    calculation["available_time"] = available_time

    for detail in pareto.jobs.all():
        output += detail.output
        good += detail.good
        performance_numerator += (detail.output * detail.takt_time)

    if status is True:
        quality = pareto.quality
    else:
        quality = quality_cal(good=good, output=output)
    calculation["quality"] = quality
    calculation["good"] = good

    downtime = 0
    for down_elem in pareto.downtimes.all():
        downtime += down_elem.minutes

    calculation["output"] = output
    calculation["downtime"] = downtime

    if status is True:
        performance = pareto.performance
    else:
        performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                      downtime=downtime)
    calculation["performance"] = performance

    availability = availability_cal(available_time=available_time, downtime=downtime)
    calculation["availability"] = availability

    if status is True:
        oee = pareto.oee
    else:
        oee = oee_cal(availability=availability, performance=performance, quality=quality)

    calculation["oee"] = oee
    scrap = 0
    for scrap_elem in pareto.scrap.all():
        scrap += scrap_elem.qty

    calculation["scrap"] = scrap

    return calculation


# when status not completed, but wants to see how it will be saved
def final_oee_calculation(pareto):
    hours = pareto.hours
    not_scheduled_to_run = pareto.not_scheduled_to_run

    available_time = int(hours) * 60 - not_scheduled_to_run

    calculation = {}

    output = 0
    good = 0
    performance_numerator = 0

    calculation["available_time"] = available_time

    for detail in pareto.jobs.all():
        output += detail.output
        good += detail.good
        performance_numerator += (detail.output * detail.takt_time)

    quality = quality_cal(good=good, output=output)
    calculation["quality"] = quality
    calculation["good"] = good

    downtime = 0
    for down_elem in pareto.downtimes.all():
        downtime += down_elem.minutes

    calculation["output"] = output
    calculation["downtime"] = downtime

    performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                  downtime=downtime)
    calculation["performance"] = performance

    availability = availability_cal(available_time=available_time, downtime=downtime)
    calculation["availability"] = availability

    oee = oee_cal(availability=availability, performance=performance, quality=quality)

    calculation["oee"] = oee
    scrap = 0
    rework_cal = 0
    for scrap_elem in pareto.scrap.all():
        scrap_id = scrap_elem.scrap_id
        scrap_obj = ScrapModel.objects.get(id=scrap_id)
        rework = scrap_obj.rework
        if rework is False:
            scrap += scrap_elem.qty
        else:
            rework_cal += scrap_elem.qty

    calculation["rework"] = rework_cal
    calculation["scrap"] = scrap

    return calculation


def before_close_pareto(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    pareto_id = pareto.id

    line = pareto.line
    line_qs = Line.objects.filter(name=line)
    calc_option = line_qs[0].calculation
    if calc_option == HCI or calc_option == HCB:
        pareto_details_qs = ParetoDetail.objects.filter(user=request.user, completed=False,
                                                        pareto_id=pareto_id).order_by("-id")
        last_detail = pareto_details_qs[0]

        # balance amount of scraps and rework, only good is correct
        good = last_detail.good
        job = last_detail.job_id

        scraps_qs = ScrapDetail.objects.filter(user=request.user, completed=False,
                                               pareto_id=pareto_id, job=job)
        scrap = 0
        rework = 0
        for scrap_obj in scraps_qs:
            scrap_id = scrap_obj.scrap_id
            scrap_elem = ScrapModel.objects.get(id=scrap_id)
            if scrap_elem.rework is False:
                scrap += scrap_obj.qty
            else:
                rework += scrap_obj.qty
        output = good + scrap

        last_detail.output = output
        last_detail.scrap = scrap
        last_detail.good = good
        last_detail.save()
    elif calc_option == TC:
        pareto_details_qs = ParetoDetail.objects.filter(user=request.user, completed=False,
                                                        pareto_id=pareto_id).order_by("-id")
        last_detail = pareto_details_qs[0]

        # balance amount of rework
        job = last_detail.job_id

        scraps_qs = ScrapDetail.objects.filter(user=request.user, completed=False,
                                               pareto_id=pareto_id, job=job)
        rework = 0
        for scrap_obj in scraps_qs:
            scrap_id = scrap_obj.scrap_id
            scrap_elem = ScrapModel.objects.get(id=scrap_id)
            if scrap_elem.rework is True:
                rework += scrap_obj.qty

        last_detail.rework = rework
        last_detail.save()

    calculation = final_oee_calculation(pareto)

    available_time = calculation["available_time"]
    output = calculation["output"]
    good = calculation["good"]
    downtime = calculation["downtime"]
    availability = calculation["availability"]
    quality = calculation["quality"]
    performance = calculation["performance"]
    oee = calculation["oee"]
    scrap = calculation["scrap"]
    rework = calculation["rework"]
    scrap_compare = output - good - scrap

    return render(request,
                  template_name='gemba/pareto_before_close.html',
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
                      "scrap_compare": scrap_compare,
                      "rework": rework,
                  },
                  )


@login_required
def final_confirmation_before_close_pareto(request):
    return render(request,
                  template_name='gemba/pareto_final_qs_before_close.html')


@login_required
def close_pareto(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)

    calculation = final_oee_calculation(pareto)

    availability = calculation["availability"]
    quality = calculation["quality"]
    performance = calculation["performance"]
    oee = calculation["oee"]

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

    pareto.availability = availability
    pareto.performance = performance
    pareto.quality = quality
    pareto.oee = oee
    pareto.completed = True
    pareto.save()

    return redirect("gemba_app:index")


# more than one pareto
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
        line = pareto.line
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
            output += detail.output
            good += detail.good
            performance_numerator += (detail.output * detail.takt_time)

        if status is True:
            quality = pareto.quality
        else:
            quality = quality_cal(good=good, output=output)

        downtime = 0
        for down_elem in pareto.downtimes.all():
            downtime += down_elem.minutes

        if status is True:
            performance = pareto.performance
        else:
            performance = performance_cal(performance_numerator=performance_numerator, available_time=available_time,
                                          downtime=downtime)

        if status is True:
            availability = pareto.availability
        else:
            availability = availability_cal(available_time=available_time, downtime=downtime)

        if status is True:
            oee = pareto.oee
        else:
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
            "line": line,
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
        if query == "":
            report_list = Pareto.objects.filter(
                Q(pareto_date__exact=datetime.now(tz=pytz.UTC).date())
            ).order_by("line", "id")
        else:
            report_list = Pareto.objects.filter(
                Q(pareto_date__exact=query)
            ).order_by("line", "id")
        object_list = get_details_to_display(object_list=report_list)
        return object_list


def export_daily_oee_report_xls(request):
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
    today_pareto = Pareto.objects.filter(pareto_date=datetime.now()).order_by("line", "id")

    report_list = get_details_to_display(object_list=today_pareto)

    return render(request,
                  template_name="gemba/pareto_view.html",
                  context={
                      "report_list": report_list,
                  },
                  )


START_CHOICES = (
    (SHIFT_CHOICES[1][1], "06:00:00"),
    (SHIFT_CHOICES[2][1], "14:00:00"),
    (SHIFT_CHOICES[3][1], "22:00:00"),
)


@login_required
def pareto_create_new(request):
    user = request.user
    line_user_qs = LineUser.objects.filter(user=user)

    if line_user_qs.exists():
        line = line_user_qs[0].line
    else:
        return render(
            request,
            template_name="gemba/error_pareto.html",
        )

    pareto_date = datetime.now(timezone.utc).date()
    form = NewPareto(request.POST or None)
    if form.is_valid():
        shift = form.cleaned_data["shift"]
        hours = form.cleaned_data["hours"]
        ops_otg = form.cleaned_data["ops_otg"]

        time_start_qs = LineHourModel.objects.filter(line=line, shift=shift)

        if time_start_qs.exists():
            time_stamp_obj = time_start_qs[0].start
            time_stamp = datetime.strptime(str(time_stamp_obj), "%H:%M:%S")
        else:
            if shift == SHIFT_CHOICES[1][1]:
                time_stamp = datetime.strptime(str(START_CHOICES[0][1]), "%H:%M:%S")
            elif shift == SHIFT_CHOICES[2][1]:
                time_stamp = datetime.strptime(str(START_CHOICES[1][1]), "%H:%M:%S")
            else:
                time_stamp = datetime.strptime(str(START_CHOICES[2][1]), "%H:%M:%S")

        Pareto.objects.create(user=user, completed=False, shift=shift, hours=hours, pareto_date=pareto_date,
                                    time_stamp=time_stamp, line=line, ops_otg=ops_otg)
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
    fields = ("job", "minutes", "frequency",)
    template_name = "form.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class DowntimeDeleteView(DeleteView):
    model = DowntimeDetail
    template_name = "gemba/delete_downtime.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class ParetoDetailView(DetailView):
    model = ParetoDetail
    template_name = "gemba/pareto_detail_view.html"


@login_required
def pareto_detail_update(request, pk):
    pareto_detail_obj = ParetoDetail.objects.get(pk=pk)
    line = pareto_detail_obj.line
    form = ParetoDetailUpdateForm(instance=pareto_detail_obj)

    old_job = pareto_detail_obj.job
    job_line_qs = JobLine.objects.filter(line=line, job=old_job)

    target = job_line_qs[0].target
    old_output = pareto_detail_obj.output * -1
    modified = pareto_detail_obj.modified
    line = pareto_detail_obj.line

    if request.method == "POST":
        form = ParetoDetailUpdateForm(request.POST, instance=pareto_detail_obj)
        if form.is_valid():
            job = form.cleaned_data["job"]
            output = form.cleaned_data["output"]
            good = form.cleaned_data["good"]
            scrap = form.cleaned_data["scrap"]

            pareto_detail_obj.job = job
            pareto_detail_obj.output = output
            pareto_detail_obj.good = good
            pareto_detail_obj.scrap = scrap
            pareto_detail_obj.save()

            if job == old_job:
                add_output = output + old_output
                tools_update(job=old_job, output=add_output, target=target, modified=modified)
            else:
                # tools update
                job_qs = JobLine.objects.filter(job=job, line=line)
                job_obj = job_qs[0]
                new_target = job_obj.target
                tools_update(job=old_job, output=old_output, target=target, modified=modified)
                tools_update(job=job, output=output, target=new_target, modified=modified)

            return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@login_required
def pareto_detail_delete(request, pk):
    pareto_detail_obj = ParetoDetail.objects.get(pk=pk)

    old_job = pareto_detail_obj.job
    old_job_id = pareto_detail_obj.job_id
    line = pareto_detail_obj.line_id
    line_job_qs = JobLine.objects.filter(job=old_job_id, line=line)
    target = line_job_qs[0].target
    old_output = pareto_detail_obj.output * -1
    modified = pareto_detail_obj.modified

    if request.method == "POST":
        pareto_detail_obj.delete()
        # tools update
        tools_update(job=old_job, output=old_output, target=target, modified=modified)
        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="gemba/delete_detail.html",
        context={"object": pareto_detail_obj}
    )


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


def timer(request):
    Timer.objects.create(user=request.user)
    return redirect("gemba_app:downtime-user-view")


def reset_timer(request):
    timer_qs = Timer.objects.filter(user=request.user, completed=False)
    for timer_obj in timer_qs:
        timer_obj.delete()
    return redirect("gemba_app:downtime-user-view")


def downtime_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    line = pareto.line
    message_status = ""
    job_otg = pareto.job_otg

    if job_otg is None:
        message_status = "Display"

    timer_qs = Timer.objects.filter(user=request.user, completed=False).order_by("-start")
    if timer_qs.exists():
        timer_obj = timer_qs[0]
        start_time = timer_obj.start
        time_now = datetime.now(tz=pytz.UTC)
        sec_now = int(time_now.strftime('%S'))
        sec_now += int(time_now.strftime('%M')) * 60
        sec_now += int(time_now.strftime('%H')) * 60 * 60

        sec_start = int(start_time.strftime('%S'))
        sec_start += int(start_time.strftime('%M')) * 60
        sec_start += int(start_time.strftime('%H')) * 60 * 60

        down_length = round((sec_now - sec_start) / 60.0)
    else:
        down_length = 0
        timer_obj = ""

    items_list = DowntimeUser.objects.filter(line=line).filter(order__gt=0).order_by("order")

    return render(
        request,
        template_name="gemba/downtime_user_view.html",
        context={
            "pareto": pareto,
            "message_status": message_status,
            "items_list": items_list,
            "timer_obj": timer_obj,
            "down_length": down_length,
        },
    )


def scrap_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    line = pareto.line
    message_status = ""
    job_otg = pareto.job_otg

    if job_otg is None:
        message_status = "Display"

    items_list = ScrapUser.objects.filter(line=line).filter(order__gt=0).order_by("order")

    return render(
        request,
        template_name="gemba/scrap_user_view.html",
        context={
            "pareto": pareto,
            "message_status": message_status,
            "items_list": items_list,
        },
    )


def job_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    line = pareto.line
    job_qs = JobLine.objects.filter(line=line).order_by("job")

    return render(
        request,
        template_name="gemba/job_user_view.html",
        context={
            "job_list": job_qs,
        },
    )


def select_job(request, pk):
    job_line_obj = JobLine.objects.get(pk=pk)
    job = job_line_obj.job_id
    job_obj = JobModel2.objects.get(id=job)
    pareto = Pareto.objects.get(user=request.user, completed=False)
    pareto.job_otg = job_obj
    pareto.save()
    return redirect("gemba_app:pareto-summary")


class DowntimeSearchResultsView(ListView):
    model = DowntimeDetail
    template_name = "gemba/downtimes_search.html"
    paginate_by = 100

    def get_queryset(self):
        query = self.request.GET.get("q")
        page_obj = DowntimeDetail.objects.filter(
            Q(pareto_date__icontains=query) | Q(line__name__icontains=query) |
            Q(downtime__code__icontains=query) | Q(downtime__description__icontains=query) |
            Q(minutes__icontains=query) | Q(job__name__icontains=query) |
            Q(pareto_id__icontains=query) | Q(created__icontains=query)
        ).order_by('-modified')
        return page_obj


class ScrapSearchResultsView(ListView):
    model = ScrapDetail
    template_name = "gemba/scraps_search.html"
    paginate_by = 100

    def get_queryset(self):
        query = self.request.GET.get("q")
        page_obj = ScrapDetail.objects.filter(
            Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
            Q(scrap__code__icontains=query) | Q(scrap__description__icontains=query) |
            Q(qty__icontains=query) | Q(job__name__icontains=query) |
            Q(pareto_id__icontains=query)
        ).order_by('-modified')
        return page_obj


class ParetoDetailsSearchResultsView(ListView):
    model = ParetoDetail
    template_name = "gemba/pareto_details_search.html"
    paginate_by = 100

    def get_queryset(self):
        query = self.request.GET.get("q")
        page_obj = ParetoDetail.objects.filter(
            Q(pareto_date__icontains=query) | Q(user__username__icontains=query) |
            Q(good__icontains=query) | Q(output__icontains=query) |
            Q(scrap__icontains=query) | Q(job__name__icontains=query) |
            Q(pareto_id__icontains=query) | Q(modified__icontains=query) |
            Q(takt_time__icontains=query)
        ).order_by('-modified')
        return page_obj


# alter to Quarantine id
def quarantine_view(request):
    quarantine_qs = ScrapDetail.objects.filter(scrap=18).order_by("-modified")

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
                         e.output,
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


class ParetoNSUpdateView(UpdateView):
    model = Pareto
    template_name = "form.html"
    form_class = NotScheduledToRunUpdateForm
    success_url = reverse_lazy("gemba_app:pareto-summary")


class EditorChartView(TemplateView):
    template_name = 'gemba/chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["qs"] = Editors.objects.all()
        return context


@login_required
def open_pareto(request, pk):
    pareto = Pareto.objects.get(pk=pk)
    user = request.user

    down_items = pareto.downtimes.all()
    down_items.update(completed=False)
    down_items.update(user=user)
    for item in down_items:
        item.save()

    scrap_items = pareto.scrap.all()
    scrap_items.update(completed=False)
    scrap_items.update(user=user)
    for item in scrap_items:
        item.save()

    details_item = pareto.jobs.all()
    details_item.update(completed=False)
    details_item.update(user=user)
    for item in details_item:
        item.save()

    pareto.user = user
    pareto.completed = False
    pareto.save()

    return redirect("gemba_app:pareto-summary")


def lines(request):
    lines_qs = Line.objects.all().order_by("name")
    return render(request, "gemba/lines.html", {"lines_qs": lines_qs})


def lines_2(request):
    lines2_qs = Line.objects.all().order_by("name")
    return render(request, "gemba/lines2.html", {"lines2_qs": lines2_qs})


def scrap_rate_report_by_week(request, line_id):
    today = datetime.now(tz=pytz.UTC).replace(hour=21, minute=45, second=0, microsecond=0)

    report = []

    scrap_list = []
    scrap_names_qs = ScrapUser.objects.filter(line=line_id).order_by("gemba")
    scrap_row_qty = []
    for obj in scrap_names_qs:
        scrap_name = obj.scrap.description
        scrap_list.append(scrap_name)
        scrap_row_qty.append(0)

        report.append({
            "scrap": scrap_name,
            "qty_0": 0,
            "scrap_rate_0": 0.00,
            "qty_1": 0,
            "scrap_rate_1": 0.00,
            "qty_2": 0,
            "scrap_rate_2": 0.00,
            "qty_3": 0,
            "scrap_rate_3": 0.00,
            "qty_4": 0,
            "scrap_rate_4": 0.00,
            "qty_5": 0,
            "scrap_rate_5": 0.00,
            "qty_6": 0,
            "scrap_rate_6": 0.00,
            "qty_7": 0,
            "scrap_rate_7": 0.00,
            "qty_8": 0,
            "scrap_rate_8": 0.00,
            "total": 0,
            "total_scrap_rate": 0.00,
        })

    totals = {
        "total_weekly_0": 0,
        "total_output_0": 0,
        "overall_scrap_rate_0": 0.00,
        "start_monday_0": "",
        "total_weekly_1": 0,
        "total_output_1": 0,
        "overall_scrap_rate_1": 0.00,
        "start_monday_1": "",
        "total_weekly_2": 0,
        "total_output_2": 0,
        "overall_scrap_rate_2": 0.00,
        "start_monday_2": "",
        "total_weekly_3": 0,
        "total_output_3": 0,
        "overall_scrap_rate_3": 0.00,
        "start_monday_3": "",
        "total_weekly_4": 0,
        "total_output_4": 0,
        "overall_scrap_rate_4": 0.00,
        "start_monday_4": "",
        "total_weekly_5": 0,
        "total_output_5": 0,
        "overall_scrap_rate_5": 0.00,
        "start_monday_5": "",
        "total_weekly_6": 0,
        "total_output_6": 0,
        "overall_scrap_rate_6": 0.00,
        "start_monday_6": "",
        "total_weekly_7": 0,
        "total_output_7": 0,
        "overall_scrap_rate_7": 0.00,
        "start_monday_7": "",
        "total_weekly_8": 0,
        "total_output_8": 0,
        "overall_scrap_rate_8": 0.00,
        "start_monday_8": "",
        "total_all_weeks": 0,
        "total_all_output": 0,
        "all_scrap_rate": 0.00,
    }

    total_all_output = 0
    total_all_weeks = 0
    for week_num in range(9):
        this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)
        start_sunday = this_sunday - timedelta(days=week_num * 7)
        key_monday = "start_monday_" + str(week_num)
        totals[key_monday] = start_sunday + timedelta(days=1)
        end_sunday = start_sunday + timedelta(days=7)
        scrap_qs = ScrapDetail.objects.filter(line=line_id).filter(created__gte=start_sunday, created__lt=end_sunday)
        total_output_qs = ParetoDetail.objects.filter(line=line_id).filter(created__gte=start_sunday,
                                                                           created__lt=end_sunday)

        total_weekly = 0
        key_qty = "qty_" + str(week_num)

        # total scrap per reason, for week, period summary total, row sum up
        for obj in scrap_qs:
            obj_name = obj.scrap.description
            pos = scrap_list.index(obj_name)
            qty = obj.qty
            total_weekly += qty
            total_all_weeks += qty
            report[pos]["total"] += qty
            report[pos][key_qty] += qty

        # assigning total weekly scrap qty to totals
        key_total = "total_weekly_" + str(week_num)
        totals[key_total] = total_weekly

        # counting output per week
        total_output = 0
        for obj in total_output_qs:
            output_obj = obj.output
            total_output += output_obj

        # assigning total weekly output to totals and counting period summary total output
        key_output = "total_output_" + str(week_num)
        totals[key_output] = total_output
        total_all_output += total_output

        # counting scrap rate
        key_scrap = "scrap_rate_" + str(week_num)
        for idx, elem in enumerate(report):
            scrap_qty = elem[key_qty]
            if total_output == 0:
                scrap_rate = 0
            else:
                scrap_rate = round((scrap_qty / total_output) * 100, ndigits=2)
            elem[key_scrap] = scrap_rate

        # counting weekly scrap rate
        key_rate = "overall_scrap_rate_" + str(week_num)
        if total_output == 0:
            overall_scrap_rate = 0
        else:
            overall_scrap_rate = round((total_weekly / total_output) * 100, ndigits=2)
        totals[key_rate] = overall_scrap_rate

    # counting total scrap rate by row
    totals["total_all_output"] = total_all_output
    for elem in report:
        total_by_scrap_type = elem["total"]
        if total_all_weeks == 0:
            total_scrap_rate = 0.00
        else:
            total_scrap_rate = round((total_by_scrap_type / total_all_output) * 100, ndigits=2)
        elem["total_scrap_rate"] = total_scrap_rate

    # counting total scrap rate
    totals["total_all_weeks"] = total_all_weeks
    if total_all_output == 0:
        all_scrap_rate = 0
    else:
        all_scrap_rate = round((total_all_weeks / total_all_output) * 100, ndigits=2)
    totals["all_scrap_rate"] = all_scrap_rate

    return render(
        request,
        template_name="gemba/scrap_rate.html",
        context={
            "report": report,
            "totals": totals,
        },
    )


def downtime_rate_report_by_week(request, line_id):
    # line = Line.objects.get(pk=line_id)
    today = datetime.now(tz=pytz.UTC).replace(hour=21, minute=45, second=0, microsecond=0)

    report = []

    down_list = []
    down_names_qs = DowntimeUser.objects.filter(line=line_id).order_by("gemba")

    down_row_qty = []
    for obj in down_names_qs:
        down_name = obj.downtime.description
        down_list.append(down_name)
        down_row_qty.append(0)

        report.append({
            "down": down_name,
            "qty_0": 0,
            "down_rate_0": 0.00,
            "qty_1": 0,
            "down_rate_1": 0.00,
            "qty_2": 0,
            "down_rate_2": 0.00,
            "qty_3": 0,
            "down_rate_3": 0.00,
            "qty_4": 0,
            "down_rate_4": 0.00,
            "qty_5": 0,
            "down_rate_5": 0.00,
            "qty_6": 0,
            "down_rate_6": 0.00,
            "qty_7": 0,
            "down_rate_7": 0.00,
            "qty_8": 0,
            "down_rate_8": 0.00,
            "total": 0,
            "total_scrap_rate": 0.00,
        })

    totals = {
        "total_weekly_0": 0,
        "total_available_time_0": 0,
        "overall_down_rate_0": 0.00,
        "start_monday_0": "",
        "total_weekly_1": 0,
        "total_available_time_1": 0,
        "overall_down_rate_1": 0.00,
        "start_monday_1": "",
        "total_weekly_2": 0,
        "total_available_time_2": 0,
        "overall_down_rate_2": 0.00,
        "start_monday_2": "",
        "total_weekly_3": 0,
        "total_available_time_3": 0,
        "overall_down_rate_3": 0.00,
        "start_monday_3": "",
        "total_weekly_4": 0,
        "total_available_time_4": 0,
        "overall_down_rate_4": 0.00,
        "start_monday_4": "",
        "total_weekly_5": 0,
        "total_available_time_5": 0,
        "overall_down_rate_5": 0.00,
        "start_monday_5": "",
        "total_weekly_6": 0,
        "total_available_time_6": 0,
        "overall_down_rate_6": 0.00,
        "start_monday_6": "",
        "total_weekly_7": 0,
        "total_available_time_7": 0,
        "overall_down_rate_7": 0.00,
        "start_monday_7": "",
        "total_weekly_8": 0,
        "total_available_time_8": 0,
        "overall_down_rate_8": 0.00,
        "start_monday_8": "",
        "total_all_weeks": 0,
        "total_all_output": 0,
        "all_down_rate": 0.00,
    }
    total_all_output = 0
    total_all_weeks = 0
    for week_num in range(9):
        this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)
        start_sunday = this_sunday - timedelta(days=week_num * 7)
        key_monday = "start_monday_" + str(week_num)
        totals[key_monday] = start_sunday + timedelta(days=1)
        end_sunday = start_sunday + timedelta(days=7)
        down_qs = DowntimeDetail.objects.filter(line=line_id).filter(created__gte=start_sunday, created__lt=end_sunday)

        # counting available time
        paretos_id = set()
        total_available_time = 0
        for obj in down_qs:
            pareto_id = obj.pareto_id
            paretos_id.add(pareto_id)

        for elem_id in paretos_id:
            pareto = Pareto.objects.get(id=elem_id)
            hours = pareto.hours
            total_available_time += int(hours) * 60

        total_weekly = 0
        key_qty = "qty_" + str(week_num)

        # total downtime per reason, for week, period summary total, row sum up
        for obj in down_qs:
            obj_name = obj.downtime.description
            pos = down_list.index(obj_name)
            minutes = obj.minutes
            total_weekly += minutes
            total_all_weeks += minutes
            report[pos]["total"] += minutes
            report[pos][key_qty] += minutes

        # assigning total weekly downtime minutes to totals
        key_total = "total_weekly_" + str(week_num)
        totals[key_total] = total_weekly

        # assigning total weekly output to totals and counting period summary total output
        key_output = "total_available_time_" + str(week_num)
        totals[key_output] = total_available_time
        total_all_output += total_available_time

        # counting downtime rate
        key_scrap = "down_rate_" + str(week_num)
        for idx, elem in enumerate(report):
            down_qty = elem[key_qty]
            if total_available_time == 0:
                down_rate = 0
            else:
                down_rate = round((down_qty / total_available_time) * 100, ndigits=2)
            elem[key_scrap] = down_rate

        # counting weekly downtime rate
        key_rate = "overall_down_rate_" + str(week_num)
        if total_available_time == 0:
            overall_down_rate = 0
        else:
            overall_down_rate = round((total_weekly / total_available_time) * 100, ndigits=2)
        totals[key_rate] = overall_down_rate

    # counting total downtime rate by row
    totals["total_all_output"] = total_all_output
    for elem in report:
        total_by_down_type = elem["total"]
        if total_all_weeks == 0:
            total_down_rate = 0.00
        else:
            total_down_rate = round((total_by_down_type / total_all_output) * 100, ndigits=2)
        elem["total_down_rate"] = total_down_rate

    # counting total downtime rate
    totals["total_all_weeks"] = total_all_weeks
    if total_all_output == 0:
        all_down_rate = 0
    else:
        all_down_rate = round((total_all_weeks / total_all_output) * 100, ndigits=2)
    totals["all_down_rate"] = all_down_rate

    return render(
        request,
        template_name="gemba/downtime_rate.html",
        context={
            "report": report,
            "totals": totals,
        },
    )


def report_choices(request):
    lines_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    return render(
        request,
        template_name="gemba/report_choices.html",
        context={
            "lines_qs": lines_qs,
        },
    )


def scrap_downtime_compare(request):
    line_name = request.GET.get("Lines")
    if line_name is None:
        line_qs = Line.objects.all()
        line_id = line_qs[0]
    else:
        line_qs = Line.objects.filter(name=line_name)
        line_id = line_qs[0]

    date_to_display = request.GET.get("date_to_display")
    if date_to_display == "":
        scrap_qs = ScrapDetail.objects.filter(line=line_id).filter(
            Q(pareto_date=datetime.now(tz=pytz.UTC)))
        down_qs = DowntimeDetail.objects.filter(line=line_id).filter(
            Q(pareto_date=datetime.now(tz=pytz.UTC)))
    else:
        scrap_qs = ScrapDetail.objects.filter(line=line_id).filter(
            Q(pareto_date=date_to_display))
        down_qs = DowntimeDetail.objects.filter(line=line_id).filter(
            Q(pareto_date=date_to_display))

    report = sorted(
        chain(down_qs, scrap_qs),
        key=lambda obj: obj.created)

    if mobile_browser_check(request):
        return render(
            request,
            template_name="gemba/scrap_downtime_compare_mobile.html",
            context={
                "report": report,
                "line_name": line_name,
            },
        )
    else:
        return render(
            request,
            template_name="gemba/scrap_downtime_compare_mobile.html",
            context={
                "report": report,
                "line_name": line_name,
            },
        )


# list of mobile User Agents
mobile_uas = [
    'w3c ', 'acs-', 'alav', 'alca', 'amoi', 'audi', 'avan', 'benq', 'bird', 'blac',
    'blaz', 'brew', 'cell', 'cldc', 'cmd-', 'dang', 'doco', 'eric', 'hipt', 'inno',
    'ipaq', 'java', 'jigs', 'kddi', 'keji', 'leno', 'lg-c', 'lg-d', 'lg-g', 'lge-',
    'maui', 'maxo', 'midp', 'mits', 'mmef', 'mobi', 'mot-', 'moto', 'mwbp', 'nec-',
    'newt', 'noki', 'oper', 'palm', 'pana', 'pant', 'phil', 'play', 'port', 'prox',
    'qwap', 'sage', 'sams', 'sany', 'sch-', 'sec-', 'send', 'seri', 'sgh-', 'shar',
    'sie-', 'siem', 'smal', 'smar', 'sony', 'sph-', 'symb', 't-mo', 'teli', 'tim-',
    'tosh', 'tsm-', 'upg1', 'upsi', 'vk-v', 'voda', 'wap-', 'wapa', 'wapi', 'wapp',
    'wapr', 'webc', 'winw', 'winw', 'xda', 'xda-'
]

mobile_ua_hints = ['SymbianOS', 'Opera Mini', 'iPhone']


def mobile_browser_check(request):
    # returns True for mobile devices

    mobile_browser = False
    ua = request.META['HTTP_USER_AGENT'].lower()[0:4]

    if ua in mobile_uas:
        mobile_browser = True
    else:
        for hint in mobile_ua_hints:
            if request.META['HTTP_USER_AGENT'].find(hint) > 0:
                mobile_browser = True

    return mobile_browser

