from datetime import datetime, timedelta

import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from gemba.filters import MonthlyResultFilter
from gemba.models import MonthlyResults, Pareto, Line, PRODUCTIVE, AM, PM, NS, ParetoDetail, DowntimeUser, ScrapUser, \
    DowntimeDetail, ScrapDetail, DowntimeModel, ScrapModel
from gemba.views import mobile_browser_check


@staff_member_required
def dashboard(request):
    today = datetime.now(tz=pytz.UTC)
    yesterday = today - timedelta(days=1)
    year = today.strftime('%Y')
    month = today.strftime('%B')

    # monthly report of average oee elements
    monthly_records_qs = MonthlyResults.objects.filter(year=year).order_by("-id", "line")
    items_filter = MonthlyResultFilter(request.GET, queryset=monthly_records_qs)

    # the best oee result from the day before
    paretos = Pareto.objects.filter(pareto_date=yesterday).order_by("-oee")[:5]

    produced = ParetoDetail.objects.all().order_by("-created")[:5]
    downtimes_qs = DowntimeDetail.objects.all().order_by("-created")[:5]
    scrap_qs = ScrapDetail.objects.all().order_by("-created")[:5]

    context = {
        "filter": items_filter,
        "produced": produced,
        "downtimes": downtimes_qs,
        "scraps": scrap_qs,
        "year": year,
        "paretos": paretos,
        "yesterday": yesterday,
    }
    if mobile_browser_check(request):
        return render(
            request,
            template_name="dashboard_mobile.html",
            context=context,
        )
    else:
        return render(
            request,
            template_name='dashboard_mobile.html',
            context=context,
        )


def test_page(request):
    today = datetime.now(tz=pytz.UTC)
    yesterday = today - timedelta(days=1)
    year = today.strftime('%Y')
    month = today.strftime('%B')

    # monthly report of average oee elements
    monthly_records_qs = MonthlyResults.objects.filter(year=year).order_by("-id", "line")
    items_filter = MonthlyResultFilter(request.GET, queryset=monthly_records_qs)

    # the best oee result from the day before
    paretos = Pareto.objects.filter(pareto_date=yesterday).order_by("-oee")[:5]

    produced = ParetoDetail.objects.all().order_by("-created")[:5]
    downtimes_qs = DowntimeDetail.objects.all().order_by("-created")[:5]
    scrap_qs = ScrapDetail.objects.all().order_by("-created")[:5]

    context = {
        "filter": items_filter,
        "produced": produced,
        "downtimes": downtimes_qs,
        "scraps": scrap_qs,
        "year": year,
        "paretos": paretos,
        "yesterday": yesterday,
    }
    return render(
        request,
        template_name='gemba/test_page.html',
        context=context,
    )


@staff_member_required
def report_choices_3(request):
    lines_qs = Line.objects.filter(line_status=PRODUCTIVE).order_by("name")
    shift = [AM, PM, NS]

    return render(
        request,
        template_name="gemba/report_choices_3.html",
        context={
            "lines_qs": lines_qs,
            "shift_list": shift,
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

    day_str = request.GET.get("day") + " 21:45:00"
    shift = request.GET.get("Shift")

    day_object = datetime.strptime(day_str, '%Y-%m-%d %H:%M:%S')

    week_sunday = day_object - timedelta(days=day_object.weekday()) - timedelta(days=1)
    next_sunday = week_sunday + timedelta(days=7)

    this_week_sunday = week_sunday
    pareto_qs = Pareto.objects.filter(pareto_date__gte=week_sunday,
                                      pareto_date__lt=next_sunday).filter(line=line_id).order_by("id")
    pareto_sun_qs = Pareto.objects.filter(pareto_date=week_sunday).exclude(shift=NS)
    pareto_qs.difference(pareto_sun_qs)

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
        display_date = week_sunday
    else:
        display_date = week_sunday + timedelta(days=1)

    for num in range(7):
        day = num + 1
        col = "col" + str(day)
        report[0][col] = display_date.date().strftime("%d-%m-%y")
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
        report[1][col] = str(available_time) + " min"
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
            "this_week_sunday": this_week_sunday,
            "shift": shift,
            "jobs_idx": jobs_idx,
            "down_idx": down_idx,
            "down_len": down_len,
            "scrap_idx": scrap_idx,
        },
    )


