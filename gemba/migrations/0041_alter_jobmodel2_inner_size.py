# Generated by Django 3.2.16 on 2023-01-08 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0040_remove_paretodetail_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobmodel2',
            name='inner_size',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
