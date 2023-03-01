# Generated by Django 3.2.16 on 2022-12-04 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gemba', '0018_alter_pareto_time_stamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='DowntimeGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=64)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'verbose_name': 'User Group Name',
            },
        ),
        migrations.AddField(
            model_name='linehourmodel',
            name='shift',
            field=models.CharField(choices=[('--', 'No choice'), ('Morning shift', 'Morning shift'), ('Afternoon shift', 'Afternoon shift'), ('Night shift', 'Night shift')], default=django.utils.timezone.now, max_length=32),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pareto',
            name='time_stamp',
            field=models.TimeField(),
        ),
        migrations.CreateModel(
            name='ScrapUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(blank=True, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scrap_group', to='gemba.downtimegroup')),
                ('scrap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scrap_user', to='gemba.scrapmodel')),
            ],
            options={
                'verbose_name': 'Scrap vs Group',
            },
        ),
        migrations.CreateModel(
            name='DowntimeUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(blank=True, null=True)),
                ('downtime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downtime_user', to='gemba.downtimemodel')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downtime_group', to='gemba.downtimegroup')),
            ],
            options={
                'verbose_name': 'Downtime vs Group',
            },
        ),
    ]