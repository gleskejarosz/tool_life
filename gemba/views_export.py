import xlwt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from xlwt import XFStyle

from gemba.models import Pareto, AM, PM, NS, JobModel2, ScrapUser, ScrapModel, ScrapDetail, DowntimeUser, \
    DowntimeModel, DowntimeDetail, Line


@login_required
def tableau_export(request, pk):
    pareto = Pareto.objects.get(pk=pk)

    date = pareto.pareto_date
    shift = pareto.shift
    if shift == AM:
        shift = "AM"
    elif shift == PM:
        shift = "PM"
    elif shift == NS:
        shift = "NS"

    user = pareto.user
    hours = pareto.hours
    not_scheduled_to_run = pareto.not_scheduled_to_run
    available_time = int(hours) * 60 - not_scheduled_to_run
    performance = pareto.performance / 100
    quality = pareto.quality / 100
    availability = pareto.availability / 100
    oee = pareto.oee / 100
    ops = pareto.ops
    line = pareto.line_id

    response = HttpResponse(content_type="application/ms-excel")
    filename = f"{date} - {shift} - {user.username}.xls"
    # dest = ('\\').join(source.split('\\')[:1})
    response["Content-Disposition"] = 'attachment; filename= "{}"'.format(filename)

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Report")

    style3 = XFStyle()
    style3.num_format_str = "YYYY-MM-DD"
    # A1 Date
    ws.write(0, 0, date, style3)
    # A2 Line name <- fix it later
    ws.write(1, 0, user.username)
    # A3 Shift
    ws.write(2, 0, shift)
    # A4 Available time
    ws.write(3, 0, available_time)
    # H1 Operators
    ws.write(0, 7, ops)

    style2 = XFStyle()
    style2.num_format_str = "0%"
    # O1 Availability
    ws.write(0, 14, "Availability")
    ws.write(0, 15, availability, style2)
    # O2 Performance
    ws.write(1, 14, "Performance")
    ws.write(1, 15, performance, style2)
    # 03 Quality
    ws.write(2, 14, "Quality")
    ws.write(2, 15, quality, style2)
    # 04 OEE
    ws.write(3, 14, "OEE")
    ws.write(3, 15, oee, style2)

    jobs = []
    col = 1
    for elem in pareto.jobs.all():
        elem_job = elem.job.name
        jobs.append(elem_job)
        elem_job_id = elem.job.id
        # wrong
        job_obj = JobModel2.objects.get(id=elem_job_id)
        target = job_obj.target
        elem_takt_time = round(60 / target, ndigits=4)
        elem_output = elem.output
        elem_good = elem.good
        ws.write(0, col, elem_job)
        ws.write(1, col, elem_takt_time)
        ws.write(2, col, elem_output)
        ws.write(3, col, elem_good)
        col += 1

    scrap_qs = ScrapUser.objects.filter(line=line).order_by("gemba")

    vector = 4  # start scrap reasons from row 5

    for idx, scrap_obj in enumerate(scrap_qs):
        scrap_id = scrap_obj.scrap.id
        scrap_item = ScrapModel.objects.get(id=scrap_id)
        scrap_name = scrap_item.description
        ws.write(vector + idx, 0, scrap_name)

        scraps_exist_qs = ScrapDetail.objects.filter(pareto_id=pk).filter(scrap=scrap_id)
        for elem in scraps_exist_qs:
            job = elem.job.name
            column = jobs.index(job) + 1
            qty = elem.qty
            ws.write(vector + idx, column, qty)

    down_qs = DowntimeUser.objects.filter(line=line).order_by("gemba")

    for idx, down_obj in enumerate(down_qs):
        down_id = down_obj.downtime.id
        down_item = DowntimeModel.objects.get(id=down_id)
        down_code = down_item.code
        down_name = down_item.description
        ws.write(idx, 9, down_code)
        ws.write(idx, 10, down_name)

        down_exist_obj = DowntimeDetail.objects.filter(pareto_id=pk).filter(downtime=down_id)
        minutes = 0
        frequency = 0
        if down_exist_obj.exists():
            for down_obj in down_exist_obj:
                obj_min = down_obj.minutes
                obj_freq = down_obj.frequency
                minutes += obj_min
                frequency += obj_freq
            ws.write(idx, 11, minutes)
            ws.write(idx, 12, frequency)

    wb.save(response)
    return response


