from datetime import timezone, time
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, DeleteView, DetailView

from gemba.filters import ParetoFilter
from gemba.forms import ParetoDetailForm, DowntimeMinutes, ScrapQuantity, ScrapQuantityJob, DowntimeMinutesJob, \
    DowntimeAdd, DowntimeJobAdd, NewPareto
from gemba.models import Pareto, ParetoDetail, DowntimeModel, DowntimeDetail, ScrapModel, ScrapDetail, DowntimeUser, \
    DowntimeGroup, ScrapUser, LineHourModel
from tools.models import JobModel


def index(request):
    items_list = Pareto.objects.all().order_by("-pareto_date")
    return render(
        request,
        template_name="gemba/pareto.html",
        context={'object_list': items_list},
    )


class GembaIndex(TemplateView):
    template_name = 'gemba/index.html'


def daily_pareto(request):
    items_list = DowntimeModel.objects.all().order_by("code")
    scrap_list = ScrapModel.objects.all().order_by("code")

    return render(
        request,
        template_name="gemba/daily_pareto.html",
        context={
            "object_list": items_list,
            "scrap_list": scrap_list,
        },
    )


def pareto_view(request):
    paretos = Pareto.objects.all().order_by("-pareto_date")
    pareto_filter = ParetoFilter(request.GET, queryset=paretos)
    return render(request, "gemba/pareto_view.html", {"filter": pareto_filter})


@login_required
def downtime_detail_create(request, pk):
    downtime = get_object_or_404(DowntimeModel, pk=pk)
    job_qs = ParetoDetail.objects.filter(user=request.user, completed=False).order_by("-id")
    scrap_created_qs = ScrapDetail.objects.filter(user=request.user, completed=False).order_by("-id")
    down_created_qs = DowntimeDetail.objects.filter(user=request.user, completed=False).order_by("-id")

    if job_qs.exists() or scrap_created_qs.exists() or down_created_qs.exists():
        if job_qs.exists():
            job = job_qs[0]
        elif scrap_created_qs.exists():
            scrap_elem_exists = scrap_created_qs[0]
            job = scrap_elem_exists.job
        else:
            down_elem_exists = down_created_qs[0]
            job = down_elem_exists.job

        form = DowntimeMinutes(request.POST or None)
        job = ParetoDetail.objects.filter(user=request.user, completed=False).order_by("-id")[0]
        job_id = JobModel.objects.get(name=job)
        if form.is_valid():
            minutes = form.cleaned_data["minutes"]
            user = request.user
            downtime_elem = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user, job=job_id)

            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            if pareto_qs.exists():
                pareto = pareto_qs[0]
                pareto.downtimes.add(downtime_elem)
                return redirect("gemba_app:pareto-summary")

            else:
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today(),
                                               time_stamp=datetime.today())
                pareto.downtimes.add(downtime_elem)
                return redirect("gemba_app:pareto-summary")
    else:
        form = DowntimeMinutesJob(request.POST or None)
        if form.is_valid():
            minutes = form.cleaned_data["minutes"]
            user = request.user
            job = form.cleaned_data["job"]

            job_id = JobModel.objects.get(name=job)
            downtime_elem = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user, job=job_id)

            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            if pareto_qs.exists():
                pareto = pareto_qs[0]
                pareto.downtimes.add(downtime_elem)
                return redirect("gemba_app:pareto-summary")

            else:
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today(), time_stamp=datetime.today())
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
    job_qs = ParetoDetail.objects.filter(user=request.user, completed=False).order_by("-id")
    scrap_created_qs = ScrapDetail.objects.filter(user=request.user, completed=False).order_by("-id")
    down_created_qs = DowntimeDetail.objects.filter(user=request.user, completed=False).order_by("-id")

    if job_qs.exists() or scrap_created_qs.exists() or down_created_qs.exists():
        if job_qs.exists():
            job = job_qs[0]
        elif scrap_created_qs.exists():
            scrap_elem_exists = scrap_created_qs[0]
            job = scrap_elem_exists.job
        else:
            down_elem_exists = down_created_qs[0]
            job = down_elem_exists.job
        form = ScrapQuantity(request.POST or None)
        if form.is_valid():
            qty = form.cleaned_data["qty"]
            user = request.user

            job_id = JobModel.objects.get(name=job)
            scrap_qs = ScrapDetail.objects.filter(user=request.user, completed=False, scrap=scrap, job=job_id)
            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            if pareto_qs.exists():
                pareto = pareto_qs[0]
                if scrap_qs.exists():
                    scrap_elem = ScrapDetail.objects.get(scrap=scrap, user=user, job=job_id)
                    scrap_elem.qty += qty
                    scrap_elem.save()
                    return redirect("gemba_app:pareto-summary")
                else:
                    scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job_id)
                    pareto.scrap.add(scrap_elem)
                    return redirect("gemba_app:pareto-summary")

            else:
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today(),
                                               time_stamp=datetime.today())
                scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job_id)
                pareto.scrap.add(scrap_elem)
                return redirect("gemba_app:pareto-summary")

    else:
        form = ScrapQuantityJob(request.POST or None)
        if form.is_valid():
            qty = form.cleaned_data["qty"]
            user = request.user
            job = form.cleaned_data["job"]

            job_id = JobModel.objects.get(name=job)
            scrap_qs = ScrapDetail.objects.filter(user=request.user, completed=False, scrap=scrap, job=job_id)
            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            if pareto_qs.exists():
                pareto = pareto_qs[0]
                if scrap_qs.exists():
                    scrap_elem = ScrapDetail.objects.get(scrap=scrap, user=user, job=job_id)
                    scrap_elem.qty += qty
                    scrap_elem.save()
                    return redirect("gemba_app:pareto-summary")
                else:
                    scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job_id)
                    pareto.scrap.add(scrap_elem)
                    return redirect("gemba_app:pareto-summary")

            else:
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today(),
                                               time_stamp=datetime.today())
                scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job_id)
                pareto.scrap.add(scrap_elem)
                return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


