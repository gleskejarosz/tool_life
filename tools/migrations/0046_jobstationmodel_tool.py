# Generated by Django 3.2.16 on 2023-01-07 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0045_auto_20230106_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobstationmodel',
            name='tool',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tools2', to='tools.toolmodel'),
        ),
    ]
