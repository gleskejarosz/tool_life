# Generated by Django 3.2.16 on 2022-11-04 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0025_jobmodel_target'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobmodel',
            name='target',
            field=models.IntegerField(default=1615),
        ),
    ]
