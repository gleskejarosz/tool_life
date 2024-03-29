# Generated by Django 3.2.16 on 2023-01-02 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0033_downtimedetail_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linehourmodel',
            name='shift',
            field=models.CharField(choices=[('--', 'No choice'), ('Morning shift', '1 - Morning shift'), ('Afternoon shift', '2 - Afternoon shift'), ('Night shift', '3 - Night shift')], max_length=32),
        ),
        migrations.AlterField(
            model_name='pareto',
            name='shift',
            field=models.CharField(choices=[('--', 'No choice'), ('Morning shift', '1 - Morning shift'), ('Afternoon shift', '2 - Afternoon shift'), ('Night shift', '3 - Night shift')], default='--', max_length=32),
        ),
    ]
