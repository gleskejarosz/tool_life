# Generated by Django 3.2.16 on 2023-01-22 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0055_timer_completed'),
        ('tools', '0060_alter_toolstationmodel_machine'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationmodel',
            name='machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lines9', to='gemba.line'),
        ),
    ]