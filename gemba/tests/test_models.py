from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.test import TestCase

from gemba.models import ParetoDetail, JobModel2, Line

# initialize in Terminal: python manage.py test gemba


class ParetoDetailModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        job = JobModel2.objects.create(name="aaa")
        line = Line.objects.create(name="Delta")
        user = User.objects.create(username='test_user')
        user.set_password('12345')
        user.save()
        ParetoDetail.objects.create(job=job, user=user, output=1000, good=900, scrap=100, rework=10, ops=2,
                                    completed=True, created=datetime.now(tz=pytz.UTC),
                                    modified=datetime.now(tz=pytz.UTC), pareto_date=datetime.now(tz=pytz.UTC).
                                    date(), takt_time=0.1, line=line)

    def test_job_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("job").verbose_name
        self.assertEqual(field_label, "job")

    def test_output_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("output").verbose_name
        self.assertEqual(field_label, "output")

    def test_good_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("good").verbose_name
        self.assertEqual(field_label, "good")

    def test_scrap_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("scrap").verbose_name
        self.assertEqual(field_label, "scrap")

    def test_rework_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("rework").verbose_name
        self.assertEqual(field_label, "rework")

    def test_user_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("user").verbose_name
        self.assertEqual(field_label, "user")

    def test_ops_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("ops").verbose_name
        self.assertEqual(field_label, "ops")

    def test_completed_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("completed").verbose_name
        self.assertEqual(field_label, "completed")

    def test_pareto_id_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("pareto_id").verbose_name
        self.assertEqual(field_label, "pareto id")

    def test_created_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("created").verbose_name
        self.assertEqual(field_label, "created")

    def test_modified_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("modified").verbose_name
        self.assertEqual(field_label, "modified")

    def test_pareto_date_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("pareto_date").verbose_name
        self.assertEqual(field_label, "pareto date")

    def test_takt_time_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("takt_time").verbose_name
        self.assertEqual(field_label, "takt time")

    def test_line_label(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        field_label = pareto_detail._meta.get_field("line").verbose_name
        self.assertEqual(field_label, "line")

    def test_object_name_is_item_producer_no_x_quantity(self):
        pareto_detail = ParetoDetail.objects.get(id=1)
        expected_object_name = f'{pareto_detail.job}'
        self.assertEqual(str(pareto_detail), expected_object_name)

