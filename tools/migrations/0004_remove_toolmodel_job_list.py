# Generated by Django 3.2.15 on 2022-10-07 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0003_toolmodel_job_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toolmodel',
            name='job_list',
        ),
    ]
