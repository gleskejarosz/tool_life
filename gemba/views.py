import decimal
from itertools import chain

import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from datetime import datetime, timezone, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.views import View
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView, ListView

from gemba.filters import DowntimeFilter, ScrapFilter, JobFilter
from gemba.forms import DowntimeMinutes, ScrapQuantity, NewPareto, ParetoUpdateForm, \
    NotScheduledToRunUpdateForm, ParetoTotalQtyDetailForm, ParetoDetailUpdateForm, ParetoDetailHCBForm, \
    ParetoDetailHCIForm, ParetoMeterForm, ParetoMeterStartForm, GoodUpdateForm, ScrapUpdateForm
from gemba.models import Pareto, ParetoDetail, DowntimeModel, DowntimeDetail, ScrapModel, ScrapDetail, DowntimeUser, \
    ScrapUser, LineHourModel, JobModel2, SHIFT_CHOICES, TC, LineUser, Line, Timer, JobLine, \
    PRODUCTIVE, HCI, HCB, MC, MonthlyResults, QuarantineHistoryDetail, AM, PM, NS
from tools.views import tools_update


class GembaIndex(TemplateView):
    template_name = 'gemba/index.html'


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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


@staff_member_required
def report_choices_2(request):
    message = ""
    lines_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    return render(
        request,
        template_name="gemba/report_choices_2.html",
        context={
            "lines_qs": lines_qs,
            "message": message,
        },
    )


@staff_member_required
def paretos_view(request):
    line = request.GET.get("line")

    if line is None:
        message = "You must select any line"
        lines_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
        return render(
            request,
            template_name="gemba/report_choices_2.html",
            context={
                "lines_qs": lines_qs,
                "message": message,
            },
        )
    else:
        line_qs = Line.objects.filter(name=line)
        line_id = line_qs[0]

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from == "":
        date_from = datetime.now(tz=pytz.UTC).date() - timedelta(days=30)

    if date_to == "":
        date_to = datetime.now(tz=pytz.UTC).date()

    date_from_ = datetime.strptime(str(date_from), "%Y-%m-%d")
    date_to_ = datetime.strptime(str(date_to), "%Y-%m-%d")

    paretos = Pareto.objects.filter(line=line_id, completed=True).filter(
        Q(pareto_date__gte=date_from) & Q(pareto_date__lte=date_to)).order_by("-pareto_date", "id")

    paginator = Paginator(paretos, 100)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    shift = [AM, PM, NS]

    return render(request,
                  template_name="gemba/paretos_view.html",
                  context={
                      "line": line,
                      "date_from": date_from,
                      "date_to": date_to,
                      "date_from_": date_from_,
                      "date_to_": date_to_,
                      "page_obj": page_obj,
                      "shift_list": shift,
                  })


@staff_member_required
def paretos_view_choices(request, line, date_from, date_to):
    shift = request.GET.get("Shift")
    line_qs = Line.objects.filter(name=line)
    line_id = line_qs[0]

    date_from_ = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_ = datetime.strptime(date_to, "%Y-%m-%d")

    paretos = Pareto.objects.filter(line=line_id, completed=True, shift=shift).filter(
        Q(pareto_date__gte=date_from_) & Q(pareto_date__lte=date_to_)).order_by("-pareto_date", "id")

    return render(request,
                  template_name="gemba/paretos_view_choices.html",
                  context={
                      "paretos": paretos,
                      "line": line,
                      "date_from_": date_from_,
                      "date_to_": date_to_,
                  })


