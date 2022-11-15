from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from gemba.forms import ParetoDetailForm, DowntimeMinutes, ScrapQuantity
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
    form = DowntimeMinutes(request.POST or None)
    if form.is_valid():
        minutes = form.cleaned_data["minutes"]
        user = request.user
        downtime_elem = DowntimeDetail.objects.create(downtime=downtime, minutes=minutes, user=user)

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
    job = ParetoDetail.objects.filter(user=request.user, completed=False).order_by("-id")[0]
    job_id = JobModel.objects.get(name=job)
    form = ScrapQuantity(request.POST or None)
    if form.is_valid():
        qty = form.cleaned_data["qty"]
        user = request.user
        scrap_elem = ScrapDetail.objects.create(scrap=scrap, qty=qty, user=user, job=job_id)

        pareto_qs = Pareto.objects.filter(user=request.user, completed=False)
        if pareto_qs.exists():
            pareto = pareto_qs[0]
            pareto.scrap.add(scrap_elem)
            return redirect("gemba_app:pareto-summary")

        else:
            pareto = Pareto.objects.create(user=request.user, pareto_date=datetime.today())
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
    if form.is_valid():
        job = form.cleaned_data["job"]
        qty = form.cleaned_data["qty"]
        user = request.user
        pareto_item = ParetoDetail.objects.create(job=job, qty=qty, user=user)

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
            print(pareto)
            scraps = ScrapDetail.objects.filter(user=self.request.user, completed=False).values()
            scrap_dict_list = []
            scrap_list = []
            job_list = []

            for scrap_elem in scraps:
                scrap = scrap_elem["scrap_id"]
                job = scrap_elem["job_id"]
                qty = scrap_elem["qty"]
                scrap_dict = {
                    "job": job,
                    "scrap": scrap,
                    "qty": qty,
                }
                if job not in job_list:
                    scrap_dict_list.append(scrap_dict)
                else:
                    if scrap in scrap_list:
                        for elem in scrap_dict_list:
                            if elem["job"] == job and elem["scrap"] == scrap:
                                elem["qty"] += qty
                    else:
                        scrap_dict_list.append(scrap_dict)
                scrap_list.append(scrap)
                job_list.append(job)
            print(scrap_dict_list)
            return render(self.request,
                          template_name='gemba/pareto.html',
                          context={
                              "pareto_list": pareto,
                              "scrap_list": scrap_dict_list,
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
