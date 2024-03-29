# Generated by Django 3.2.16 on 2023-01-24 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0056_jobmodel2_line'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='downtimegroup',
            name='line',
        ),
        migrations.RemoveField(
            model_name='downtimegroup',
            name='user',
        ),
        migrations.DeleteModel(
            name='HourModel',
        ),
        migrations.AlterModelOptions(
            name='downtimeuser',
            options={'verbose_name': 'Downtime vs Line'},
        ),
        migrations.AlterModelOptions(
            name='scrapuser',
            options={'verbose_name': 'Scrap vs Line'},
        ),
        migrations.RemoveField(
            model_name='downtimeuser',
            name='group',
        ),
        migrations.RemoveField(
            model_name='jobmodel2',
            name='group',
        ),
        migrations.RemoveField(
            model_name='scrapuser',
            name='group',
        ),
        migrations.AddField(
            model_name='downtimeuser',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lines13', to='gemba.line'),
        ),
        migrations.AddField(
            model_name='line',
            name='calculation',
            field=models.CharField(choices=[('Total output, Total good', 'Total output, Total good'), ('Hourly Good, Scrap items', 'Hourly Good, Scrap items'), ('Meter, Scrap items', 'Meter, Scrap items')], default='Hourly Good, Scrap items', max_length=32),
        ),
        migrations.AddField(
            model_name='line',
            name='line_status',
            field=models.CharField(choices=[('Productive', 'Productive'), ('Not in use', 'Not in use')], default='Productive', max_length=64),
        ),
        migrations.AddField(
            model_name='scrapuser',
            name='line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lines14', to='gemba.line'),
        ),
        migrations.DeleteModel(
            name='DowntimeGroup',
        ),
    ]