@staff_member_required
def downtime_detail_create(request, pk):
    downtime = get_object_or_404(DowntimeModel, pk=pk)
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    if pareto_qs.exists():
        pareto = pareto_qs[0]
        pareto_id = pareto.id
        pareto_date = pareto.pareto_date
        job = pareto.job_otg
        line = pareto.line

        if job is None:
            return redirect("gemba_app:pareto-summary")

        # make sure pk=7 is "Set up"
        if pk == "7":
            pareto_before_qs = ParetoDetail.objects.filter(user=request.user).order_by("-id")
            if len(pareto_before_qs) > 1:
                pareto_before_obj = pareto_before_qs[1]
                job_before_id = pareto_before_obj.job_id
                job_before_obj = JobModel2.objects.get(id=job_before_id)
                job_before = job_before_obj.name
            else:
                job_before = ""

            downtime_qs = DowntimeDetail.objects.filter(user=request.user, completed=False, downtime_id=pk, job=job)

            if downtime_qs.exists() and job != job_before:
                downtime_id = downtime_qs[0].id
                downtime = DowntimeDetail.objects.get(id=downtime_id)
                old_time = downtime.minutes

                form = DowntimeMinutes(request.POST or None)

                if form.is_valid():
                    minutes = form.cleaned_data["minutes"]
                    new_time = minutes + old_time
                    downtime.minutes = new_time
                    downtime.save()
                    return redirect("gemba_app:pareto-summary")
        else:
            job_before = ""

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
                                                          from_job=job_before, pareto_id=pareto_id,
                                                          pareto_date=pareto_date,
                                                          line=line)
            pareto.downtimes.add(downtime_elem)
            return redirect("gemba_app:pareto-summary")

        return render(
            request,
            template_name="form.html",
            context={"form": form}
        )
    else:
        return redirect("gemba_app:pareto-summary")


@staff_member_required
def scrap_detail_create(request, pk):
    scrap = ScrapModel.objects.get(pk=pk)
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    if pareto_qs.exists():
        pareto = pareto_qs[0]
        pareto_id = pareto.id
        pareto_date = pareto.pareto_date
        job = pareto.job_otg
        line = pareto.line
        line_qs = Line.objects.filter(name=line)
        calc_option = line_qs[0].calculation

        if job is None:
            return redirect("gemba_app:pareto-summary")

        # make sure this is "Set up"
        if pk == "1":
            pareto_before_qs = ParetoDetail.objects.filter(user=request.user).order_by("-id")
            if len(pareto_before_qs) > 1:
                pareto_before_obj = pareto_before_qs[1]
                job_before_id = pareto_before_obj.job_id
                job_before_obj = JobModel2.objects.get(id=job_before_id)
                job_before = job_before_obj.name
            else:
                job_before = ""

            scrap_qs = ScrapDetail.objects.filter(user=request.user, completed=False, scrap=scrap, job=job)

            if scrap_qs.exists() and job != job_before:
                scrap_id = scrap_qs[0].id
                scrap = ScrapDetail.objects.get(id=scrap_id)
                old_qty = scrap.qty

                form = ScrapQuantity(request.POST or None)

                if form.is_valid():
                    qty = form.cleaned_data["qty"]
                    new_qty = qty + old_qty
                    scrap.qty = new_qty
                    scrap.save()
                    return redirect("gemba_app:pareto-summary")
        else:
            job_before = ""

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

            if calc_option != TC:
                pareto_detail = ParetoDetail.objects.get(user=request.user, completed=False, job=job)
                pareto_detail.scrap += qty
                pareto_detail.output += qty
                pareto_detail.save()
            return redirect("gemba_app:pareto-summary")

        return render(
            request,
            template_name="form.html",
            context={"form": form}
        )
    else:
        return redirect("gemba_app:pareto-summary")


