# Generated by Django 3.2.16 on 2022-10-26 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0023_auto_20221023_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='stationmodel',
            name='num',
            field=models.DecimalField(decimal_places=0, default=100, max_digits=3),
        ),
    ]