@login_required
def pareto_detail_form(request):
    form = ParetoDetailForm(request.POST or None)
    user = request.user
    if form.is_valid():
        job = form.cleaned_data["job"]
        qty = form.cleaned_data["qty"]
        good = form.cleaned_data["good"]
        pareto_item = ParetoDetail.objects.create(job=job, qty=qty, user=user, good=good)

        pareto_qs = Pareto.objects.filter(user=user, completed=False)
        if pareto_qs.exists():
            pareto = pareto_qs[0]
            pareto.jobs.add(pareto_item)
            return redirect("gemba_app:pareto-summary")
        else:
            pareto = Pareto.objects.create(user=user, pareto_date=datetime.today(), time_stamp=datetime.today())
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
            pareto = Pareto.objects.get(user=self.request.user, completed=False)

            pareto_status = ""
            status = pareto.completed
            hours = pareto.hours
            time_stamp = pareto.time_stamp
            available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp)

            scrap_details = ParetoDetail.objects.filter(user=self.request.user, completed=False).values("id", "qty",
                                                                                                        "good", "job")
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

            down_qs = DowntimeDetail.objects.filter(user=self.request.user, completed=False).values("id", "minutes")
            total_down = 0
            if down_qs.exists():
                for down in down_qs:
                    quantity = down["minutes"]
                    total_down += quantity

            availability = availability_cal(available_time=available_time, downtime=total_down)

            scrap_qs = ScrapDetail.objects.filter(user=self.request.user, completed=False).values("id", "qty")
            total_scrap = 0
            if scrap_qs.exists():
                for scrap in scrap_qs:
                    qty = scrap["qty"]
                    total_scrap += qty

            performance_numerator = 0

            if scrap_details.exists():
                for pareto_detail in scrap_details:
                    job_elem = pareto_detail["job"]
                    job_model = JobModel.objects.get(id=job_elem)
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
                          }
                          )


def available_time_cal(status, hours, time_stamp):
    if status is True:
        available_time = int(hours) * 60
    else:
        import time
        now = time.time()
        #now = datetime.strptime(str(time_now), "%H:%M:%S")
        time_start = datetime.strptime(str(time_stamp), "%H:%M:%S")
        available_time = round((now - time_start).total_seconds() / 60.0)
    return available_time


def performance_cal(performance_numerator, available_time, downtime):
    if available_time != 0:
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
        availability = round(((available_time - downtime) / available_time) * 100)
    return availability


def oee_cal(availability, performance, quality):
    oee = round(availability * performance * quality / 10000)
    return oee