@staff_member_required
def pareto_detail_create(request):
    user = request.user
    pareto_qs = Pareto.objects.filter(user=user, completed=False)

    if pareto_qs.exists():
        pareto = pareto_qs[0]
        job = pareto.job_otg
        ops = pareto.ops_otg
        pareto_id = pareto.id

        line = pareto.line
        if job is None:
            return redirect("gemba_app:pareto-summary")

        name_id = pareto.job_otg_id
        job_qs = JobLine.objects.filter(job=name_id)
        job_obj = job_qs[0]
        target = job_obj.target
        factor = job_obj.factor
        takt_time = round(60 / target, ndigits=5)
        pareto_details_qs = ParetoDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)

        total_output = 0
        total_good = 0

        for elem in pareto_details_qs:
            total_output += elem.output
            total_good += elem.good

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
                    pareto_elem = ParetoDetail.objects.get(user=user, completed=False, job=job, pareto_id=pareto_id)
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
                                                              pareto_id=pareto_id, line=line, ops=ops,
                                                              rework=rework_cal,
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

        elif calc_option == MC:
            scrap_qs = ScrapDetail.objects.filter(user=user, completed=False, pareto_id=pareto_id, job=job)

            if pareto_details_qs.exists():
                form = ParetoMeterForm(request.POST or None)

                if form.is_valid():
                    meter = form.cleaned_data["meter"]

                    rework_cal = 0
                    scrap = 0
                    for scrap_elem in scrap_qs:
                        scrap_id = scrap_elem.scrap_id
                        scrap_obj = ScrapModel.objects.get(id=scrap_id)
                        rework = scrap_obj.rework
                        if rework is True:
                            rework_cal += scrap_elem.qty
                        else:
                            scrap += scrap_elem.qty

                    pareto_elem = ParetoDetail.objects.get(user=user, completed=False, job=job, pareto_id=pareto_id)
                    start_meter = pareto_elem.start_meter
                    output = (meter - start_meter) * factor
                    new_output = output - total_output
                    good = output - scrap
                    pareto_elem.output = output
                    pareto_elem.good = good
                    pareto_elem.scrap = scrap
                    pareto_elem.rework = rework_cal
                    pareto_elem.save()

                    # tools update
                    modified = pareto_elem.modified
                    tools_update(job=job, output=new_output, target=target, modified=modified)

                    return redirect("gemba_app:pareto-summary")

                pareto_elem = ParetoDetail.objects.get(user=user, completed=False, job=job, pareto_id=pareto_id)
                start_meter = pareto_elem.start_meter
                prev_meter = total_output + start_meter

                return render(
                    request,
                    template_name="gemba/form_meter.html",
                    context={
                        "form": form,
                        "prev_meter": prev_meter,
                    })
            else:
                form = ParetoMeterStartForm(request.POST or None)

                if form.is_valid():
                    meter = form.cleaned_data["meter"]
                    start_meter = form.cleaned_data["start_meter"]

                    output = (meter - start_meter) * factor

                    new_output = output - total_output

                    rework_cal = 0
                    scrap = 0
                    for scrap_elem in scrap_qs:
                        scrap_id = scrap_elem.scrap_id
                        scrap_obj = ScrapModel.objects.get(id=scrap_id)
                        rework = scrap_obj.rework
                        if rework is True:
                            rework_cal += scrap_elem.qty
                        else:
                            scrap += scrap_elem.qty

                    good = output - scrap

                    pareto_elem = ParetoDetail.objects.create(job=job, output=output, user=user, good=good,
                                                              pareto_id=pareto_id, line=line, ops=ops,
                                                              rework=rework_cal,
                                                              start_meter=start_meter, pareto_date=pareto_date,
                                                              scrap=scrap,
                                                              takt_time=takt_time)
                    pareto.jobs.add(pareto_elem)

                    # tools update
                    modified = pareto_elem.modified
                    tools_update(job=job, output=new_output, target=target, modified=modified)

                    return redirect("gemba_app:pareto-summary")

                return render(
                    request,
                    template_name="form.html",
                    context={
                        "form": form,
                    })
        else:
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
                    pareto_elem = ParetoDetail.objects.get(user=user, completed=False, job=job, pareto_id=pareto_id)
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
        return redirect("gemba_app:pareto-summary")


class ParetoSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user = self.request.user
        pareto_qs = Pareto.objects.filter(user=user, completed=False)
        start_meter = 0
        if pareto_qs.exists():
            pareto = pareto_qs[0]

            line = pareto.line
            line_qs = Line.objects.filter(name=line)
            calc_option = line_qs[0].calculation
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
                    start_meter = scrap_cal.start_meter
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
                              "start_meter": start_meter,
                              "calc_option": calc_option,
                              "TC": TC,
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
            start_meter = 0
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
                              "start_meter": start_meter,
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

        max_available_time = int(hours) * 60 - not_scheduled_to_run

        if available_time > max_available_time:
            available_time = max_available_time
        elif available_time < 0:
            available_time = max_available_time

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


def count_downtimes(pareto):
    downtimes = []
    downtimes_list = []
    founded = 0

    for down_obj in pareto.downtimes.all():
        down_code = down_obj.downtime.code
        down_desc = down_obj.downtime.description
        down_time = down_obj.minutes
        down_id = down_obj.downtime_id
        job = down_obj.job.name
        if down_id not in downtimes:
            downtimes_list.append({
                "down_id": down_id,
                "job": job,
                "code": down_code,
                "description": down_desc,
                "minutes": down_time,
                "frequency": 1,
            })
            downtimes.append(down_id)
        else:
            for down_elem in downtimes_list:
                job_elem = down_elem["job"]
                down_elem_id = down_elem["down_id"]
                if job == job_elem and down_id == down_elem_id:
                    down_elem["minutes"] += down_time
                    down_elem["frequency"] += 1
                    founded += 1
                    break
            if founded == 0:
                downtimes_list.append({
                    "down_id": down_id,
                    "job": job,
                    "code": down_code,
                    "description": down_desc,
                    "minutes": down_time,
                    "frequency": 1,
                })
                downtimes.append(down_id)
            founded = 0
    sorted_downtimes_list = sorted(downtimes_list, key=lambda d: d['minutes'], reverse=True)
    return sorted_downtimes_list


