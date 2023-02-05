from datetime import datetime

import pytz
from django.contrib.auth.models import User

from django.test import TestCase
from django.urls import reverse

from gemba.models import Line, Pareto, JobModel2, LineUser, AM, LineHourModel, DowntimeModel, DowntimeDetail


class ParetoOperations(TestCase):

    @classmethod
    def setUpTestData(cls):
        line = Line.objects.create(name="Delta")
        JobModel2.objects.create(name="Delta-A")
        user = User.objects.create(username="test_user")
        user_2 = User.objects.create(username="test_user_2")
        user_2.set_password('12345')
        user_2.save()
        user.set_password('12345')
        user.save()
        LineUser.objects.create(user=user, line=line)
        LineHourModel.objects.create(line=line, shift=AM, start="06:00")
        DowntimeModel.objects.create(code="W2", description="Meeting")

    def test_create_pareto(self):
        line = Line.objects.get(id=1)
        user = User.objects.get(username='test_user')
        pareto_date = datetime.now(tz=pytz.UTC).date()
        time_user = LineHourModel.objects.get(id=1)
        time_start = time_user.start
        pareto = Pareto.objects.create(user=user, shift=AM, hours=8, pareto_date=pareto_date,
                                       line=line, ops_otg=1, time_stamp=time_start)

        self.assertEqual(pareto.line.name, "Delta")
        self.assertEqual(pareto.user.username, "test_user")
        self.assertEqual(pareto.shift, AM)
        self.assertEqual(pareto.hours, 8)
        self.assertEqual(pareto.ops_otg, 1)
        self.assertEqual(pareto.pareto_date, datetime.now(tz=pytz.UTC).date())

    def test_when_line_user_exist(self):
        line = Line.objects.get(id=1)
        user = User.objects.get(username='test_user')
        line_user = LineUser.objects.filter(user=user)
        self.assertEqual(line, line_user[0].line)
        response = self.client.get(reverse("gemba_app:pareto-summary"))
        self.assertTrue(response.status_code, 200)

    def test_when_line_user_not_exist(self):
        user_2 = User.objects.get(username="test_user_2")
        line_user = LineUser.objects.filter(user=user_2)
        len_line_user = len(line_user)
        self.assertEqual(len_line_user, 0)
        response = self.client.get(reverse("gemba_app:pareto-summary"))
        self.assertEqual(response.status_code, 302)

    def test_create_downtime_if_not_set_up(self):
        minutes = 10
        downtime = DowntimeModel.objects.get(id=1)
        pareto_date = datetime.now(tz=pytz.UTC).date()
        line = Line.objects.get(id=1)
        user = User.objects.get(username="test_user")
        job = JobModel2.objects.get(id=1)
        job_name = job.name
        time_user = LineHourModel.objects.get(id=1)
        time_start = time_user.start
        Pareto.objects.create(user=user, shift=AM, hours=8, pareto_date=pareto_date, job=job_name,
                              line=line, ops_otg=1, time_stamp=time_start)
        pareto = Pareto.objects.get(id=1)
        pareto_id = pareto.id

        down_detail = DowntimeDetail.objects.create(
            line=line,
            downtime=downtime,
            job=job,
            user=user,
            minutes=minutes,
            pareto_id=pareto_id,
            pareto_date=pareto_date,
        )
        pareto.downtimes.add(down_detail)

        self.assertEqual(down_detail.line, "Delta-A")
        self.assertEqual(down_detail.downtime.code, "W2")
        self.assertEqual(down_detail.downtime.description, "Meeting")
        self.assertEqual(down_detail.job.name, "Delta-A")
        self.assertEqual(down_detail.user.username, "test_user")
        self.assertEqual(down_detail.minutes, 10)
        self.assertEqual(down_detail.pareto_id, 1)
        self.assertEqual(down_detail.pareto_date, datetime.now(tz=pytz.UTC).date())
        self.assertEqual(len(pareto.downtimes), 1)
        self.assertEqual(pareto.downtimes.code, "W2")
        self.assertEqual(pareto.downtimes.description, "Meeting")










