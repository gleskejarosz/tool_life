import csv

import xlwt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import redirect
from xlwt import XFStyle, Font

from gemba.models import Pareto, AM, PM, NS, ScrapUser, ScrapModel, ScrapDetail, DowntimeUser, DowntimeModel,\
    DowntimeDetail, ParetoDetail
from gemba.views import get_details_to_display, oee_calculation, count_downtimes, count_scraps


@staff_member_required
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

    col = 1
    jobs = []
    total_ops = 0
    jobs_objs = 0
    for elem in pareto.jobs.all():
        elem_job = elem.job.name
        jobs.append(elem_job)
        elem_takt_time = elem.takt_time
        elem_output = elem.output
        elem_good = elem.good
        elem_ops = elem.ops
        total_ops += elem_ops
        jobs_objs += 1
        ws.write(0, col, elem_job)
        ws.write(1, col, elem_takt_time)
        ws.write(2, col, elem_output)
        ws.write(3, col, elem_good)
        col += 1

    ops = round(total_ops/jobs_objs, ndigits=0)
    # H1 Operators
    ws.write(0, 7, ops)

    scrap_qs = ScrapUser.objects.filter(line=line).order_by("gemba")

    vector = 4  # start scrap reasons from row 5

    for idx, scrap_obj in enumerate(scrap_qs):
        scrap_id = scrap_obj.scrap.id
        scrap_item = ScrapModel.objects.get(id=scrap_id)
        scrap_name = scrap_item.description
        ws.write(vector + idx, 0, scrap_name)

        qty = 0
        scraps_exist_qs = ScrapDetail.objects.filter(pareto_id=pk).filter(scrap=scrap_id)
        column = 1
        for elem in scraps_exist_qs:
            job = elem.job.name
            column += jobs.index(job)
            qty += elem.qty
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
                minutes += obj_min
                frequency += 1
            ws.write(idx, 11, minutes)
            ws.write(idx, 12, frequency)

    wb.save(response)
    return response


@staff_member_required
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

        col = line_id
        if col > 0:
            col *= 4

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
        for elem in pareto.jobs.all():
            elem_job = elem.job.name
            jobs.append(elem_job)
            elem_takt_time = elem.takt_time
            takt_times.append(elem_takt_time)
            elem_output = elem.output
            output_values.append(elem_output)

        ws.write(64 + shift_vector, 1 + col, "Product A - Run")
        ws.write(64 + shift_vector, 2 + col, jobs[0])
        ws.write(64 + shift_vector, 3 + col, takt_times[0])
        ws.write(65 + shift_vector, 1 + col, "Total Number of Direct Operators")
        ws.write(66 + shift_vector, 1 + col, "Total Bags made(bags)")
        ws.write(66 + shift_vector, 2 + col, output_values[0])

        downtime_rows = 60
        scrap_rows = 40

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


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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


@staff_member_required
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

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas


@staff_member_required
def export_pareto_to_pdf(request, pk):
    pareto = Pareto.objects.get(pk=pk)

    report_list = oee_calculation(pareto)
    downtimes_list = count_downtimes(pareto)
    scraps_list = count_scraps(pareto)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 100, "Hello word.")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")


from django.http import HttpResponse
from .resources import JobModelResource

@staff_member_required
def export_job_model_csv(request):
    job_model_resource = JobModelResource()
    dataset = job_model_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobs.csv"'
    return response


@staff_member_required
def export_job_model_xls(request):
    job_model_resource = JobModelResource()
    dataset = job_model_resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="jobs.xls"'
    return response


@staff_member_required
def update_database_many_to_many_field(request):
    pareto_qs = Pareto.objects.all()

    for pareto in pareto_qs:
        pareto_id = pareto.id
        pareto_details_qs = ParetoDetail.objects.filter(pareto_id=pareto_id)
        scrap_details_qs = ScrapDetail.objects.filter(pareto_id=pareto_id)
        downtime_details_qs = DowntimeDetail.objects.filter(pareto_id=pareto_id)
        for pareto_detail in pareto_details_qs:
            if pareto_detail not in pareto.jobs.all():
                pareto.jobs.add(pareto_detail)
        for scrap in scrap_details_qs:
            if scrap not in pareto.scrap.all():
                pareto.scrap.add(scrap)
        for downtime in downtime_details_qs:
            if downtime not in pareto.downtimes.all():
                pareto.downtimes.add(downtime)

    return redirect("gemba_app:index")