def pareto_detail_view(request, pk):
    pareto = get_object_or_404(Pareto, pk=pk)

    status = pareto.completed
    hours = pareto.hours
    time_stamp = pareto.time_stamp
    available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp)

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
def add_to_pareto(request, pk):
    job = get_object_or_404(JobModel, pk=pk)
    pareto_item, created = ParetoDetail.objects.get_or_create(job=job, user=request.user, completed=False)
    pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
    if pareto_qs.exists():
        pareto = pareto_qs[0]
        print(pareto_qs)
        if pareto.jobs.filter(job__pk=job.pk).exists():
            pareto_item.qty += 1
            pareto_item.save()
            return redirect("gemba_app:pareto-summary")
        else:
            pareto.jobs.add(pareto_item)
            return redirect("gemba_app:pareto-summary")

    else:
        pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
        pareto.jobs.add(pareto_item)
        return redirect("gemba_app:pareto-summary")


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


def daily_oee_report(request):
    paretos = Pareto.objects.all().order_by("-pareto_date")

    report_list = []
    for pareto in paretos:
        date = pareto.pareto_date
        id = pareto.id
        shift = pareto.shift
        user = pareto.user
        status = pareto.completed
        hours = pareto.hours
        time_stamp = pareto.time_stamp
        available_time = available_time_cal(status=status, hours=hours, time_stamp=time_stamp)

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
            "user": user,
            "availability": availability,
            "performance": performance,
            "quality": quality,
            "oee": oee,
        })

    return render(request,
                  template_name="gemba/daily_oee_report.html",
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
        time_start = LineHourModel.objects.get(user=user, shift=shift)

        time_stamp = datetime.strptime(str(time_start), "%H:%M:%S")
        print(time_stamp)
        Pareto.objects.create(user=user, completed=False, shift=shift, hours=hours, pareto_date=pareto_date,
                              time_stamp=time_stamp)
        return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


class ScrapDetailView(DetailView):
    model = ScrapDetail
    template_name = "gemba/scrap_detail_view.html"


class ScrapUpdateView(UpdateView):
    model = ScrapDetail
    fields = ("qty", )
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
    fields = ("minutes", )
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
    fields = ("job", "qty", "good", )
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


@login_required
def add_downtime_detail(request):
    job_qs = ParetoDetail.objects.filter(user=request.user, completed=False).order_by("-id")
    scrap_created_qs = ScrapDetail.objects.filter(user=request.user, completed=False).order_by("-id")
    down_created_qs = DowntimeDetail.objects.filter(user=request.user, completed=False).order_by("-id")

    if job_qs.exists() or scrap_created_qs.exists() or down_created_qs.exists():
        if job_qs.exists():
            job = job_qs[0]
        elif scrap_created_qs.exists():
            scrap_elem_exists = scrap_created_qs[0]
            job = scrap_elem_exists.job
        else:
            down_elem_exists = down_created_qs[0]
            job = down_elem_exists.job
        job_id = JobModel.objects.get(name=job)

        form = DowntimeAdd(request.POST or None)
        if form.is_valid():
            downtime = form.cleaned_data["downtime"]
            minutes = form.cleaned_data["minutes"]
            user = request.user
            downtime_detail = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user, job=job_id)

            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            pareto = pareto_qs[0]
            pareto.downtimes.add(downtime_detail)
            return redirect("gemba_app:pareto-summary")
    else:
        form = DowntimeJobAdd(request.POST or None)
        if form.is_valid():
            job = form.cleaned_data["job"]
            downtime = form.cleaned_data["downtime"]
            minutes = form.cleaned_data["minutes"]
            user = request.user
            downtime_detail = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user, job=job)

            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            pareto = pareto_qs[0]
            pareto.downtimes.add(downtime_detail)
            return redirect("gemba_app:pareto-summary")

    return render(
        request,
        template_name="form.html",
        context={"form": form}
    )


def downtime_user_list(request):
    general_list = DowntimeUser.objects.filter(group=1).order_by("order")
    group_qs = DowntimeGroup.objects.filter(user=request.user)
    if group_qs.exists():
        group = group_qs[0]
        items_list = DowntimeUser.objects.filter(group=group).order_by("order")
    else:
        items_list = {}

    return render(
        request,
        template_name="gemba/downtime_user_view.html",
        context={
            "general_list": general_list,
            "items_list": items_list,
        },
    )


def scrap_user_list(request):
    general_list = ScrapUser.objects.filter(group=1).order_by("order")
    group_qs = DowntimeGroup.objects.filter(user=request.user)
    if group_qs.exists():
        group = group_qs[0]
        items_list = ScrapUser.objects.filter(group=group).order_by("order")
    else:
        items_list = {}

    return render(
        request,
        template_name="gemba/scrap_user_view.html",
        context={
            "general_list": general_list,
            "items_list": items_list,
        },
    )