from datetime import datetime, timedelta

import pytz
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from gemba.filters import MonthlyResultFilter
from gemba.models import MonthlyResults, Pareto


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

    return render(request,
                  template_name='dashboard.html',
                  context={
                      "filter": items_filter,
                      "year": year,
                      "paretos": paretos,
                      "yesterday": yesterday,
                  },
                  )
