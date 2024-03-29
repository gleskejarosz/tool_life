# Generated by Django 3.2.15 on 2022-10-12 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0004_remove_toolmodel_job_list'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobmodel',
            options={'verbose_name_plural': 'Jobs'},
        ),
        migrations.AlterModelOptions(
            name='machinemodel',
            options={'verbose_name_plural': 'Machines'},
        ),
        migrations.AlterModelOptions(
            name='relationmodel',
            options={'verbose_name_plural': 'Relations'},
        ),
        migrations.AlterModelOptions(
            name='stationmodel',
            options={'verbose_name_plural': 'Stations'},
        ),
        migrations.AlterModelOptions(
            name='toolmodel',
            options={'verbose_name_plural': 'Tools'},
        ),
        migrations.RemoveField(
            model_name='toolmodel',
            name='machine',
        ),
        migrations.RemoveField(
            model_name='toolmodel',
            name='station',
        ),
        migrations.AddField(
            model_name='operationmodel',
            name='machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='machines2', to='tools.machinemodel'),
        ),
        migrations.AddField(
            model_name='operationmodel',
            name='station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stations', to='tools.stationmodel'),
        ),
    ]