def count_scraps(pareto):
    scraps = []
    scraps_list = []
    founded = 0
    for scrap_obj in pareto.scrap.all():
        scrap_code = scrap_obj.scrap.code
        scrap_desc = scrap_obj.scrap.description
        scrap_id = scrap_obj.scrap_id
        scrap_qty = scrap_obj.qty
        job = scrap_obj.job.name
        if scrap_id not in scraps:
            scraps_list.append({
                "scrap_id": scrap_id,
                "job": job,
                "code": scrap_code,
                "description": scrap_desc,
                "qty": scrap_qty,
                "frequency": 1,
            })
            scraps.append(scrap_id)
        else:
            for scrap_elem in scraps_list:
                job_elem = scrap_elem["job"]
                scrap_elem_id = scrap_elem["scrap_id"]
                if job == job_elem and scrap_id == scrap_elem_id:
                    scrap_elem["qty"] += scrap_qty
                    scrap_elem["frequency"] += 1
                    founded += 1
                    break
            if founded == 0:
                scraps_list.append({
                    "scrap_id": scrap_id,
                    "job": job,
                    "code": scrap_code,
                    "description": scrap_desc,
                    "qty": scrap_qty,
                    "frequency": 1,
                })
                scraps.append(scrap_id)
            founded = 0
    sorted_scraps_list = sorted(scraps_list, key=lambda d: d['qty'], reverse=True)
    return sorted_scraps_list


@staff_member_required
def pareto_detail_view(request, pk):
    pareto = Pareto.objects.get(pk=pk)

    report_list = oee_calculation(pareto)
    downtimes_list = count_downtimes(pareto)
    scraps_list = count_scraps(pareto)

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


