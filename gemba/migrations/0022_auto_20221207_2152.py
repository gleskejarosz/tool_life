# Generated by Django 3.2.16 on 2022-12-07 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0021_auto_20221207_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='downtimedetail',
            name='pareto_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paretodetail',
            name='pareto_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scrapdetail',
            name='pareto_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
