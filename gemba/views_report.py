from datetime import datetime, timedelta

import pytz
from django.shortcuts import render

from gemba.models import MonthlyResults, Pareto


def dashboard(request):
    today = datetime.now(tz=pytz.UTC)
    yesterday = today - timedelta(days=1)
    year = today.strftime('%Y')
    month = today.strftime('%B')

    # monthly report of average oee elements
    monthly_records_qs = MonthlyResults.objects.filter(year=year).order_by("-month", "line")

    # the best oee result from the day before
    paretos = Pareto.objects.filter(pareto_date=yesterday).order_by("-oee")[:5]

    return render(request,
                  template_name='dashboard.html',
                  context={
                      "monthly_records": monthly_records_qs,
                      "year": year,
                      "paretos": paretos,
                      "yesterday": yesterday,
                  },
                  )
