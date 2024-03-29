# Generated by Django 3.2.15 on 2022-10-15 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0008_remove_operationmodel_job'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stationmodel',
            name='machine',
        ),
        migrations.AddField(
            model_name='toolmodel',
            name='machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='machines', to='tools.machinemodel'),
        ),
        migrations.AddField(
            model_name='toolmodel',
            name='station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stations1', to='tools.stationmodel'),
        ),
    ]
