# Generated by Django 3.2.16 on 2023-01-06 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0036_alter_jobmodel2_group'),
        ('tools', '0043_delete_jobmodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobupdate',
            name='hours',
        ),
        migrations.RemoveField(
            model_name='operationmodel',
            name='hours',
        ),
        migrations.AddField(
            model_name='jobupdate',
            name='minutes',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='operationmodel',
            name='minutes',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='operationmodel',
            name='machine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='machines', to='tools.machinemodel'),
        ),
        migrations.CreateModel(
            name='ToolJobModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_3', to='gemba.jobmodel2')),
                ('tool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tools1', to='tools.toolmodel')),
            ],
            options={
                'verbose_name': 'Tools vs Job',
            },
        ),
    ]