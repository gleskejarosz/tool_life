from datetime import datetime, timedelta

import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from gemba.filters import MonthlyResultFilter
from gemba.models import MonthlyResults, Pareto, Line, PRODUCTIVE, AM, PM, NS, ParetoDetail, DowntimeUser, ScrapUser, \
    DowntimeDetail, ScrapDetail


@staff_member_required
def dashboard(request):
    today = datetime.now(tz=pytz.UTC)
    yesterday = today - timedelta(days=1)
    year = today.strftime('%Y')
    month = today.strftime('%B')

    # monthly report of average oee elements
    monthly_records_qs = MonthlyResults.objects.filter(year=year).order_by("-month", "line")
    items_filter = MonthlyResultFilter(request.GET, queryset=monthly_records_qs)

    # the best oee result from the day before
    paretos = Pareto.objects.filter(pareto_date=yesterday).order_by("-oee")[:5]

    produced = ParetoDetail.objects.all().order_by("created")[:5]
    downtimes_qs = DowntimeDetail.objects.all().order_by("created")[:5]
    scrap_qs = ScrapDetail.objects.all().order_by("created")[:5]

    return render(request,
                  template_name='dashboard.html',
                  context={
                      "filter": items_filter,
                      "produced": produced,
                      "downtimes": downtimes_qs,
                      "scraps": scrap_qs,
                      "year": year,
                      "paretos": paretos,
                      "yesterday": yesterday,
                  },
                  )


@staff_member_required
def report_choices_3(request):
    lines_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    shift = [AM, PM, NS]
    week_list = []
    today = datetime.now(tz=pytz.UTC)

    for w in range(10):
        previous_monday = (today - timedelta(days=today.weekday()) - timedelta(days=w * 7)).strftime("%d-%m-%Y")
        week_list.append(previous_monday)

    return render(
        request,
        template_name="gemba/report_choices_3.html",
        context={
            "lines_qs": lines_qs,
            "shift_list": shift,
            "week_list": week_list,
        },
    )


