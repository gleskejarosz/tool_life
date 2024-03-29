# Generated by Django 3.2.16 on 2023-02-05 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0060_auto_20230204_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyResults',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4)),
                ('month', models.CharField(max_length=16)),
                ('total_output', models.PositiveIntegerField(default=0)),
                ('total_good', models.IntegerField(default=0)),
                ('total_scrap', models.PositiveIntegerField(default=0)),
                ('total_rework', models.PositiveIntegerField(default=0)),
                ('total_available_time', models.PositiveIntegerField(default=0)),
                ('total_availability', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_performance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_quality', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_oee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('counter', models.IntegerField(default=1)),
                ('line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lines20', to='gemba.line')),
            ],
        ),
    ]
