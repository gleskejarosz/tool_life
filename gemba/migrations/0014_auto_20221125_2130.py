# Generated by Django 3.2.16 on 2022-11-25 21:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gemba', '0013_auto_20221120_2120'),
    ]

    operations = [
        migrations.CreateModel(
            name='HourModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Start hour',
            },
        ),
        migrations.AddField(
            model_name='pareto',
            name='hours',
            field=models.CharField(choices=[('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], default=8, max_length=32),
        ),
        migrations.AddField(
            model_name='pareto',
            name='shift',
            field=models.CharField(choices=[('--', 'No choice'), ('Morning shift', 'Morning shift'), ('Afternoon shift', 'Afternoon shift'), ('Night shift', 'Night shift')], default='--', max_length=32),
        ),
        migrations.CreateModel(
            name='LineHourModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='starts', to='gemba.hourmodel')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Line start hour',
            },
        ),
    ]
