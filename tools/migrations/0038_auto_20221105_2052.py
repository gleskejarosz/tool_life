# Generated by Django 3.2.16 on 2022-11-05 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0037_auto_20221105_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobupdate',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='operationmodel',
            name='finish_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='operationmodel',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]