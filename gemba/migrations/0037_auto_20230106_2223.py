# Generated by Django 3.2.16 on 2023-01-06 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0036_alter_jobmodel2_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timer',
            name='user',
        ),
        migrations.DeleteModel(
            name='Segment',
        ),
        migrations.DeleteModel(
            name='Timer',
        ),
    ]