@staff_member_required
def before_close_pareto(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    pareto_id = pareto.id

    line = pareto.line
    line_qs = Line.objects.filter(name=line)
    calc_option = line_qs[0].calculation

    if calc_option == TC:
        pareto_details_qs = ParetoDetail.objects.filter(user=request.user, completed=False,
                                                        pareto_id=pareto_id).order_by("-id")
        if pareto_details_qs.exists():
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


@staff_member_required
def final_confirmation_before_close_pareto(request):
    return render(request,
                  template_name='gemba/pareto_final_qs_before_close.html')


@staff_member_required
def close_pareto(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    line = pareto.line
    pareto_date = pareto.pareto_date

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

    year = pareto_date.strftime('%Y')
    month = pareto_date.strftime('%B')
    daily_output = calculation["output"]
    daily_good = calculation["good"]
    daily_scrap = calculation["scrap"]
    daily_rework = calculation["rework"]
    daily_available_time = calculation["available_time"]

    monthly_record_qs = MonthlyResults.objects.filter(line=line, year=year, month=month).order_by("id")

    if monthly_record_qs.exists():
        monthly_record = monthly_record_qs[0]
        monthly_record.total_output += daily_output
        monthly_record.total_good += daily_good
        monthly_record.total_scrap += daily_scrap
        monthly_record.total_rework += daily_rework
        monthly_record.total_available_time += daily_available_time
        monthly_record.total_availability += decimal.Decimal(availability)
        monthly_record.total_performance += decimal.Decimal(performance)
        monthly_record.total_quality += decimal.Decimal(quality)
        monthly_record.total_oee += decimal.Decimal(oee)
        monthly_record.counter += 1
        monthly_record.save()
    else:
        MonthlyResults.objects.create(year=year, month=month, line=line, total_output=daily_output,
                                      total_good=daily_good, total_scrap=daily_scrap, total_rework=daily_rework,
                                      total_available_time=daily_available_time, total_availability=availability,
                                      total_performance=performance, total_quality=quality, total_oee=oee, counter=1)

    return redirect("gemba_app:index")


# more than one pareto
def get_details_to_display(object_list):
    """
    Organizing data to be displayed in the form of a list of dictionaries, taking into account OEE calculations.
    Used in Daily OEE Report.
    """
    report_list = []
    sum_availability = 0
    sum_performance = 0
    sum_quality = 0
    sum_oee = 0
    counter = 0
    sum_ops = 0

    for pareto in object_list:
        date = pareto.pareto_date
        id = pareto.id
        shift = pareto.shift
        user = pareto.user.username
        line = pareto.line
        target = line.target
        status = pareto.completed
        hours = pareto.hours
        time_stamp = pareto.time_stamp
        job_otg = pareto.job_otg
        ops = pareto.ops_otg
        if ops is None:
            ops = 0
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
            "target": target,
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee,
            "ops": ops,
        })

        sum_availability += decimal.Decimal(availability)
        sum_performance += decimal.Decimal(performance)
        sum_quality += decimal.Decimal(quality)
        sum_oee += decimal.Decimal(oee)
        sum_ops += ops
        counter += 1

    if counter > 0:
        avg_availability = round(sum_availability / counter, ndigits=2)
        avg_performance = round(sum_performance / counter, ndigits=2)
        avg_quality = round(sum_quality / counter, ndigits=2)
        avg_oee = round(sum_oee / counter, ndigits=2)
    else:
        avg_availability = 0
        avg_performance = 0
        avg_quality = 0
        avg_oee = 0

    report_list.append({
        "avg_availability": avg_availability,
        "avg_performance": avg_performance,
        "avg_quality": avg_quality,
        "avg_oee": avg_oee,
        "sum_ops": sum_ops,
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
            ).order_by("line__name", "id")
        else:
            report_list = Pareto.objects.filter(
                Q(pareto_date__exact=query)
            ).order_by("line__name", "id")
        object_list = get_details_to_display(object_list=report_list)

        return object_list


@staff_member_required
def pareto_view(request):
    today_pareto = Pareto.objects.filter(pareto_date=datetime.now(tz=pytz.UTC)).order_by("line__name", "id")

    object_list = get_details_to_display(object_list=today_pareto)

    avg_availability = object_list[-1]["avg_availability"]
    avg_performance = object_list[-1]["avg_performance"]
    avg_quality = object_list[-1]["avg_quality"]
    avg_oee = object_list[-1]["avg_oee"]
    sum_ops = object_list[-1]["sum_ops"]

    report_list = object_list[:-1]

    return render(request,
                  template_name="gemba/pareto_view.html",
                  context={
                      "report_list": report_list,
                      "sum_ops": sum_ops,
                      "avg_availability": avg_availability,
                      "avg_performance": avg_performance,
                      "avg_quality": avg_quality,
                      "avg_oee": avg_oee,
                  },
                  )


START_CHOICES = (
    (SHIFT_CHOICES[1][1], "06:00:00"),
    (SHIFT_CHOICES[2][1], "14:00:00"),
    (SHIFT_CHOICES[3][1], "22:00:00"),
)


@staff_member_required
def pareto_create_new(request):
    user = request.user
    line_user_qs = LineUser.objects.filter(user=user)

    if line_user_qs.exists():
        line = line_user_qs[0].line
    else:
        message = "Your account is not assigned to any line. Please contact your administrator to set this up."
        return render(
            request,
            template_name="gemba/error_message.html",
            context={
                "message": message,
            }
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


@staff_member_required
def scrap_update_view(request, pk):
    scrap_obj = ScrapDetail.objects.get(pk=pk)
    old_qty = scrap_obj.qty
    job = scrap_obj.job
    line = scrap_obj.line
    line_qs = Line.objects.filter(name=line)
    calc_option = line_qs[0].calculation

    form = ScrapUpdateForm(instance=scrap_obj)

    if request.method == "POST":
        form = ScrapUpdateForm(request.POST, instance=scrap_obj)
        if form.is_valid():
            new_qty = form.cleaned_data["qty"]

            scrap_obj.qty = new_qty
            scrap_obj.save()

            if calc_option != TC:
                pareto_detail = ParetoDetail.objects.get(user=request.user, completed=False, job=job)
                qty_diff = old_qty - new_qty
                pareto_detail.scrap -= qty_diff
                pareto_detail.output -= qty_diff
                pareto_detail.save()

            return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


class ScrapDeleteView(DeleteView):
    model = ScrapDetail
    template_name = "gemba/delete_scrap.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")

    def delete(self, request, *args, **kwargs):
        scrap = self.get_object()
        job = scrap.job
        qty = scrap.qty
        line = scrap.line
        line_qs = Line.objects.filter(name=line)
        calc_option = line_qs[0].calculation

        if calc_option != TC:
            pareto_detail = ParetoDetail.objects.get(user=request.user, completed=False, job=job)
            pareto_detail.scrap -= qty
            pareto_detail.output -= qty
            pareto_detail.save()

        return super().delete(request, *args, **kwargs)


class DowntimeDetailView(DetailView):
    model = DowntimeDetail
    template_name = "gemba/downtime_detail_view.html"


class DowntimeUpdateView(UpdateView):
    model = DowntimeDetail
    fields = ("job", "minutes",)
    template_name = "form.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class DowntimeDeleteView(DeleteView):
    model = DowntimeDetail
    template_name = "gemba/delete_downtime.html"
    success_url = reverse_lazy("gemba_app:pareto-summary")


class ParetoDetailView(DetailView):
    model = ParetoDetail
    template_name = "gemba/pareto_detail_view.html"


@staff_member_required
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


@staff_member_required
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


@staff_member_required
def add_scrap_detail(request, pk):
    scrap = get_object_or_404(ScrapDetail, pk=pk)
    old_qty = scrap.qty
    job = scrap.job
    line = scrap.line
    line_qs = Line.objects.filter(name=line)
    calc_option = line_qs[0].calculation

    form = ScrapQuantity(request.POST or None)
    if form.is_valid():
        qty = form.cleaned_data["qty"]
        new_qty = qty + old_qty

        scrap.qty = new_qty
        scrap.save()

        if calc_option != TC:
            pareto_detail = ParetoDetail.objects.get(user=request.user, completed=False, job=job)
            pareto_detail.scrap += qty
            pareto_detail.output += qty
            pareto_detail.save()

        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@staff_member_required
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


@staff_member_required
def timer(request):
    Timer.objects.create(user=request.user)
    return redirect("gemba_app:downtime-user-view")


@staff_member_required
def reset_timer(request):
    timer_qs = Timer.objects.filter(user=request.user, completed=False)
    for timer_obj in timer_qs:
        timer_obj.delete()
    return redirect("gemba_app:downtime-user-view")


@staff_member_required
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
    items_filter = DowntimeFilter(request.GET, queryset=items_list)

    return render(
        request,
        template_name="gemba/downtime_user_view.html",
        context={
            "pareto": pareto,
            "message_status": message_status,
            "filter": items_filter,
            "timer_obj": timer_obj,
            "down_length": down_length,
        },
    )


@staff_member_required
def scrap_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    line = pareto.line
    message_status = ""
    job_otg = pareto.job_otg

    if job_otg is None:
        message_status = "Display"

    items_list = ScrapUser.objects.filter(line=line).filter(order__gt=0).order_by("order")
    items_filter = ScrapFilter(request.GET, queryset=items_list)

    return render(
        request,
        template_name="gemba/scrap_user_view.html",
        context={
            "pareto": pareto,
            "message_status": message_status,
            "filter": items_filter,
        },
    )


@staff_member_required
def job_user_list(request):
    pareto = Pareto.objects.get(user=request.user, completed=False)
    line = pareto.line

    job_qs = JobLine.objects.filter(line=line).order_by("job__name")
    items_filter = JobFilter(request.GET, queryset=job_qs)

    return render(
        request,
        template_name="gemba/job_user_view.html",
        context={
            "filter": items_filter,
        },
    )


@staff_member_required
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
@staff_member_required
def quarantine_view(request):
    quarantine_qs = ScrapDetail.objects.filter(scrap=14).order_by("-modified")

    return render(
        request,
        template_name="gemba/quarantine_view.html",
        context={
            "quarantine_qs": quarantine_qs,
        },
    )


class ParetoNSUpdateView(UpdateView):
    model = Pareto
    template_name = "form.html"
    form_class = NotScheduledToRunUpdateForm
    success_url = reverse_lazy("gemba_app:pareto-summary")


@staff_member_required
def open_pareto(request, pk):
    pareto = Pareto.objects.get(pk=pk)
    user = request.user

    open_pareto_qs = Pareto.objects.filter(user=user, completed=False)

    if len(open_pareto_qs) > 0:
        message = "You can only have one pareto open at a time."
        return render(
            request,
            template_name="gemba/error_message.html",
            context={
                "message": message,
            }, )
    if pareto.completed is False:
        message = "Not completed Pareto cannot be updated."
        return render(
            request,
            template_name="gemba/error_message.html",
            context={
                "message": message,
            }, )

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

    output = 0
    good = 0
    scrap = 0
    rework = 0
    details_item = pareto.jobs.all()
    details_item.update(completed=False)
    details_item.update(user=user)
    for item in details_item:
        output += item.output
        good += item.good
        scrap += item.scrap
        rework += item.rework
        item.save()

    pareto.user = user
    pareto.completed = False
    pareto.save()

    line = pareto.line
    pareto_date = pareto.pareto_date
    available_time = int(pareto.hours) * 60

    availability = pareto.availability
    quality = pareto.quality
    performance = pareto.performance
    oee = pareto.oee
    year = pareto_date.strftime('%Y')
    month = pareto_date.strftime('%B')

    monthly_record_qs = MonthlyResults.objects.filter(line=line, year=year, month=month)

    if monthly_record_qs.exists():
        monthly_record = monthly_record_qs[0]
        monthly_record.total_output -= output
        monthly_record.total_good -= good
        monthly_record.total_scrap -= scrap
        monthly_record.total_rework -= rework
        monthly_record.total_available_time -= available_time
        monthly_record.total_availability -= decimal.Decimal(availability)
        monthly_record.total_performance -= decimal.Decimal(performance)
        monthly_record.total_quality -= decimal.Decimal(quality)
        monthly_record.total_oee -= decimal.Decimal(oee)
        monthly_record.counter -= 1
        monthly_record.save()

    return redirect("gemba_app:pareto-summary")


@staff_member_required
def report_choices(request):
    lines_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    return render(
        request,
        template_name="gemba/report_choices.html",
        context={
            "lines_qs": lines_qs,
        },
    )


@staff_member_required
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

    context = {
        "report": report,
        "line_name": line_name,
        "date": date_to_display,
    }
    if mobile_browser_check(request):
        return render(
            request,
            template_name="gemba/scrap_downtime_compare_mobile.html",
            context=context,
        )
    else:
        return render(
            request,
            template_name="gemba/scrap_downtime_compare.html",
            context=context,
        )


mobile_ua_hints = ['symbianos', 'opera mini', 'android', 'iphone']


def mobile_browser_check(request):
    # returns True for mobile devices

    mobile_browser = False
    ua = request.META['HTTP_USER_AGENT'].lower()

    for hint in mobile_ua_hints:
        if ua.find(hint) > 0:
            mobile_browser = True

    return mobile_browser


@staff_member_required
def lines_3(request):
    lines3_qs = Line.objects.all().order_by("name")
    return render(request, "gemba/lines3.html", {"lines3_qs": lines3_qs})


@staff_member_required
def downtime_scrap_set_up(request, line_id):
    line = Line.objects.get(pk=line_id)
    line_name = line.name
    pareto_detail_qs = ParetoDetail.objects.filter(line=line_id)
    down_qs = DowntimeDetail.objects.filter(line=line_id, downtime=7)
    scrap_qs = ScrapDetail.objects.filter(line=line_id, scrap=1)

    report = sorted(
        chain(pareto_detail_qs, down_qs, scrap_qs),
        key=lambda obj: obj.created, reverse=True)

    context = {
        "report": report,
        "line_name": line_name,
    }
    if mobile_browser_check(request):
        return render(
            request,
            template_name="gemba/downtime_scrap_set_up.html",
            context=context,
        )
    else:
        return render(
            request,
            template_name="gemba/downtime_scrap_set_up.html",
            context=context,
        )


@staff_member_required
def pareto_quarantine_view(request, scrap_id):
    scrap_obj = ScrapDetail.objects.get(pk=scrap_id)
    pareto_id = scrap_obj.pareto_id

    pareto = Pareto.objects.get(pk=pareto_id)
    user = scrap_obj.user

    return render(request,
                  template_name='gemba/pareto_quarantine.html',
                  context={
                      "pareto_list": pareto,
                      "scrap_obj": scrap_obj,
                      "user": user,
                      "scrap_id": scrap_id,
                  },
                  )


@staff_member_required
def create_quarantine_historic_detail(request, scrap_id, pareto_id):
    pareto = Pareto.objects.get(id=pareto_id)
    scrap_obj = ScrapDetail.objects.get(id=scrap_id)

    completed = pareto.completed
    if completed is False:
        message = "This operation cannot be done when pareto is open"
        return render(
            request,
            template_name="gemba/error_message.html",
            context={
                "message": message,
            }
        )

    initial_qty = scrap_obj.qty
    user = request.user
    line = pareto.line
    pareto_date = pareto.pareto_date
    job = scrap_obj.job

    pareto_detail = ParetoDetail.objects.get(pareto_id=pareto_id, line=line, job=job)
    good = pareto_detail.good
    scrap = pareto_detail.scrap

    scrap_qs = ScrapUser.objects.filter(line=line)

    quarantine_qs = QuarantineHistoryDetail.objects.filter(pareto_id=pareto_id, user=user, line=line,
                                                           pareto_date=pareto_date, job=job, good=good, scrap=scrap,
                                                           initial_qty=initial_qty)
    if len(quarantine_qs) == 0:
        quarantine_obj = QuarantineHistoryDetail.objects.create(pareto_id=pareto_id, user=user, line=line,
                                                                pareto_date=pareto_date, job=job, good=good,
                                                                scrap=scrap, initial_qty=initial_qty)
    else:
        quarantine_obj = quarantine_qs[0]

    scrap_details_qs = ScrapDetail.objects.filter(line=line, pareto_id=pareto_id, quarantined=True)
    total_scrap = 0
    for scrap_obj in scrap_details_qs:
        qty = scrap_obj.qty
        total_scrap += qty

    return render(
        request,
        template_name="gemba/pareto_quarantine_resolve.html",
        context={
            "quarantine_obj": quarantine_obj,
            "scrap_qs": scrap_qs,
            "scrap_details_qs": scrap_details_qs,
            "total_scrap": total_scrap,
        }
    )


class GoodUpdateView(UpdateView):
    model = QuarantineHistoryDetail
    template_name = "form.html"
    form_class = GoodUpdateForm
    success_url = reverse_lazy("gemba_app:quarantine-case-summary")


@staff_member_required
def quarantine_summary(request):
    quarantine_case_qs = QuarantineHistoryDetail.objects.filter(user=request.user, completed=False)
    if quarantine_case_qs.exists():
        quarantine_case = quarantine_case_qs[0]
        line = quarantine_case.line
        pareto_id = quarantine_case.pareto_id
        scrap_qs = ScrapUser.objects.filter(line=line)
        scrap_details_qs = ScrapDetail.objects.filter(line=line, pareto_id=pareto_id, quarantined=True)
    else:
        quarantine_case = []
        scrap_qs = []
        scrap_details_qs = []

    total_scrap = 0
    for scrap_obj in scrap_details_qs:
        qty = scrap_obj.qty
        total_scrap += qty

    return render(
        request,
        template_name="gemba/quarantine_summary.html",
        context={
            "quarantine_obj": quarantine_case,
            "scrap_qs": scrap_qs,
            "scrap_details_qs": scrap_details_qs,
            "total_scrap": total_scrap,
        }
    )


@staff_member_required
def create_quarantined_scrap(request, pk):
    scrap = ScrapUser.objects.get(pk=pk)
    line = scrap.line
    scrap_id = scrap.scrap.id
    scrap_obj = ScrapModel.objects.get(id=scrap_id)

    quarantine_case_qs = QuarantineHistoryDetail.objects.filter(user=request.user, completed=False)
    if quarantine_case_qs.exists():
        quarantine_case = quarantine_case_qs[0]
        pareto_id = quarantine_case.pareto_id
        pareto_date = quarantine_case.pareto_date
        job = quarantine_case.job

        form = ScrapQuantity(request.POST or None)

        if form.is_valid():
            qty = form.cleaned_data["qty"]

            scrap_elem = ScrapDetail.objects.create(scrap=scrap_obj, qty=qty, user=request.user, job=job,
                                                    quarantined=True,
                                                    pareto_id=pareto_id, pareto_date=pareto_date, line=line)
            quarantine_case.scraps.add(scrap_elem)
            return redirect("gemba_app:quarantine-case-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )
