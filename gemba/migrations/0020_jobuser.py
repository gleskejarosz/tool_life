# Generated by Django 3.2.16 on 2022-12-04 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0041_jobmodel_inner_size'),
        ('gemba', '0019_auto_20221204_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(blank=True, null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_group', to='gemba.downtimegroup')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_user', to='tools.jobmodel')),
            ],
            options={
                'verbose_name': 'Job vs Group',
            },
        ),
    ]