@staff_member_required
def weekly_report_by_line(request):
    line_name = request.GET.get("Line")
    if line_name is None:
        line_qs = Line.objects.all()
        line_id = line_qs[0]
    else:
        line_qs = Line.objects.filter(name=line_name)
        line_id = line_qs[0]

    monday_str = request.GET.get("Week") + " 21:45:00"
    shift = request.GET.get("Shift")

    monday_object = datetime.strptime(monday_str, '%d-%m-%Y %H:%M:%S')

    this_sunday = monday_object - timedelta(days=1)
    end_sunday = this_sunday + timedelta(days=7)
    pareto_detail_qs = ParetoDetail.objects.filter(created__gte=this_sunday,
                                                   created__lt=end_sunday).filter(line=line_id).order_by("id")

    pareto_qs = set()
    for pareto_detail_obj in pareto_detail_qs:
        pareto_id = pareto_detail_obj.pareto_id
        pareto_obj = Pareto.objects.get(id=pareto_id)
        pareto_qs.add(pareto_obj)

    pareto_shift_qs = []
    for pareto_obj in pareto_qs:
        shift_obj = pareto_obj.shift
        if shift == shift_obj:
            pareto_shift_qs.append(pareto_obj)

    report = []
    report.append({
        "col0": "Date",
        "col1": "",
        "col2": "",
        "col3": "",
        "col4": "",
        "col5": "",
        "col6": "",
        "col7": "",
    })

    if shift == NS:
        display_date = this_sunday
    else:
        display_date = this_sunday + timedelta(days=1)

    pareto_date = this_sunday + timedelta(days=1)

    for num in range(7):
        day = num + 1
        col = "col" + str(day)
        report[0][col] = display_date.date().strftime("%d-%m-%Y")
        display_date += timedelta(days=1)

    for num in range(5):
        report.append({
            "col0": "",
            "col1": 0,
            "col2": 0,
            "col3": 0,
            "col4": 0,
            "col5": 0,
            "col6": 0,
            "col7": 0,
        })

    report[1]["col0"] = "Available time"
    report[2]["col0"] = "Availability"
    report[3]["col0"] = "Performance"
    report[4]["col0"] = "Quality"
    report[5]["col0"] = "OEE"

    for obj in pareto_shift_qs:
        idx = obj.pareto_date.weekday() + 1
        if shift == NS:
            if idx == 7:
                idx -= 6
            else:
                idx += 1
        col = "col" + str(idx)
        available_time = int(obj.hours) * 60
        report[1][col] = available_time
        availability = obj.availability
        report[2][col] = str(availability) + "%"
        performance = obj.performance
        report[3][col] = str(performance) + "%"
        quality = obj.quality
        report[4][col] = str(quality) + "%"
        oee = obj.oee
        report[5][col] = str(oee) + "%"

    indexes = [0, 0, 0, 0, 0, 0, 0, 0]
    max_index = 0
    for obj in pareto_shift_qs:
        for pos, pareto_detail in enumerate(obj.jobs.all()):
            idx = obj.pareto_date.weekday() + 1
            if shift == NS:
                if idx == 7:
                    idx -= 6
                else:
                    idx += 1
            indexes[idx] += 1
            col = "col" + str(idx)
            index = max(indexes)
            if max_index < index:
                for n in range(5):
                    report.append({
                        "col0": "",
                        "col1": 0,
                        "col2": 0,
                        "col3": 0,
                        "col4": 0,
                        "col5": 0,
                        "col6": 0,
                        "col7": 0,
                    })
            max_index = index
            job = pareto_detail.job
            report[6 + pos * 5]["col0"] = "Job"
            report[6 + pos * 5][col] = job
            output = pareto_detail.output
            report[7 + pos * 5]["col0"] = "Output"
            report[7 + pos * 5][col] = output
            good = pareto_detail.good
            report[8 + pos * 5]["col0"] = "Good"
            report[8 + pos * 5][col] = good
            scrap = pareto_detail.scrap
            report[9 + pos * 5]["col0"] = "Scrap"
            report[9 + pos * 5][col] = scrap
            rework = pareto_detail.rework
            report[10 + pos * 5]["col0"] = "Rework"
            report[10 + pos * 5][col] = rework

    downtimes_qs = DowntimeUser.objects.filter(line=line_id, order__gte=0).order_by("order")
    downtimes_list = []
    downtimes_sum = []

    for downtime_elem in downtimes_qs:
        downtime = downtime_elem.downtime.description
        report.append({
            "col0": downtime_elem.downtime,
            "col1": 0,
            "col2": 0,
            "col3": 0,
            "col4": 0,
            "col5": 0,
            "col6": 0,
            "col7": 0,
        })
        downtimes_list.append(downtime)
        downtimes_sum.append(0)

    row = 5 + 5 * max_index + 1
    for obj in pareto_shift_qs:
        idx = obj.pareto_date.weekday() + 1
        if shift == NS:
            if idx == 7:
                idx -= 6
            else:
                idx += 1
        col = "col" + str(idx)
        for down_detail in obj.downtimes.all():
            down_desc = down_detail.downtime.description
            minutes = down_detail.minutes
            pos = downtimes_list.index(down_desc)
            report[row + pos][col] += minutes
            downtimes_sum[pos] += minutes

    idx = 0
    for down_elem in report[row:]:
        if downtimes_sum[idx] == 0:
            report.remove(down_elem)
        idx += 1

    report_len = len(report)

    scraps_qs = ScrapUser.objects.filter(line=line_id, order__gte=0).order_by("order")
    scraps_list = []
    scraps_sum = []

    for scrap_elem in scraps_qs:
        scrap = scrap_elem.scrap.description
        report.append({
            "col0": scrap_elem.scrap,
            "col1": 0,
            "col2": 0,
            "col3": 0,
            "col4": 0,
            "col5": 0,
            "col6": 0,
            "col7": 0,
        })
        scraps_list.append(scrap)
        scraps_sum.append(0)

    for obj in pareto_shift_qs:
        idx = obj.pareto_date.weekday() + 1
        if shift == NS:
            if idx == 7:
                idx -= 6
            else:
                idx += 1
        col = "col" + str(idx)
        for scrap_detail in obj.scrap.all():
            scrap_desc = scrap_detail.scrap.description
            qty = scrap_detail.qty
            pos2 = scraps_list.index(scrap_desc)
            report[report_len + pos2][col] += qty
            scraps_sum[pos2] += qty

    idx = 0
    for scrap_elem in report[report_len:]:
        if scraps_sum[idx] == 0:
            report.remove(scrap_elem)
        idx += 1

    jobs_idx = "6:" + str(row)
    down_idx = str(row) + ":" + str(report_len)
    down_len = str(report_len - row)
    scrap_idx = str(report_len) + ":"
    return render(
        request,
        template_name="gemba/weekly_report_by_line.html",
        context={
            "report": report,
            "line_name": line_name,
            "shift": shift,
            "jobs_idx": jobs_idx,
            "down_idx": down_idx,
            "down_len": down_len,
            "scrap_idx": scrap_idx,
        },
    )