@staff_member_required
def previous_weekly_report_by_line(request, line_name, this_week_sunday, shift):
    # line_name = request.GET.get("Line")
    if line_name is None:
        line_qs = Line.objects.all()
        line_id = line_qs[0]
    else:
        line_qs = Line.objects.filter(name=line_name)
        line_id = line_qs[0]

    print(line_name)
    print(this_week_sunday)
    print(shift)

    # day_str = day + " 21:45:00"

    # day_object = datetime.strptime(day_str, '%Y-%m-%d %H:%M:%S')

    # week_sunday = day_object - timedelta(days=day_object.weekday()) - timedelta(days=1)
    week_sunday = this_week_sunday - timedelta(days=7)
    next_sunday = this_week_sunday

    pareto_qs = Pareto.objects.filter(pareto_date__gte=week_sunday,
                                      pareto_date__lt=next_sunday).filter(line=line_id).order_by("id")
    pareto_sun_qs = Pareto.objects.filter(pareto_date=week_sunday).exclude(shift=NS)
    pareto_qs.difference(pareto_sun_qs)

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
        display_date = week_sunday
    else:
        display_date = week_sunday + timedelta(days=1)

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
        template_name="gemba/previous_weekly_report_by_line.html",
        context={
            "report": report,
            "line_name": line_name,
            "shift": shift,
            "this_week_sunday": this_week_sunday,
            "jobs_idx": jobs_idx,
            "down_idx": down_idx,
            "down_len": down_len,
            "scrap_idx": scrap_idx,
        },
    )

@staff_member_required
def lines(request):
    lines_qs = Line.objects.all().order_by("name")
    return render(request, "gemba/lines.html", {"lines_qs": lines_qs})


@staff_member_required
def lines_2(request):
    lines2_qs = Line.objects.all().order_by("name")
    return render(request, "gemba/lines2.html", {"lines2_qs": lines2_qs})


