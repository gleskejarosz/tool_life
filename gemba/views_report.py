from datetime import datetime

import pytz
from django.shortcuts import render

from gemba.models import MonthlyResults


def dashboard(request):
    today = datetime.now(tz=pytz.UTC)
    year = today.strftime('%Y')
    month = today.strftime('%B')

    monthly_records_qs = MonthlyResults.objects.filter(year=year).order_by("-month", "line")

    return render(request,
                  template_name='dashboard.html',
                  context={
                      "monthly_records": monthly_records_qs,
                      "year": year,
                  },
                  )