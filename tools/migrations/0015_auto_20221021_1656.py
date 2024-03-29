# Generated by Django 3.2.15 on 2022-10-21 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0014_alter_jobupdate_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobstationmodel',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs1', to='tools.jobmodel'),
        ),
        migrations.AlterField(
            model_name='jobstationmodel',
            name='machine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='machines1', to='tools.machinemodel'),
        ),
        migrations.AlterField(
            model_name='jobstationmodel',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stations2', to='tools.stationmodel'),
        ),
        migrations.AlterField(
            model_name='operationmodel',
            name='machine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='machines2', to='tools.machinemodel'),
        ),
        migrations.AlterField(
            model_name='operationmodel',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stations', to='tools.stationmodel'),
        ),
    ]