@staff_member_required
def scrap_rate_report_by_week(request, line_id):
    # today = datetime.now(tz=pytz.UTC).replace(hour=21, minute=45, second=0, microsecond=0)
    report = []

    scrap_list = []
    scrap_names_qs = ScrapUser.objects.filter(line=line_id, order__gt=0).order_by("order")
    scrap_row_qty = []
    for obj in scrap_names_qs:
        scrap_name = obj.scrap.description
        scrap_id = obj.scrap.id
        scrap_list.append(scrap_name)
        scrap_row_qty.append(0)

        report.append({
            "scrap": scrap_name,
            "scrap_id": scrap_id,
            "week_0": 8,
            "qty_0": 0,
            "scrap_rate_0": 0.00,
            "week_1": 7,
            "qty_1": 0,
            "scrap_rate_1": 0.00,
            "week_2": 6,
            "qty_2": 0,
            "scrap_rate_2": 0.00,
            "week_3": 5,
            "qty_3": 0,
            "scrap_rate_3": 0.00,
            "week_4": 4,
            "qty_4": 0,
            "scrap_rate_4": 0.00,
            "week_5": 3,
            "qty_5": 0,
            "scrap_rate_5": 0.00,
            "week_6": 2,
            "qty_6": 0,
            "scrap_rate_6": 0.00,
            "week_7": 1,
            "qty_7": 0,
            "scrap_rate_7": 0.00,
            "week_8": 0,
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
    range_list = [a for a in range(9)]
    reversed_range_list = reversed(range_list)
    for week_num, idx in enumerate(reversed_range_list):
        today = datetime.now(tz=pytz.UTC)
        this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)
        start_sunday = this_sunday - timedelta(days=idx * 7)
        key_monday = "start_monday_" + str(week_num)
        totals[key_monday] = start_sunday + timedelta(days=1)
        end_sunday = start_sunday + timedelta(days=7)

        scrap_qs = ScrapDetail.objects.filter(line=line_id).filter(pareto_date__gte=start_sunday,
                                                                   pareto_date__lt=end_sunday)
        scrap_sun_qs = ScrapDetail.objects.filter(line=line_id).filter(pareto_date=start_sunday)
        for scrap_elem in scrap_sun_qs:
            pareto_id = scrap_elem.pareto_id
            pareto = Pareto.objects.get(id=pareto_id)
            shift = pareto.shift
            if shift == NS:
                scrap_sun_qs.difference(scrap_elem)

        scrap_qs.difference(scrap_sun_qs)

        total_output_qs = ParetoDetail.objects.filter(line=line_id).filter(pareto_date__gte=start_sunday,
                                                                           pareto_date__lt=end_sunday)
        total_output_sun_qs = ParetoDetail.objects.filter(line=line_id).filter(pareto_date=start_sunday)
        for pareto_detail_elem in total_output_sun_qs:
            pareto_id = pareto_detail_elem.pareto_id
            pareto = Pareto.objects.get(id=pareto_id)
            shift = pareto.shift
            if shift == NS:
                total_output_sun_qs.difference(pareto_detail_elem)

        total_output_qs.difference(total_output_sun_qs)

        # this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)
        # start_sunday = this_sunday - timedelta(days=idx * 7)
        # key_monday = "start_monday_" + str(week_num)
        # totals[key_monday] = start_sunday + timedelta(days=1)
        # end_sunday = start_sunday + timedelta(days=7)
        # scrap_qs = ScrapDetail.objects.filter(line=line_id).filter(created__gte=start_sunday, created__lt=end_sunday)
        # total_output_qs = ParetoDetail.objects.filter(line=line_id).filter(created__gte=start_sunday,
        #                                                                    created__lt=end_sunday)
        total_weekly = 0
        key_qty = "qty_" + str(week_num)

        # total scrap per reason, for week, period summary total, row sum up
        for obj in scrap_qs:
            obj_name = obj.scrap.description
            if obj_name in scrap_list:
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

    new_report = []
    for elem in report:
        if elem["total"] != 0:
            new_report.append(elem)

    return render(
        request,
        template_name="gemba/scrap_rate.html",
        context={
            "report": new_report,
            "totals": totals,
            "line_id": line_id,
        },
    )


@staff_member_required
def downtime_rate_report_by_week(request, line_id):
    # today = datetime.now(tz=pytz.UTC).replace(hour=21, minute=45, second=0, microsecond=0)
    report = []

    down_list = []
    down_names_qs = DowntimeUser.objects.filter(line=line_id, order__gt=0).order_by("order")

    down_row_qty = []
    for obj in down_names_qs:
        down_name = obj.downtime.description
        down_id = obj.downtime.id
        down_list.append(down_name)
        down_row_qty.append(0)

        report.append({
            "down": down_name,
            "down_id": down_id,
            "week_0": 8,
            "qty_0": 0,
            "down_rate_0": 0.00,
            "week_1": 7,
            "qty_1": 0,
            "down_rate_1": 0.00,
            "week_2": 6,
            "qty_2": 0,
            "down_rate_2": 0.00,
            "week_3": 5,
            "qty_3": 0,
            "down_rate_3": 0.00,
            "week_4": 4,
            "qty_4": 0,
            "down_rate_4": 0.00,
            "week_5": 3,
            "qty_5": 0,
            "down_rate_5": 0.00,
            "week_6": 2,
            "qty_6": 0,
            "down_rate_6": 0.00,
            "week_7": 1,
            "qty_7": 0,
            "down_rate_7": 0.00,
            "week_8": 0,
            "qty_8": 0,
            "down_rate_8": 0.00,
            "total": 0,
            "total_down_rate": 0.00,
        })

    totals = {
        "total_weekly_0": 0,
        "total_available_time_0": 0,
        "total_uptime_0": 0,
        "overall_down_rate_0": 0.00,
        "uptime_rate_0": 0.00,
        "start_monday_0": "",
        "total_weekly_1": 0,
        "total_available_time_1": 0,
        "total_uptime_1": 0,
        "overall_down_rate_1": 0.00,
        "uptime_rate_1": 0.00,
        "start_monday_1": "",
        "total_weekly_2": 0,
        "total_available_time_2": 0,
        "total_uptime_2": 0,
        "overall_down_rate_2": 0.00,
        "uptime_rate_2": 0.00,
        "start_monday_2": "",
        "total_weekly_3": 0,
        "total_available_time_3": 0,
        "total_uptime_3": 0,
        "overall_down_rate_3": 0.00,
        "uptime_rate_3": 0.00,
        "start_monday_3": "",
        "total_weekly_4": 0,
        "total_available_time_4": 0,
        "total_uptime_4": 0,
        "overall_down_rate_4": 0.00,
        "uptime_rate_4": 0.00,
        "start_monday_4": "",
        "total_weekly_5": 0,
        "total_available_time_5": 0,
        "total_uptime_5": 0,
        "overall_down_rate_5": 0.00,
        "uptime_rate_5": 0.00,
        "start_monday_5": "",
        "total_weekly_6": 0,
        "total_available_time_6": 0,
        "total_uptime_6": 0,
        "overall_down_rate_6": 0.00,
        "uptime_rate_6": 0.00,
        "start_monday_6": "",
        "total_weekly_7": 0,
        "total_available_time_7": 0,
        "total_uptime_7": 0,
        "overall_down_rate_7": 0.00,
        "uptime_rate_7": 0.00,
        "start_monday_7": "",
        "total_weekly_8": 0,
        "total_available_time_8": 0,
        "total_uptime_8": 0,
        "overall_down_rate_8": 0.00,
        "uptime_rate_8": 0.00,
        "start_monday_8": "",
        "total_all_weeks": 0,
        "total_all_output": 0,
        "total_all_uptime": 0,
        "all_uptime_rate": 0.00,
        "all_down_rate": 0.00,
    }
    total_all_output = 0
    total_all_weeks = 0
    total_all_uptime = 0
    range_list = [a for a in range(9)]
    reversed_range_list = reversed(range_list)
    for week_num, idx in enumerate(reversed_range_list):
        today = datetime.now(tz=pytz.UTC)
        this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)
        start_sunday = this_sunday - timedelta(days=idx * 7)
        key_monday = "start_monday_" + str(week_num)
        totals[key_monday] = start_sunday + timedelta(days=1)
        end_sunday = start_sunday + timedelta(days=7)

        down_qs = DowntimeDetail.objects.filter(line=line_id).filter(pareto_date__gte=start_sunday,
                                                                     pareto_date__lt=end_sunday)
        down_sun_qs = DowntimeDetail.objects.filter(line=line_id).filter(pareto_date=start_sunday)
        for down_elem in down_sun_qs:
            pareto_id = down_elem.pareto_id
            pareto = Pareto.objects.get(id=pareto_id)
            shift = pareto.shift
            if shift == NS:
                down_sun_qs.difference(down_elem)

        down_qs.difference(down_sun_qs)

        # this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)
        # start_sunday = this_sunday - timedelta(days=idx * 7)
        # key_monday = "start_monday_" + str(week_num)
        # totals[key_monday] = start_sunday + timedelta(days=1)
        # end_sunday = start_sunday + timedelta(days=7)
        # down_qs = DowntimeDetail.objects.filter(line=line_id).filter(created__gte=start_sunday, created__lt=end_sunday)

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
            if obj_name in down_list:
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

        # assigning total weekly uptime
        key_output = "total_uptime_" + str(week_num)
        total_uptime = total_available_time - total_weekly
        totals[key_output] = total_uptime
        total_all_uptime += total_uptime

        # counting downtime rate
        key_down = "down_rate_" + str(week_num)
        for idx, elem in enumerate(report):
            down_qty = elem[key_qty]
            if total_available_time == 0:
                down_rate = 0
            else:
                down_rate = round((down_qty / total_available_time) * 100, ndigits=2)
            elem[key_down] = down_rate

        # counting weekly uptime rate
        key_rate = "uptime_rate_" + str(week_num)
        if total_available_time == 0:
            uptime_rate = 0
        else:
            uptime_rate = round((total_uptime / total_available_time) * 100, ndigits=2)
        totals[key_rate] = uptime_rate

        # counting weekly downtime rate
        key_rate = "overall_down_rate_" + str(week_num)
        if total_available_time == 0:
            overall_down_rate = 0
        else:
            overall_down_rate = round((total_weekly / total_available_time) * 100, ndigits=2)
        totals[key_rate] = overall_down_rate

    # counting total downtime rate by row
    totals["total_all_output"] = total_all_output
    totals["total_all_uptime"] = total_all_uptime
    for elem in report:
        total_by_down_type = elem["total"]
        if total_all_weeks == 0:
            total_down_rate = 0.00
        else:
            total_down_rate = round((total_by_down_type / total_all_output) * 100, ndigits=2)
        elem["total_down_rate"] = total_down_rate

    # counting total uptime rate
    if total_all_output == 0:
        all_uptime_rate = 0
    else:
        all_uptime_rate = round((total_all_uptime / total_all_output) * 100, ndigits=2)
    totals["all_uptime_rate"] = all_uptime_rate

    # counting total downtime rate
    totals["total_all_weeks"] = total_all_weeks
    if total_all_output == 0:
        all_down_rate = 0
    else:
        all_down_rate = round((total_all_weeks / total_all_output) * 100, ndigits=2)
    totals["all_down_rate"] = all_down_rate

    new_report = []
    for elem in report:
        if elem["total"] != 0:
            new_report.append(elem)

    return render(
        request,
        template_name="gemba/downtime_rate.html",
        context={
            "report": new_report,
            "totals": totals,
            "line_id": line_id,
        },
    )