@login_required
def gemba_export2(request):
    query = request.GET.get("q")

    pareto_qs = Pareto.objects.filter(
        Q(pareto_date__exact=query)
    )
    response = HttpResponse(content_type="application/ms-excel")
    filename = f"{query} - Gemba Report.xls"

    response["Content-Disposition"] = 'attachment; filename= "{}"'.format(filename)

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Gemba_data")

    for pareto in pareto_qs:
        pareto_id = pareto.id
        shift = pareto.shift
        line = pareto.line
        line_id = pareto.line_id
        line_name = line.name

        # first column for data
        line_obj = Line.objects.get(id=line_id)
        col = line_obj.col_vector

        # from row - depends on the shift
        if shift == AM:
            shift_vector = 0
            ws.write(1, 2 + col, line_name)
        elif shift == PM:
            shift_vector = 159
        else:
            shift_vector = 318

        hours = pareto.hours
        not_scheduled_to_run = pareto.not_scheduled_to_run
        available_time = int(hours) * 60 - not_scheduled_to_run
        performance = pareto.performance / 100
        quality = pareto.quality / 100
        availability = pareto.availability / 100
        oee = pareto.oee / 100

        ws.write(63 + shift_vector, 1 + col, "Total Available Time")
        ws.write(63 + shift_vector, 2 + col, available_time)
        ws.write(156 + shift_vector, 1 + col, "Availability")
        ws.write(156 + shift_vector, 2 + col, availability)
        ws.write(157 + shift_vector, 1 + col, "Performance")
        ws.write(157 + shift_vector, 2 + col, performance)
        ws.write(158 + shift_vector, 1 + col, "Quality")
        ws.write(158 + shift_vector, 2 + col, quality)
        ws.write(159 + shift_vector, 1 + col, "OEE")
        ws.write(159 + shift_vector, 2 + col, oee)

        jobs = []
        takt_times = []
        output_values = []
        good_values = []
        for elem in pareto.jobs.all():
            elem_job = elem.job.name
            jobs.append(elem_job)
            elem_job_id = elem.job.id
            job_obj = JobModel2.objects.get(id=elem_job_id)
            target = job_obj.target
            elem_takt_time = round(60 / target, ndigits=4)
            takt_times.append(elem_takt_time)
            elem_output = elem.output
            output_values.append(elem_output)

        ws.write(64 + shift_vector, 1 + col, "Product A - Run")
        ws.write(64 + shift_vector, 2 + col, jobs[0])
        ws.write(64 + shift_vector, 3 + col, takt_times[0])
        ws.write(65 + shift_vector, 1 + col, "Total Number of Direct Operators")
        ws.write(66 + shift_vector, 1 + col, "Total Bags made(bags)")
        ws.write(66 + shift_vector, 2 + col, output_values[0])

        downtime_rows = line_obj.downtime_rows
        scrap_rows = line_obj.scrap_rows

        offset_a = downtime_rows + 5
        offset_b = scrap_rows + 6
        ws.write(110 + shift_vector, 1 + col, "Product B - Run")
        ws.write(111 + shift_vector, 1 + col, "Total Number of Direct Operators")
        ws.write(112 + shift_vector, 1 + col, "Total Bags made(bags)")

        if len(jobs) > 1:
            ws.write(110 + shift_vector, 2 + col, jobs[1])
            ws.write(110 + shift_vector, 3 + col, takt_times[1])

            ws.write(112 + shift_vector, 2 + col, output_values[1])

        down_qs = DowntimeUser.objects.filter(line=line).order_by("gemba")

        down_vector = 2
        for idx, down_obj in enumerate(down_qs):
            down_id = down_obj.downtime.id
            down_item = DowntimeModel.objects.get(id=down_id)
            down_code = down_item.code
            down_desc = down_item.description
            row = shift_vector + down_vector + idx
            ws.write(row, 0 + col, down_code)
            ws.write(row, 1 + col, down_desc)

            down_exist_obj = DowntimeDetail.objects.filter(pareto_id=pareto_id).filter(downtime=down_id)
            minutes = 0
            frequency = 0
            if down_exist_obj.exists():
                for down_obj in down_exist_obj:
                    obj_min = down_obj.minutes
                    frequency += 1
                    minutes += obj_min
                ws.write(row, 2 + col, minutes)
                ws.write(row, 3 + col, frequency)

        scrap_qs = ScrapUser.objects.filter(line=line).order_by("gemba")

        for idx, scrap_obj in enumerate(scrap_qs):
            scrap_id = scrap_obj.scrap.id
            scrap_item = ScrapModel.objects.get(id=scrap_id)
            scrap_code = scrap_item.code
            scrap_desc = scrap_item.description
            row = shift_vector + down_vector + idx
            ws.write(row + offset_a, 0 + col, scrap_code)
            ws.write(row + offset_a + offset_b, 0 + col, scrap_code)
            ws.write(row + offset_a, 1 + col, scrap_desc)
            ws.write(row + offset_a + offset_b, 1 + col, scrap_desc)

            scraps_exist_qs = ScrapDetail.objects.filter(pareto_id=pareto_id).filter(scrap=scrap_id)
            qty_a = 0
            qty_b = 0
            if scraps_exist_qs.exists():
                for elem in scraps_exist_qs:
                    job = elem.job.name
                    if job in jobs:
                        num = jobs.index(job)
                        if num == 0:
                            # product A
                            qty_a += elem.qty
                        else:
                            # product B
                            qty_b += elem.qty
                ws.write(row + offset_a, 2 + col, qty_a)
                ws.write(row + offset_a + offset_b, 2 + col, qty_b)

    wb.save(response)
    return response


