# Generated by Django 3.2.16 on 2023-01-21 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0054_timer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='timer',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]