def display_downtime_in_a_week(request, line_id, week_no, down_id):
    line = Line.objects.get(id=line_id)
    line_name = line.name
    down = DowntimeModel.objects.get(id=down_id)
    down_code = down.code
    down_description = down.description

    today = datetime.now(tz=pytz.UTC).date()
    this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)

    start_sunday = this_sunday - timedelta(days=int(week_no) * 7)
    end_sunday = start_sunday + timedelta(days=7)
    monday = start_sunday + timedelta(days=1)

    down_qs = DowntimeDetail.objects.filter(pareto_date__gte=start_sunday, pareto_date__lt=end_sunday).filter(
                                            line=line_id).filter(downtime=down_id)

    return render(
        request,
        template_name="gemba/display_downtime_in_a_week.html",
        context={
            "down_qs": down_qs,
            "line_name": line_name,
            "down_code": down_code,
            "down_description": down_description,
            "monday": monday,
        },
    )


def display_scrap_in_a_week(request, line_id, week_no, scrap_id):
    line = Line.objects.get(id=line_id)
    line_name = line.name
    scrap = ScrapModel.objects.get(id=scrap_id)
    scrap_code = scrap.code
    scrap_description = scrap.description

    today = datetime.now(tz=pytz.UTC).date()
    this_sunday = today - timedelta(days=today.weekday()) - timedelta(days=1)

    start_sunday = this_sunday - timedelta(days=int(week_no) * 7)
    end_sunday = start_sunday + timedelta(days=7)
    monday = start_sunday + timedelta(days=1)

    scrap_qs = ScrapDetail.objects.filter(pareto_date__gte=start_sunday, pareto_date__lt=end_sunday).filter(
                                          line=line_id).filter(scrap=scrap_id)

    return render(
        request,
        template_name="gemba/display_scrap_in_a_week.html",
        context={
            "scrap_qs": scrap_qs,
            "line_name": line_name,
            "scrap_code": scrap_code,
            "scrap_description": scrap_description,
            "monday": monday,
        },
    )