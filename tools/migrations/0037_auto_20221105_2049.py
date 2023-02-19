# Generated by Django 3.2.16 on 2022-11-05 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0036_auto_20221105_2030'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MyDateField',
        ),
        migrations.AddField(
            model_name='jobupdate',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='operationmodel',
            name='finish_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='operationmodel',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
