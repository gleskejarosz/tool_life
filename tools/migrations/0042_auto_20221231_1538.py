# Generated by Django 3.2.16 on 2022-12-31 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0033_downtimedetail_frequency'),
        ('tools', '0041_jobmodel_inner_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobstationmodel',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs1', to='gemba.jobmodel2'),
        ),
        migrations.AlterField(
            model_name='jobupdate',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs2', to='gemba.jobmodel2'),
        ),
    ]