# Generated by Django 3.2.16 on 2023-01-22 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0057_alter_operationmodel_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolStationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tool', models.CharField(max_length=64)),
                ('tool_status', models.CharField(choices=[('Spare', 'Spare'), ('In use', 'In use'), ('Scrapped', 'Scrapped')], default='Spare', max_length=64)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='machines1', to='tools.machinemodel')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stations1', to='tools.stationmodel')),
            ],
            options={
                'verbose_name': 'Tool',
            },
        ),
        migrations.AlterModelOptions(
            name='toolmodel',
            options={'verbose_name': 'Tool to delete'},
        ),
        migrations.DeleteModel(
            name='JobStationModel',
        ),
    ]
