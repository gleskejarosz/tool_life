# Generated by Django 3.2.16 on 2023-01-22 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0065_auto_20230122_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='operationmodel',
            name='machine',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='operationmodel',
            name='station',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]