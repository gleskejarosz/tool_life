# Generated by Django 3.2.16 on 2023-01-22 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0058_auto_20230122_0827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tooljobmodel',
            name='tool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tools1', to='tools.toolstationmodel'),
        ),
        migrations.DeleteModel(
            name='JobUpdate',
        ),
    ]
