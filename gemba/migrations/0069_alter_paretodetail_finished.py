# Generated by Django 3.2.16 on 2023-03-02 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gemba', '0068_auto_20230227_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paretodetail',
            name='finished',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
