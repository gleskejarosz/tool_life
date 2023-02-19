# Generated by Django 3.2.16 on 2022-11-05 20:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0031_alter_jobupdate_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationmodel',
            name='finish_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='operationmodel',
            name='start_date',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]
