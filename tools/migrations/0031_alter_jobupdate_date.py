# Generated by Django 3.2.16 on 2022-11-05 20:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0030_auto_20221105_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobupdate',
            name='date',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]