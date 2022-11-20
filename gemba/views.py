from datetime import datetime, timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView

from gemba.forms import ParetoDetailForm, DowntimeMinutes, ScrapQuantity, ScrapQuantityJob, DowntimeMinutesJob, \
    ParetoDetailFormJob
from gemba.models import Pareto, ParetoDetail, DowntimeModel, DowntimeDetail, ScrapModel, ScrapDetail
from tools.models import JobModel


def index(request):
    items_list = Pareto.objects.all().order_by("-pareto_date")
    return render(
        request,
        template_name="gemba/pareto.html",
        context={'object_list': items_list},
    )


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


class DowntimeDetailView(DetailView):
    model = DowntimeModel
    template_name = "gemba/downtime_details.html"


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
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
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
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
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
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
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
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
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
        form = ParetoDetailForm(request.POST or None)
        if form.is_valid():
            qty = form.cleaned_data["qty"]
            good = form.cleaned_data["good"]
            user = request.user
            pareto_item = ParetoDetail.objects.create(job=job_id, qty=qty, user=user, good=good)

            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            if pareto_qs.exists():
                pareto = pareto_qs[0]
                pareto.jobs.add(pareto_item)
                return redirect("gemba_app:pareto-summary")

            else:
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
                pareto.jobs.add(pareto_item)
                return redirect("gemba_app:pareto-summary")
    else:
        form = ParetoDetailFormJob(request.POST or None)
        if form.is_valid():
            job = form.cleaned_data["job"]
            qty = form.cleaned_data["qty"]
            good = form.cleaned_data["good"]
            user = request.user
            job_id = JobModel.objects.get(name=job)
            pareto_item = ParetoDetail.objects.create(job=job_id, qty=qty, user=user, good=good)

            pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
            if pareto_qs.exists():
                pareto = pareto_qs[0]
                pareto.jobs.add(pareto_item)
                return redirect("gemba_app:pareto-summary")

            else:
                pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
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

            now = datetime.now(timezone.utc)
            available_time = round((now - pareto.time_stamp).total_seconds() / 60.0)
            availability = round((available_time / 480) * 100)

            scrap_details = ParetoDetail.objects.filter(user=self.request.user, completed=False).values("id", "qty",
                                                                                                        "good", "job")
            total_good = 0
            total_output = 0
            for scrap_cal in scrap_details:
                output = scrap_cal["qty"]
                total_output += output
                good = scrap_cal["good"]
                total_good += good
            total_scrap_cal = total_output - total_good

            quality = round((total_good / total_output) * 100)

            down_qs = DowntimeDetail.objects.filter(user=self.request.user, completed=False).values("id", "minutes")
            total_down = 0
            for down in down_qs:
                quantity = down["minutes"]
                total_down += quantity

            scrap_qs = ScrapDetail.objects.filter(user=self.request.user, completed=False).values("id", "qty")
            total_scrap = 0
            for scrap in scrap_qs:
                qty = scrap["qty"]
                total_scrap += qty

            performance_numerator = 0

            for pareto_detail in scrap_details:
                job_elem = pareto_detail["job"]
                takt_time = 0.03715
                print(takt_time)
                qty_elem = pareto_detail["qty"]
                performance_numerator += (qty_elem * takt_time)
                print(performance_numerator)

            performance = round((performance_numerator / (available_time - total_down)) * 100)
            oee = round(availability * performance * quality / 10000)

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
            return render(self.request,
                          template_name='gemba/pareto.html',
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
